# auth_routes.py

import os
import secrets
import base64
import json
import traceback
from uuid import uuid4
from datetime import timedelta
from src.nuvai.utils.token_utils import store_jti_in_redis
from flask import session, Blueprint, request, jsonify, url_for, make_response, redirect, abort, current_app
from authlib.integrations.flask_client import OAuth
from jwt import InvalidTokenError
from redis import Redis
from werkzeug.utils import secure_filename
from src.nuvai.utils.logger import get_logger
from src.nuvai.utils.sanitize import sanitize_email, sanitize_text, sanitize_name
from src.nuvai.models.user import User
from src.nuvai.utils.token_utils import generate_jwt
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

auth_blueprint = Blueprint("auth", __name__)
logger = get_logger(__name__)
oauth = OAuth()
# redis_client = Redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"))

# ALLOWED_PROVIDERS = {
#     "google": {
#         "client_id": os.getenv("GOOGLE_CLIENT_ID"),
#         "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
#         "server_metadata_url": "https://accounts.google.com/.well-known/openid-configuration",
#         "client_kwargs": {"scope": "openid profile email"}
#     },
#     "github": {
#         "client_id": os.getenv("GITHUB_CLIENT_ID"),
#         "client_secret": os.getenv("GITHUB_CLIENT_SECRET"),
#         "api_base_url": "https://api.github.com/",
#         "access_token_url": "https://github.com/login/oauth/access_token",
#         "authorize_url": "https://github.com/login/oauth/authorize",
#         "client_kwargs": {"scope": "read:user user:email"}
#     },
# }
# for name, config in ALLOWED_PROVIDERS.items():
#     oauth.register(name=name, **config)

@auth_blueprint.route("/callback/<provider>")
def callback_provider(provider):
    logger.info(f"--- ENTERING OAuth Callback for provider: {provider} ---")    
    provider_name = provider.lower()
    if provider_name not in current_app.config['ALLOWED_PROVIDERS']:
        logger.warning(f"Callback received for unsupported provider: {provider_name}")
        abort(400, "Unsupported provider")

    base_frontend_url = os.getenv("DEV_FRONTEND_URL", "http://localhost:3000")
    if os.getenv("NUVAI_ENV") == "production":
        base_frontend_url = os.getenv("PROD_FRONTEND_URL", "https://luai.io")
    return_to_path = session.pop('redirect_after_oauth', '/scan')
    
    try:
        client = oauth.create_client(provider_name)
        nonce = session.pop('oauth_nonce', None) if provider_name == 'google' else None
        logger.info("Attempting to exchange authorization code for an access token...")        
        token = client.authorize_access_token(nonce=nonce)        
        logger.info("Successfully received access token. Now fetching user profile...")

        email, name, logo_url = None, None, None
        if provider_name == 'github':
            user_profile = client.get('user', token=token).json()
        else:
            user_info = client.parse_id_token(token, nonce=nonce)
            email, name, logo_url = user_info.get("email"), user_info.get("name"), user_info.get("picture")

        logger.info(f"User profile obtained. Email: {email}, Name: {name}")

        if not email:
            logger.warning("No email found in user profile. Redirecting to login with error.")
            return redirect(f"{base_frontend_url}/login?error=no_email")
            
        sanitized_email, sanitized_name = sanitize_email(email), sanitize_name(name or "")
        logger.info("Connecting to the database (Neon) to check if user exists...")
        
        user = User.get_by_email(sanitized_email)
        
        if not user:
            logger.info(f"User '{sanitized_email}' not found. Creating a new user...")
            user = User.create_oauth_user(email=sanitized_email, name=sanitized_name, provider=provider_name, logo_url=logo_url)
        else:
            logger.info(f"Found existing user: '{sanitized_email}'.")
            if not user.logo_path or user.logo_path.startswith("http"):
                user.logo_path = logo_url
                user.save()
        logger.info("User processed. Now generating JWT and storing session in Redis...")      
        jwt_token, jti = generate_jwt(user.id, user.email)
        store_jti_in_redis(jti)
        logger.info("Session stored successfully. Preparing final redirect...")
        if not return_to_path.startswith('/'): return_to_path = '/scan'
        final_redirect_url = f"{base_frontend_url.rstrip('/')}{return_to_path}"
        resp = make_response(redirect(final_redirect_url))
        resp.set_cookie("luai.jwt", jwt_token, httponly=True, secure=(os.getenv("NUVAI_ENV")=="production"), samesite="Lax", path="/")
        logger.info(f"--- OAuth Callback for {provider_name} COMPLETED ---")
        return resp

    except Exception as e:
        logger.error(f"!!! CRITICAL OAuth callback failed for provider {provider_name} !!!")
        logger.error(f"Error Details: {e}\nFull Traceback:\n{traceback.format_exc()}")
        return redirect(f"{base_frontend_url}/login?error=oauth_failed")

