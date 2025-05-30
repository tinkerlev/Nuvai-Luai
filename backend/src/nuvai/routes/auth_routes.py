import os
import jwt
import secrets
import datetime
from flask import Blueprint, request, jsonify, url_for, make_response, redirect, abort
from authlib.integrations.flask_client import OAuth
from jwt import InvalidTokenError
from redis import Redis
from src.nuvai.utils.jwt_utils import create_tokens, verify_token, blacklist_token
from src.nuvai.utils.logger import get_logger
from src.nuvai.utils.sanitize import sanitize_email, sanitize_text, sanitize_name
from src.nuvai.models.user import User

auth_blueprint = Blueprint("auth", __name__)
logger = get_logger(__name__)
oauth = OAuth()
redis_client = Redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"))
# --- OAuth Providers ---
ALLOWED_PROVIDERS = {
    "google": {
        "client_id": os.getenv("GOOGLE_CLIENT_ID"),
        "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
        "access_token_url": "https://oauth2.googleapis.com/token",
        "authorize_url": "https://accounts.google.com/o/oauth2/auth",
        "api_base_url": "https://www.googleapis.com/oauth2/v1/",
        "userinfo_endpoint": "userinfo",
        "client_kwargs": {"scope": "openid email profile", "prompt": "consent"}
    },
    "github": {
        "client_id": os.getenv("GITHUB_CLIENT_ID"),
        "client_secret": os.getenv("GITHUB_CLIENT_SECRET"),
        "access_token_url": "https://github.com/login/oauth/access_token",
        "authorize_url": "https://github.com/login/oauth/authorize",
        "api_base_url": "https://api.github.com/",
        "userinfo_endpoint": "user",
        "client_kwargs": {"scope": "read:user user:email"}
    },
    "linkedin": {
        "client_id": os.getenv("LINKEDIN_CLIENT_ID"),
        "client_secret": os.getenv("LINKEDIN_CLIENT_SECRET"),
        "access_token_url": "https://www.linkedin.com/oauth/v2/accessToken",
        "authorize_url": "https://www.linkedin.com/oauth/v2/authorization",
        "api_base_url": "https://api.linkedin.com/v2/",
        "userinfo_endpoint": "me?projection=(id,localizedFirstName,localizedLastName,emailAddress)",
        "client_kwargs": {"scope": "r_liteprofile r_emailaddress"}
    }
}
for name, config in ALLOWED_PROVIDERS.items():
    oauth.register(name=name, **config)

@auth_blueprint.route("/auth/login/<provider>")
def login_provider(provider):
    provider = provider.lower().strip()
    if provider not in ALLOWED_PROVIDERS:
        abort(400, description="Unsupported provider")
    redirect_uri = url_for("auth.callback_provider", provider=provider, _external=True)
    state = secrets.token_urlsafe(16)
    return oauth.create_client(provider).authorize_redirect(redirect_uri, state=state)

@auth_blueprint.route("/auth/callback/<provider>")
def callback_provider(provider):
    provider = provider.lower().strip()
    if provider not in ALLOWED_PROVIDERS:
        abort(400, description="Unsupported provider")
    try:
        oauth_client = oauth.create_client(provider)
        token = oauth_client.authorize_access_token()
        userinfo_url = ALLOWED_PROVIDERS[provider]["userinfo_endpoint"]
        user_info = oauth_client.get(userinfo_url).json()
        email = user_info.get("email") or user_info.get("login")
        name = user_info.get("name") or user_info.get("localizedFirstName")
        if not email or not name:
            return jsonify({"error": "Missing user information"}), 400
        email = sanitize_email(email)
        user = User.get_by_email(email)
        if not user:
            user = User.create_oauth_user(email=email, name=name, provider=provider)
        jwt_token, csrf_token = create_tokens(user.id)
        redirect_url = "https://luai.io/dashboard" if os.getenv("ENV", "development") == "production" else "http://localhost:3000/dashboard"
        resp = make_response(redirect(redirect_url))
        resp.set_cookie("__Secure-luai.jwt", jwt_token, httponly=True, secure=True, samesite='Lax', max_age=3600)
        resp.set_cookie("__Secure-luai.csrf", csrf_token, httponly=False, secure=True, samesite='Lax', max_age=3600)
        return resp
    except Exception as e:
        logger.error(f"OAuth callback failed: {str(e)}")
        return jsonify({"error": f"{provider} authentication failed"}), 400

@auth_blueprint.route("/auth/logout", methods=["POST"])
def logout():
    access_token = request.cookies.get("__Secure-luai.jwt")
    csrf_token = request.cookies.get("__Secure-luai.csrf")
    if not access_token or not csrf_token:
        return jsonify({"error": "Missing tokens"}), 400
    try:
        verify_token(access_token, expected_type="access")
        verify_token(csrf_token, expected_type="csrf")
        blacklist_token(access_token)
        blacklist_token(csrf_token)
        response = jsonify({"message": "Successfully logged out"})
        response.delete_cookie("__Secure-luai.jwt")
        response.delete_cookie("__Secure-luai.csrf")
        return response, 200
    except InvalidTokenError as e:
        return jsonify({"error": f"Logout failed: {str(e)}"}), 401

@auth_blueprint.route("/register", methods=["POST", "OPTIONS"])
def register():
    if request.method == "OPTIONS":
        return jsonify({"message": "Preflight OK"}), 200
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
        if not email or not password:
            return jsonify({"message": "Missing required fields"}), 400
        if len(password) < 12:
            return jsonify({"message": "Password must be at least 12 characters."}), 400
        if User.get_by_email(email):
            return jsonify({"message": "Email already registered."}), 409
        new_user = User(
            email=email,
            role="user",
            first_name=first_name,
            last_name=last_name,
            plan=plan,
            phone=phone,
            profession=profession,
            company=company
        )
        new_user.set_password(password)
        new_user.save()
        logger.info(f"New user registered: {email}")
        return jsonify({"message": "User registered successfully."}), 200
    except Exception as e:
        import traceback
        logger.exception("Unhandled exception during registration")
        return jsonify({
            "message": "Internal server error.",
            "details": str(e),
            "trace": traceback.format_exc()
        }), 500

@auth_blueprint.route("/login", methods=["POST", "OPTIONS"])
def login():
    if request.method == "OPTIONS":
        return jsonify({"message": "Preflight OK"}), 200
    try:
        data = request.get_json(force=True)
        email = sanitize_email(data.get("email", ""))
        password = data.get("password", "")
        if not email or not password:
            return jsonify({"message": "Missing email or password"}), 400
        user = User.get_by_email(email)
        if not user or not user.check_password(password):
            return jsonify({"message": "Invalid credentials"}), 401
        jwt_token, csrf_token = create_tokens(user.id)
        response = jsonify({
            "message": "Login successful"
        })
        response.set_cookie("__Secure-luai.jwt", jwt_token, httponly=True, secure=True, samesite='Lax', max_age=3600)
        response.set_cookie("__Secure-luai.csrf", csrf_token, httponly=False, secure=True, samesite='Lax', max_age=3600)
        return response
    except Exception as e:
        import traceback
        logger.exception("Unhandled exception during login")
        return jsonify({
            "message": "Unexpected error occurred",
            "details": str(e),
            "traceback": traceback.format_exc()
        }), 500
