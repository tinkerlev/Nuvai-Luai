# File: server.py

import sys
import os
import uuid
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from werkzeug.utils import secure_filename

from src.nuvai.routes.auth_routes import auth_blueprint
from src.nuvai.routes.reset_password_secure import reset_blueprint
from config import get_config, validate_config
from src.nuvai import scan_code
from src.nuvai.utils import get_language
from src.nuvai.utils.logger import get_logger
from src.nuvai.core.db import init_db
from src.nuvai.routes.early_access_routes import early_access_blueprint


logger = get_logger(__name__)

load_dotenv()
validate_config()
config = get_config()

API_PORT = int(os.getenv("API_PORT", 5000))
MAX_FILE_SIZE = config["MAX_UPLOAD_SIZE_MB"] * 1024 * 1024
UPLOAD_FOLDER = os.path.join(os.getcwd(), "backend", "tmp")
ALLOWED_ORIGINS = [origin.strip() for origin in os.getenv("ALLOWED_ORIGINS", "").split(",") if origin.strip()]
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def create_app():
    app = Flask(__name__)
    app.config["MAX_CONTENT_LENGTH"] = MAX_FILE_SIZE

    CORS(app,
         origins=ALLOWED_ORIGINS,
         supports_credentials=True,
         allow_headers=["Content-Type", "Authorization", "X-Requested-With", "X-CSRF-Token", "x-client-nonce"],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])

    app.register_blueprint(reset_blueprint, url_prefix="/auth")
    app.register_blueprint(auth_blueprint, url_prefix="/auth")
    app.register_blueprint(early_access_blueprint)

    @app.route("/")
    def health_check():
        logger.info("Health check endpoint called")
        return jsonify({
            "status": "ok",
            "version": "1.0.0",
            "service": "Luai-scanner"
        }), 200

    @app.before_request
    def log_request_info():
        logger.info(f"Incoming request: {request.method} {request.path} from IP: {request.remote_addr}")

    @app.after_request
    def set_cors_and_security_headers(response):
        origin = request.headers.get("Origin")

        if origin and any(origin.strip().lower() == allowed.lower() for allowed in ALLOWED_ORIGINS):
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With, X-CSRF-Token, x-client-nonce"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"

        response.headers["Content-Security-Policy"] = (
            "default-src 'none'; "
            "script-src 'self'; "
            "style-src 'self'; "
            "img-src 'self'; "
            "connect-src 'self'; "
            "frame-ancestors 'none'; "
            "form-action 'self'; "
            "base-uri 'none'; "
            "object-src 'none'; "
            "upgrade-insecure-requests;"
        )
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Vary"] = "Origin"
        return response

    @app.route("/scan", methods=["POST"])
    def scan_file_or_files():
        logger.info("Received scan request")
        if not request.files:
            logger.warning("No file(s) uploaded")
            return jsonify({"error": "No file(s) uploaded"}), 400

        file_items = list(request.files.items())
        if len(file_items) == 1:
            _, file = file_items[0]
            return scan_single_file(file)

        results = [scan_and_return(file) for _, file in file_items]
        return jsonify(results)

    def scan_single_file(file):
        result = scan_and_return(file)
        return jsonify(result)

    def scan_and_return(file):
        original_filename = secure_filename(file.filename)
        file_id = uuid.uuid4().hex
        filename = f"{file_id}_{original_filename}"
        file_path = os.path.join(UPLOAD_FOLDER, filename)

        try:
            file.save(file_path)
            with open(file_path, "r", encoding="utf-8") as f:
                code = f.read()

            language = get_language(original_filename, code)
            logger.info(f"Scanning file '{original_filename}' (language: {language})")
            findings = scan_code(code, language)

            normalized = [{
                "severity": f.get("severity") or f.get("level", "info").lower(),
                "title": f.get("title") or f.get("type", "Untitled Finding"),
                "description": f.get("description") or f.get("message", "No description provided."),
                "recommendation": f.get("recommendation", "No recommendation available.")
            } for f in findings]

            return {
                "filename": original_filename,
                "language": language,
                "vulnerabilities": normalized
            }

        except UnicodeDecodeError:
            logger.warning(f"Invalid encoding in file '{original_filename}'")
            return {
                "filename": original_filename,
                "error": "Unable to decode file. Please ensure UTF-8 encoding."
            }
        except Exception as e:
            logger.exception(f"Scan failed for file {original_filename}")
            return {
                "filename": original_filename,
                "error": str(e)
            }
        finally:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.debug(f"Temporary file '{file_path}' deleted")

    return app

if __name__ == "__main__":
    init_db()
    app = create_app()
    
    ssl_cert = os.getenv("SSL_CERT_PATH")
    ssl_key = os.getenv("SSL_KEY_PATH")

    
    if not ssl_cert or not ssl_key:
        raise RuntimeError("❌")

    if not os.path.exists(ssl_cert) or not os.path.exists(ssl_key):
        raise FileNotFoundError("❌ SSL certificate or key file not found")

    ssl_context = (ssl_cert, ssl_key)

    logger.info(f"Nuvai API starting on port {API_PORT} with HTTPS")
    app.run(
        host="0.0.0.0",
        port=API_PORT,
        ssl_context=ssl_context,
        debug=True  # ❗ Remove for production
    )
