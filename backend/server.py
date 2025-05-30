# server.py

import sys
import os
from dotenv import load_dotenv
load_dotenv()
import uuid
import logging
from functools import wraps
from flask import Flask, request, jsonify, send_from_directory, abort
from flask_cors import CORS
from werkzeug.utils import secure_filename
from src.nuvai.routes.auth_routes import auth_blueprint
from src.nuvai.routes.reset_password_secure import reset_blueprint
from src.nuvai.routes.early_access_routes import early_access_blueprint
from config import get_config, validate_config
from src.nuvai.utils.ai_analyzer import analyze_scan_results
from src.nuvai import scan_code
from src.nuvai.utils.get_language import get_language
from src.nuvai.utils.logger import get_logger
from src.nuvai.core.db import init_db
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.nuvai.models.user import User
from src.nuvai.routes.auth_oauth import oauth_bp, oauth

logger = get_logger(__name__)

ENVIRONMENT = os.getenv("ENV", "development").lower()
log_level = logging.INFO if ENVIRONMENT == "production" else logging.DEBUG
logging.basicConfig(
    level=log_level,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
)
validate_config()
config = get_config()
API_PORT = int(os.getenv("API_PORT", 5000))
MAX_FILE_SIZE = config["MAX_UPLOAD_SIZE_MB"] * 1024 * 1024
UPLOAD_FOLDER = os.path.join(os.getcwd(), "backend", "tmp")
ALLOWED_ORIGINS = [origin.strip() for origin in os.getenv("ALLOWED_ORIGINS", "").split(",") if origin.strip()]
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
required_dirs = [
    UPLOAD_FOLDER,
    os.path.join("secure_user_logos"),
    os.path.join("static", "user_logos"),
    os.path.join("frontend", "public")
]
for directory in required_dirs:
    if not os.path.isabs(directory):
        directory = os.path.join(os.getcwd(), directory)
    try:
        os.makedirs(directory, exist_ok=True)
    except Exception as e:
        logger.error(f"Failed to create directory {directory}: {str(e)}")
        abort(500)

def rate_limit_check():
    return False

def method_check(allowed_methods):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if request.method not in allowed_methods:
                logger.warning(f"Method not allowed: {request.method} on {request.path}")
                abort(405)
            return f(*args, **kwargs)
        return wrapped
    return decorator

def create_app():
    app = Flask(__name__)
    oauth.init_app(app)
    app.secret_key = os.getenv("FLASK_SECRET_KEY", "super-secret-dev-key")
    app.config["MAX_CONTENT_LENGTH"] = MAX_FILE_SIZE
    logger.debug(f"ALLOWED_ORIGINS = {ALLOWED_ORIGINS}")
    CORS(app,
         origins=ALLOWED_ORIGINS,
         supports_credentials=True,
         allow_headers=["Content-Type", "Authorization", "X-Requested-With", "X-CSRF-Token", "x-client-nonce"],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
    app.register_blueprint(reset_blueprint, url_prefix="/auth")
    app.register_blueprint(auth_blueprint, url_prefix="/auth")
    app.register_blueprint(early_access_blueprint)
    app.register_blueprint(oauth_bp)

    @app.route("/favicon.ico")
    def favicon():
        return send_from_directory(
            os.path.join(app.root_path, "frontend", "public"),
            "favicon.ico",
            mimetype="image/vnd.microsoft.icon"
        )

    @app.route("/user-logo/<filename>", methods=["GET"])
    @jwt_required()
    @method_check(["GET"])
    def get_user_logo(filename):
        if rate_limit_check():
            return jsonify({"error": "Too many requests"}), 429
        user_email = get_jwt_identity()
        filename = secure_filename(filename)
        user = User.get_by_email(user_email)
        if not user or not user.logo_path:
            logger.warning(f"No user or logo for {user_email}")
            return jsonify({"error": "Unauthorized or no logo"}), 403
        if filename not in user.logo_path:
            logger.warning(f"User {user_email} attempted to access another user's logo: {filename}")
            return jsonify({"error": "Unauthorized access"}), 403
        relative_path = os.path.normpath(filename)
        absolute_logo_path = os.path.abspath(os.path.join("static", "user_logos", relative_path))
        static_root = os.path.abspath(os.path.join("static", "user_logos"))
        if not absolute_logo_path.startswith(static_root):
            logger.warning(f"Directory traversal attempt by {user_email}: {absolute_logo_path}")
            return jsonify({"error": "Access denied"}), 403
        if not os.path.isfile(absolute_logo_path):
            logger.warning(f"Logo file '{filename}' not found for user {user_email}")
            return jsonify({"error": "Logo file not found"}), 404
        return send_from_directory(static_root, filename)

    @app.route("/")
    def health_check():
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
        if rate_limit_check():
            return jsonify({"error": "Too many requests"}), 429
        if not request.files:
            return jsonify({"error": "No file(s) uploaded"}), 400
        file_items = list(request.files.items())
        if len(file_items) == 1:
            _, file = file_items[0]
            return jsonify(scan_and_return(file))
        results = [scan_and_return(file) for _, file in file_items]
        return jsonify(results)

    def scan_and_return(file):
        original_filename = secure_filename(file.filename)
        if not original_filename.lower().endswith((".py", ".js", ".html", ".java")):
            logger.warning(f"Disallowed file type: {original_filename}")
            return {"filename": original_filename, "error": "Unsupported file type"}

        file_id = uuid.uuid4().hex
        filename = f"{file_id}_{original_filename}"
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        try:
            file.save(file_path)
            with open(file_path, "r", encoding="utf-8") as f:
                code = f.read()
            language = get_language(original_filename, code)
            findings = scan_code(code, language)
            ai_summary = analyze_scan_results({
                "filename": original_filename,
                "language": language,
                "vulnerabilities": findings
            })
            normalized = [{
                "severity": f.get("severity") or f.get("level", "info").lower(),
                "title": f.get("title") or f.get("type", "Untitled Finding"),
                "description": f.get("description") or f.get("message", "No description provided."),
                "recommendation": f.get("recommendation", "No recommendation available.")
            } for f in findings]
            return {
                "filename": original_filename,
                "language": language,
                "vulnerabilities": normalized,
                "ai_analysis": ai_summary.get("ai_analysis", ""),
                "model_used": ai_summary.get("model_used", "")
            }
        except UnicodeDecodeError:
            return {"filename": original_filename, "error": "Unable to decode file. Please ensure UTF-8 encoding."}
        except Exception as e:
            logger.exception(f"Scan failed for file {original_filename}")
            return {"filename": original_filename, "error": str(e)}
        finally:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.debug(f"Temporary file '{file_path}' deleted")

    return app

if __name__ == "__main__":
    init_db()
    app = create_app()
    app.run(host="0.0.0.0", port=API_PORT)