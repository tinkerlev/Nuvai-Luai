# File: reset_password_secure.py

from flask import Blueprint, request, jsonify
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from werkzeug.security import generate_password_hash
from src.nuvai.models.user import User
from src.nuvai.utils.email_utils import send_reset_email
from config import get_config
from markupsafe import escape
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from src.nuvai.utils.logger import get_logger
import re


config = get_config()
SECRET_KEY = config.get("JWT_SECRET")

# Validate SECRET_KEY existence
if not SECRET_KEY:
    raise EnvironmentError("[SECURITY] Missing JWT_SECRET in environment configuration")

# Setup Blueprint, logger and serializer
reset_blueprint = Blueprint("reset", __name__)
serializer = URLSafeTimedSerializer(SECRET_KEY)
logger = get_logger(__name__)

# Setup rate limiting (5 requests per 15 minutes per IP)
limiter = Limiter(key_func=get_remote_address)
limiter.limit("5 per 15 minutes")(reset_blueprint)

# Strong password regex - OWASP + NIST + ISO/IEC 27001 compliant
PASSWORD_REGEX = re.compile(
    r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)"
    r"(?=.*[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>/?]).{12,}$"
)

@reset_blueprint.route("/forgot-password", methods=["POST"])
def forgot_password():
    data = request.get_json()
    email = escape(data.get("email", "").strip())

    if not email or not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
        logger.warning("Invalid email format received in forgot-password request")
        return jsonify({"message": "Invalid email format."}), 422

    user = User.query.filter_by(email=email).first()
    if user:
        try:
            token = serializer.dumps({"email": user.email})
            send_reset_email(user.email, token)
            logger.info(f"Password reset link sent to {user.email}")
        except Exception as e:
            logger.error(f"Failed to send password reset email: {str(e)}")

    # Always respond generically for security
    return jsonify({"message": "If your email is valid, a reset link was sent."}), 200


@reset_blueprint.route("/reset-password", methods=["POST"])
def reset_password():
    data = request.get_json()
    token = data.get("token")
    new_password = escape(data.get("password", "").strip())

    if not token or not new_password:
        logger.warning("Reset-password request missing token or password")
        return jsonify({"message": "Token and password are required."}), 400

    if not PASSWORD_REGEX.match(new_password):
        logger.warning("Password does not meet security requirements")
        return jsonify({"message": "Password does not meet security requirements."}), 422

    try:
        decoded = serializer.loads(token, max_age=3600)
        email = decoded.get("email")
    except SignatureExpired:
        logger.warning("Reset token expired")
        return jsonify({"message": "Token expired. Please request a new reset link."}), 403
    except BadSignature:
        logger.warning("Invalid reset token")
        return jsonify({"message": "Invalid token."}), 401

    user = User.query.filter_by(email=email).first()
    if not user:
        logger.warning(f"User not found for reset token email: {email}")
        return jsonify({"message": "User not found."}), 404

    user.password = generate_password_hash(new_password)
    user.save()
    logger.info(f"Password reset successfully for user: {user.email}")

    return jsonify({"message": "Password reset successful. You may now log in."}), 200
