# auth_routes.py
import os
import jwt
import secrets
import datetime
import base64
import json
from flask import session
from flask import Blueprint, request, jsonify, url_for, make_response, redirect, abort
from authlib.integrations.flask_client import OAuth
from jwt import InvalidTokenError
from redis import Redis
from src.nuvai.utils.logger import get_logger
from src.nuvai.utils.sanitize import sanitize_email, sanitize_text, sanitize_name
from src.nuvai.models.user import User
from src.nuvai.utils.token_utils import generate_jwt
from flask_jwt_extended import jwt_required, get_jwt_identity
import traceback

auth_blueprint = Blueprint("auth", __name__)
logger = get_logger(__name__)
oauth = OAuth()
redis_client = Redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"))

ALLOWED_PROVIDERS = {
    "google": {
        "client_id": os.getenv("GOOGLE_CLIENT_ID"),
        "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
        "server_metadata_url": "https://accounts.google.com/.well-known/openid-configuration",
        "client_kwargs": {"scope": "openid profile email"}
    },
    "github": {
        "client_id": os.getenv("GITHUB_CLIENT_ID"),
        "client_secret": os.getenv("GITHUB_CLIENT_SECRET"),
        "api_base_url": "https://api.github.com/",
        "access_token_url": "https://github.com/login/oauth/access_token",
        "authorize_url": "https://github.com/login/oauth/authorize",
        "client_kwargs": {"scope": "read:user user:email"}
    },
}
for name, config in ALLOWED_PROVIDERS.items():
    oauth.register(name=name, **config)

@auth_blueprint.route("/login/<provider>")
def login_provider(provider):
    provider = provider.lower().strip()
    if provider not in ALLOWED_PROVIDERS: abort(400, "Unsupported provider")
    redirect_uri = url_for("auth.callback_provider", provider=provider, _external=True, _scheme='https' if os.getenv("NUVAI_ENV") == "production" else 'http')
    print(f"!!! DEBUG: Generated Callback URL for {provider} is: {redirect_uri}")
    client = oauth.create_client(provider)
    session['redirect_after_oauth'] = request.args.get('returnTo', '/scan')
    
    if provider == 'google':
        nonce = secrets.token_urlsafe(16)
        session['oauth_nonce'] = nonce
        return client.authorize_redirect(redirect_uri, nonce=nonce)
    return client.authorize_redirect(redirect_uri)

@auth_blueprint.route("/callback/<provider>")
def callback_provider(provider):
    provider = provider.lower().strip()
    if provider not in ALLOWED_PROVIDERS: abort(400, "Unsupported provider")
    base_frontend_url = os.getenv("DEV_FRONTEND_URL", "http://localhost:3000")
    if os.getenv("NUVAI_ENV") == "production":
        base_frontend_url = os.getenv("PROD_FRONTEND_URL", "https://luai.io") 
    return_to_path = session.pop('redirect_after_oauth', '/scan')
    
    try:
        client = oauth.create_client(provider)
        nonce = session.pop('oauth_nonce', None) if provider == 'google' else None
        token = client.authorize_access_token(nonce=nonce)
        email, name = None, None
        if provider == 'github':
            user_profile = client.get('user', token=token).json()
            name = user_profile.get('name') or user_profile.get('login')
            email = user_profile.get('email')
            if not email:
                user_emails_info = client.get('user/emails', token=token).json()
                for e_info in user_emails_info:
                    if e_info.get('primary') and e_info.get('verified'):
                        email = e_info.get('email'); break
        else:
            user_info = client.parse_id_token(token, nonce=nonce)
            email, name = user_info.get("email"), user_info.get("name")
        
        if not email:
            logger.error(f"Could not retrieve a valid email from {provider}")
            return redirect(f"{base_frontend_url}/login?error=no_email")

        sanitized_email = sanitize_email(email)
        sanitized_name = sanitize_name(name or "")
        user = User.get_by_email(sanitized_email)
        if not user:
            user = User.create_oauth_user(email=sanitized_email, name=sanitized_name, provider=provider)
        
        jwt_token = generate_jwt(user.id, user.email)
        if not return_to_path.startswith('/'): return_to_path = '/scan'
        final_redirect_url = f"{base_frontend_url.rstrip('/')}{return_to_path}"
        resp = make_response(redirect(final_redirect_url))
        resp.set_cookie("luai.jwt", jwt_token, httponly=True, secure=(os.getenv("NUVAI_ENV")=="production"), samesite="Lax", path="/")
        return resp
        
    except Exception as e:
        logger.error(f"CRITICAL OAuth callback failed: {e}\n{traceback.format_exc()}")
        return redirect(f"{base_frontend_url}/login?error=oauth_failed")

