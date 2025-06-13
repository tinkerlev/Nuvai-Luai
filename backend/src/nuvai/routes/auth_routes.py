# auth_routes.py

import os
import secrets
import base64
import json
import traceback
import stripe
from flask import session, Blueprint, request, jsonify, url_for, make_response, redirect, abort
from authlib.integrations.flask_client import OAuth
from jwt import InvalidTokenError
from redis import Redis
from werkzeug.utils import secure_filename

from src.nuvai.utils.logger import get_logger
from src.nuvai.utils.sanitize import sanitize_email, sanitize_text, sanitize_name
from src.nuvai.models.user import User
from src.nuvai.utils.token_utils import generate_jwt
from flask_jwt_extended import jwt_required, get_jwt_identity


auth_blueprint = Blueprint("auth", __name__)
logger = get_logger(__name__)
oauth = OAuth()
redis_client = Redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"))
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

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
    session['redirect_after_oauth'] = request.args.get('returnTo', '/scan')
    client = oauth.create_client(provider)
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
        email, name, logo_url = None, None, None
        if provider == 'github':
            user_profile = client.get('user', token=token).json()
            name = user_profile.get('name') or user_profile.get('login')
            email = user_profile.get('email')
            logo_url = user_profile.get("avatar_url")
            if not email:
                user_emails_info = client.get('user/emails', token=token).json()
                for e_info in user_emails_info:
                    if e_info.get('primary') and e_info.get('verified'):
                        email = e_info.get('email'); break
        else:
            user_info = client.parse_id_token(token, nonce=nonce)
            email, name, logo_url = user_info.get("email"), user_info.get("name"), user_info.get("picture")
        if not email:
            return redirect(f"{base_frontend_url}/login?error=no_email")
        sanitized_email, sanitized_name = sanitize_email(email), sanitize_name(name or "")
        user = User.get_by_email(sanitized_email)
        if not user:
            user = User.create_oauth_user(email=sanitized_email, name=sanitized_name, provider=provider, logo_url=logo_url)
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
        jwt_token = generate_jwt(new_user.id, new_user.email)
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
        jwt_token = generate_jwt(user.id, user.email)
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

        user.logo_path = os.path.join("user_logos", filename).replace("\\", "/")
        user.save()
        
        new_logo_url = f"/user-logo/{filename}"
        logger.info(f"Sending logo URL to client: {new_logo_url}")

        return jsonify({
            "message": "Profile picture updated",
            "newLogoUrl": new_logo_url
        }), 200

    except Exception as e:
        logger.error(f"Picture upload failed for {user.email}: {e}")
        return jsonify(msg="Server error during file upload"), 500

@auth_blueprint.route("/webhooks/stripe", methods=['POST'])
def stripe_webhook():
    payload, sig_header = request.data, request.headers.get('Stripe-Signature')
    endpoint_secret = os.getenv('STRIPE_WEBHOOK_SECRET')
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except Exception as e:
        logger.error(f"Stripe webhook error: {e}")
        return jsonify(status='error'), 400
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
    return jsonify(status='success'), 200
    
@auth_blueprint.route("/create-checkout-session", methods=['POST'])
@jwt_required(optional=True)
def create_checkout_session():
    try:
        data = request.get_json()
        price_id = data.get('priceId')
        return jsonify({'id': 'some_session_id'})
    except Exception as e:
        return jsonify(error={"message": str(e)}), 500