@auth_blueprint.route("/logout", methods=["POST"])
def logout():
    response = jsonify({"message": "Logged out successfully"})
    response.delete_cookie("luai.jwt")
    return response, 200

@auth_blueprint.route("/register", methods=["POST", "OPTIONS"])
def register():
    if request.method == "OPTIONS": return jsonify({"message": "Preflight OK"}), 200
    try:
        data = request.get_json(force=True)
        email, password = sanitize_email(data.get("email", "")), data.get("password", "")
        if not email or not password or len(password) < 12: return jsonify(message="Invalid data"), 400
        if User.get_by_email(email): return jsonify(message="Email already registered."), 409
        new_user = User(
            email=email, role="user",
            first_name=sanitize_name(data.get("firstName", "")),
            last_name=sanitize_name(data.get("lastName", "")),
            plan=sanitize_text(data.get("plan", "free")),
            phone=sanitize_text(data.get("phone", "")),
            profession=sanitize_text(data.get("profession", "")),
            company=sanitize_text(data.get("company", "")),
        )
        new_user.set_password(password)
        new_user.save()
        jwt_token, jti = generate_jwt(new_user.id, new_user.email)
        store_jti_in_redis(jti)
        response = jsonify(message="User registered", user={"id": new_user.id, "email": new_user.email})
        response.set_cookie("luai.jwt", jwt_token, httponly=True, secure=(os.getenv("NUVAI_ENV")=="production"), samesite="Lax", path="/")
        return response, 201
    except Exception as e:
        logger.exception("Registration error")
        return jsonify({"message": "Internal error"}), 500

@auth_blueprint.route("/login", methods=["POST", "OPTIONS"])
def login():
    if request.method == "OPTIONS": return jsonify(message="Preflight OK"), 200
    try:
        data = request.get_json(force=True)
        email, password = sanitize_email(data.get("email", "")), data.get("password", "")
        user = User.get_by_email(email)
        if not user or not user.check_password(password): return jsonify(message="Invalid credentials"), 401
        jwt_token, jti = generate_jwt(user.id, user.email)
        store_jti_in_redis(jti)
        response = jsonify(message="Login successful", user={"id": user.id, "email": user.email})
        response.set_cookie("luai.jwt", jwt_token, httponly=True, secure=(os.getenv("NUVAI_ENV") == "production"), samesite="Lax", path="/")
        return response
    except Exception as e:
        logger.exception("Login error")
        return jsonify(message="Internal error"), 500

@auth_blueprint.route('/userinfo', methods=['GET'])
@jwt_required()
def get_user_info():
    current_user_email = get_jwt_identity()
    jti = get_jwt()["jti"]
    redis_client = current_app.config['REDIS_CLIENT']
    print(f"[DEBUG] JWT Identity: {current_user_email}")
    print(f"[DEBUG] JTI: {jti}")
    if redis_client.get(f"revoked:{jti}"):
        response = jsonify({"msg": "Token invalidated"})
        response.delete_cookie("luai.jwt")
        return response, 401
    if not redis_client.get(f"active:{jti}"):
        response = jsonify({"msg": "Session expired"})
        response.delete_cookie("luai.jwt")
        return response, 401
    user = User.get_by_email(current_user_email)
    if not user: return jsonify(msg="User not found"), 404
    logo_url = user.get_logo_url()
    return jsonify({
        "authenticated": True,
        "user": {
            "id": user.id, "email": user.email, "firstName": user.first_name, "lastName": user.last_name,
            "phone": user.phone, "profession": user.profession, "company": user.company,
            "fullName": user.get_full_name(), "plan": user.plan, "role": user.role,
            "provider": user.oauth_provider or "email", "logoUrl": user.get_logo_url(),
            "initials": f"{user.first_name[0] if user.first_name else ''}{user.last_name[0] if user.last_name else ''}".upper(), "logoUrl": logo_url
        }
    }), 200
    
