# auth_oauth.py
from flask import Blueprint, redirect, request, jsonify, url_for, make_response, abort
from authlib.integrations.flask_client import OAuth
from src.nuvai.utils.logger import get_logger
from src.nuvai.models.user import User
from src.nuvai.utils.jwt_utils import create_tokens
from src.nuvai.utils.sanitize import sanitize_email
from datetime import datetime, timedelta
from redis import Redis
from dotenv import load_dotenv
load_dotenv()
import os
import re
import secrets
from urllib.parse import urlparse

logger = get_logger(__name__)
redis_client = Redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"))

def get_lockout_duration(failure_count):
    if failure_count < 5:
        return 0
    elif failure_count < 10:
        return 60
    elif failure_count < 15:
        return 120
    elif failure_count < 20:
        return 240
    elif failure_count < 25:
        return 480
    else:
        return -1

def is_locked(provider, ip):
    lock_key = f"lock:{provider}:{ip}"
    lock_until = redis_client.get(lock_key)
    if lock_until:
        try:
            if int(lock_until) > int(datetime.utcnow().timestamp()):
                return True
        except ValueError:
            pass
    return False

def register_failed_attempt(provider, ip):
    key = f"failures:{provider}:{ip}"
    lock_key = f"lock:{provider}:{ip}"
    failures = redis_client.incr(key)
    redis_client.expire(key, 3600)
    duration = get_lockout_duration(failures)
    if duration == -1:
        redis_client.set(lock_key, int(datetime.utcnow().timestamp()) + 10 * 365 * 24 * 60 * 60)
    elif duration > 0:
        redis_client.set(lock_key, int(datetime.utcnow().timestamp()) + duration)

def reset_failed_attempts(provider, ip):
    redis_client.delete(f"failures:{provider}:{ip}")
    redis_client.delete(f"lock:{provider}:{ip}")

def is_safe_redirect_path(path):
    if urlparse(path).netloc:
        return False
    if not re.match(r"^/[a-zA-Z0-9/_\-]*$", path):
        return False
    return True

oauth_bp = Blueprint('oauth_bp', __name__)
oauth = OAuth()
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
        "userinfo_endpoint": "me",
        "client_kwargs": {
            "scope": "openid profile email",
            "prompt": "consent"
        }
    }
}
for name, config in ALLOWED_PROVIDERS.items():
    if not config.get("client_id") or not config.get("client_secret"):
        print(f"[OAuth INIT WARNING] Skipping provider '{name}' due to missing credentials.")
        continue
    oauth.register(
        name=name,
        client_id=config["client_id"],
        client_secret=config["client_secret"],
        access_token_url=config["access_token_url"],
        authorize_url=config["authorize_url"],
        api_base_url=config["api_base_url"],
        client_kwargs=config["client_kwargs"]
    )

@oauth_bp.route("/auth/login/<provider>")
def login_provider(provider):
    provider = provider.lower().strip()
    if provider not in ALLOWED_PROVIDERS:
        logger.warning(f"Attempted login with unsupported provider: {provider}")
        abort(400, description="Unsupported provider")
    base = os.getenv("OAUTH_REDIRECT_BASE", request.host_url.rstrip("/"))
    return_to = request.args.get("returnTo", "/login")
    redirect_uri = f"{base}/auth/callback/{provider}?returnTo={return_to}"
    logger.info(f"[OAuth] Using redirect URI for {provider}: {redirect_uri}")

    try:
            state = secrets.token_urlsafe(16)
            return oauth.create_client(provider).authorize_redirect(redirect_uri, state=state)
    except Exception as e:
            logger.exception(f"[OAuth] Failed to redirect to provider {provider}: {str(e)}")
            return jsonify({"error": "OAuth redirect failed", "details": str(e)}), 500

@oauth_bp.route("/auth/callback/<provider>")
def callback_provider(provider):
    provider = provider.lower().strip()
    if provider not in ALLOWED_PROVIDERS:
        logger.warning(f"Callback from unsupported provider: {provider}")
        abort(400, description="Unsupported provider")
    ip_address = request.remote_addr
    if is_locked(provider, ip_address):
        lock_until = redis_client.get(f"lock:{provider}:{ip_address}")
        try:
            seconds_left = int(lock_until) - int(datetime.utcnow().timestamp())
        except (ValueError, TypeError):
            seconds_left = None
        logger.warning(f"Login locked: {provider} | {ip_address} | {seconds_left}s remaining")
        return jsonify({
            "error": "Too many failed attempts",
            "lockout_seconds": seconds_left
        }), 429
    try:
        oauth_client = oauth.create_client(provider)
        token = oauth_client.authorize_access_token()
        userinfo_url = ALLOWED_PROVIDERS[provider]["userinfo_endpoint"]
        user_info = oauth_client.get(userinfo_url).json()

        if provider == "linkedin":
            email_resp = oauth_client.get("emailAddress?q=members&projection=(elements*(handle~))").json()
            email = (
                email_resp.get("elements", [{}])[0]
                .get("handle~", {})
                .get("emailAddress")
            )
            first_name = user_info.get("localizedFirstName")
            last_name = user_info.get("localizedLastName")
            name = f"{first_name} {last_name}".strip() if first_name or last_name else None
        else:
            email = user_info.get("email") or user_info.get("login")
            name = user_info.get("name") or user_info.get("login")
        if not email:
            logger.error(f"{provider.capitalize()} login failed: No email found in user info")
            register_failed_attempt(provider, ip_address)
            return jsonify({"error": "Email not found in user info"}), 400
        if not name:
            logger.warning(f"{provider.capitalize()} login failed: No name found in user info")
            register_failed_attempt(provider, ip_address)
            return jsonify({"error": "No name found in user info"}), 400
        email = sanitize_email(email)
        user = User.get_by_email(email)
        if not user:
            user = User.create_oauth_user(email=email, name=name, provider=provider)
        logger.info(f"{provider.capitalize()} login successful: {email} | {name}")
        reset_failed_attempts(provider, ip_address)
        return_to = request.args.get("returnTo")
        ENVIRONMENT = os.getenv("ENV", "development").lower()
        if return_to and is_safe_redirect_path(return_to):
            base = "https://luai.io" if ENVIRONMENT == "production" else "http://localhost:3000"
            redirect_url = f"{base}{return_to}"
        else:
            if return_to and return_to.startswith("http"):
                logger.warning(f"[OAuth] Unsafe returnTo URL blocked: {return_to}")
            redirect_url = (
                "https://luai.io/dashboard"
                if ENVIRONMENT == "production"
                else "http://localhost:3000/dashboard"
            )
        resp = make_response(redirect(redirect_url))
        jwt_token, csrf_token = create_tokens(user.id)
        resp.set_cookie("luai.jwt", jwt_token, httponly=True, secure=True, samesite='Lax', max_age=3600)
        resp.set_cookie("__Secure-luai.csrf", csrf_token, httponly=False, secure=True, samesite='Lax', max_age=3600)
        return resp
    except Exception as e:
        register_failed_attempt(provider, ip_address)
        logger.error(f"{provider.capitalize()} login failed: {str(e)}")
        return jsonify({"error": f"{provider.capitalize()} authentication failed"}), 400