@auth_blueprint.route("/logout", methods=["POST"])
def logout():
    token = request.cookies.get("luai.jwt")
    if not token:
        return jsonify({"error": "No token provided"}), 400
    try:
        response = jsonify({"message": "Logged out successfully"})
        response.delete_cookie("luai.jwt")
        return response, 200
    except Exception as e:
        logger.exception("Logout error")
        return jsonify({"error": "Logout failed"}), 500

@auth_blueprint.route("/register", methods=["POST", "OPTIONS"])
def register():
    if request.method == "OPTIONS": return jsonify({"message": "Preflight OK"}), 200
    try:
        data = request.get_json(force=True)
        email = sanitize_email(data.get("email", ""))
        password = data.get("password", "")
        first_name = sanitize_name(data.get("firstName", ""), max_length=50)
        last_name = sanitize_name(data.get("lastName", ""), max_length=50)
        plan = sanitize_text(data.get("plan", "free"), max_length=20)
        phone = sanitize_text(data.get("phone", ""), max_length=20)
        profession = sanitize_text(data.get("profession", ""), max_length=50)
        company = sanitize_text(data.get("company", ""), max_length=50)
        if not email or not password or len(password) < 12:
            return jsonify({"message": "Invalid registration data"}), 400
        if User.get_by_email(email):
            return jsonify({"message": "Email already registered."}), 409
        new_user = User(
            email=email, role="user", first_name=first_name, last_name=last_name,
            plan=plan, phone=phone, profession=profession, company=company
        )
        new_user.set_password(password)
        new_user.save()
        logger.info(f"New user registered: {email}")
        return jsonify({"message": "User registered successfully."}), 201
    except Exception as e:
        logger.exception("Unhandled exception during registration")
        return jsonify({"message": "Internal server error.", "details": str(e)}), 500

@auth_blueprint.route("/login", methods=["POST", "OPTIONS"])
def login():
    if request.method == "OPTIONS": return jsonify({"message": "Preflight OK"}), 200
    try:
        data = request.get_json(force=True)
        email = sanitize_email(data.get("email", ""))
        password = data.get("password", "")
        if not email or not password:
            return jsonify({"message": "Missing email or password"}), 400
        user = User.get_by_email(email)
        if not user or not user.check_password(password):
            return jsonify({"message": "Invalid credentials"}), 401
        jwt_token = generate_jwt(user.id, user.email)
        response = jsonify(message="Login successful", user={"id": user.id, "email": user.email})
        response.set_cookie(
            "luai.jwt", jwt_token, httponly=True, secure=(os.getenv("ENV") == "production"),
            samesite="Lax", path="/", max_age=60 * 60 * 2
        )
        return response
    except Exception as e:
        logger.exception("Unhandled exception during login")
        return jsonify({"message": "Unexpected error occurred", "details": str(e)}), 500

@auth_blueprint.route('/userinfo', methods=['GET'])
@jwt_required()
def get_user_info():
    current_user_email = get_jwt_identity()
    user = User.get_by_email(current_user_email)
    if not user:
        return jsonify(msg="User not found"), 404
    return jsonify(authenticated=True, user={"id": user.id, "email": user.email}), 200