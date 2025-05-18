# file: auth_routes.py

import os
import jwt
import datetime
from flask import Blueprint, request, jsonify
from src.nuvai.models.user import User 
from src.nuvai.utils.logger import get_logger
from src.utils.sanitize import sanitize_email, sanitize_text
from src.nuvai.utils.token_utils import generate_jwt


auth_blueprint = Blueprint("auth", __name__)
logger = get_logger(__name__)

@auth_blueprint.route("/register", methods=["POST", "OPTIONS"])
def register():
    if request.method == "OPTIONS":
        logger.debug("CORS preflight received on /register")
        return jsonify({"message": "Preflight OK"}), 200

    try:
        data = request.get_json(force=True)
        if not data:
            logger.warning("Missing JSON in request")
            return jsonify({"message": "Missing JSON"}), 400

        email = sanitize_email(data.get("email", ""))
        password = data.get("password", "")
        first_name = sanitize_text(data.get("firstName", ""), max_length=50)
        last_name = sanitize_text(data.get("lastName", ""), max_length=50)
        plan = sanitize_text(data.get("plan", "free"), max_length=20)

        if not email or not password:
            return jsonify({"message": "Missing required fields"}), 400
        if len(password) < 12:
            return jsonify({"message": "Password must be at least 12 characters."}), 400

        if User.get_by_email(email):
            logger.info(f"Duplicate registration attempt: {email}")
            return jsonify({"message": "Email already registered."}), 409

        new_user = User(
            email=email,
            role="user",
            first_name=first_name,
            last_name=last_name,
            plan=plan
        )
        new_user.set_password(password)
        new_user.save()

        logger.info(f"✅ New user registered: {email}")
        return jsonify({"message": "User registered successfully."}), 200

    except Exception as e:
        logger.exception("Unhandled exception during registration")
        return jsonify({"message": "Internal server error."}), 500


@auth_blueprint.route("/login", methods=["POST", "OPTIONS"])
def login():
    if request.method == "OPTIONS":
        logger.debug("CORS preflight received on /login")
        return jsonify({"message": "Preflight OK"}), 200

    try:
        data = request.get_json(force=True)
        if not data:
            return jsonify({"message": "Missing JSON"}), 400

        email = sanitize_email(data.get("email", ""))
        password = data.get("password", "")

        if not email or not password:
            return jsonify({"message": "Missing email or password"}), 400

        user = User.get_by_email(email)
        print("[DEBUG] Received data:", data)
        if not user or not user.check_password(password):
            logger.warning(f"Failed login for {email}")
            return jsonify({"message": "Invalid credentials"}), 401
        
        token = generate_jwt(user.id, user.email)

        csrf_token = os.urandom(16).hex()

        return jsonify({
            "message": "Login successful",
            "token": token,
            "csrfToken": csrf_token
        }), 200

    except Exception as e:
        logger.exception("Unhandled exception during login")
        return jsonify({"message": "Unexpected error occurred. Please try again later."}), 500