@auth_blueprint.route("/update-profile", methods=['POST'])
@jwt_required()
def update_profile():
    current_user_email = get_jwt_identity()
    user = User.get_by_email(current_user_email)
    if not user: return jsonify({"error": "User not found"}), 404
    data = request.get_json()
    allowed_fields = ['first_name', 'last_name', 'phone', 'profession', 'company']
    for field in allowed_fields:
        if field in data and data[field] is not None: setattr(user, field, sanitize_text(str(data[field])))
    user.save()
    return jsonify({"message": "Profile updated", "user": {"firstName": user.first_name, "lastName": user.last_name, "phone": user.phone, "profession": user.profession, "company": user.company, "fullName": user.get_full_name()}}), 200

@auth_blueprint.route('/update-profile-picture', methods=['POST'])
@jwt_required()
def update_profile_picture():
    current_user_email = get_jwt_identity()
    user = User.get_by_email(current_user_email)
    if not user: return jsonify(msg="User not found"), 404

    if 'profile_picture' not in request.files: return jsonify(msg="No profile_picture file part"), 400
    file = request.files['profile_picture']
    if file.filename == '': return jsonify(msg="No selected file"), 400
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
    if '.' not in file.filename or file.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
        return jsonify(msg="Invalid file type"), 400
    
    try:
        if user.logo_path and os.path.exists(os.path.join("static", user.logo_path)):
             os.remove(os.path.join("static", user.logo_path))
        filename = f"user_{user.id}_{secrets.token_hex(8)}.{secure_filename(file.filename.rsplit('.', 1)[1].lower())}"
        logos_dir = os.path.join("static", "user_logos")
        os.makedirs(logos_dir, exist_ok=True)
        file_path = os.path.join(logos_dir, filename)
        file.save(file_path)

        user.logo_path = f"static/user_logos/{filename}"
        user.save()

        new_logo_url = f"/static/user_logos/{filename}"
        logger.info(f"Sending logo URL to client: {new_logo_url}")

        return jsonify({
            "message": "Profile picture updated",
            "newLogoUrl": new_logo_url
        }), 200

    except Exception as e:
        logger.error(f"Picture upload failed for {user.email}: {e}")
        return jsonify(msg="Server error during file upload"), 500

@auth_blueprint.route('/delete-profile-picture', methods=['POST'])
@jwt_required()
def delete_profile_picture():
    current_user_email = get_jwt_identity()
    user = User.get_by_email(current_user_email)
    if not user:
        return jsonify({"error": "User not found"}), 404
    if not user.logo_path:
        return jsonify({"message": "No profile picture to delete."}), 200

    try:
        file_to_delete = os.path.join("static", user.logo_path)
        if os.path.exists(file_to_delete):
            os.remove(file_to_delete)
            logger.info(f"Deleted physical logo file for user {user.email}: {file_to_delete}")
        else:
            logger.warning(f"Logo file not found for user {user.email}, but DB entry existed: {file_to_delete}")
        user.logo_path = None
        user.save()
        logger.info(f"Profile picture database path cleared for user {user.email}")
        
        return jsonify({"message": "Profile picture deleted successfully"}), 200

    except Exception as e:
        logger.error(f"Error deleting profile picture for user {user.email}: {str(e)}")
        logger.exception(e)
        return jsonify({"error": "An internal error occurred while deleting the picture."}), 500