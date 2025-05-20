# File: backend/src/nuvai/utils/token_utils.py

import os
import jwt
import datetime
from jwt import ExpiredSignatureError, InvalidTokenError
from dotenv import load_dotenv
from src.nuvai.utils.logger import get_logger

load_dotenv()
logger = get_logger(__name__)

# Load secret key securely from environment
JWT_SECRET = os.getenv("NUVAI_SECRET")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = int(os.getenv("JWT_EXPIRATION_HOURS", 2))

if not JWT_SECRET:
    raise RuntimeError("❌ JWT_SECRET is not set in environment variables.")

def generate_jwt(user_id: int, email: str, custom_claims: dict = None) -> str:
    """
    Generates a secure JWT token with standard and optional custom claims.
    """
    try:
        payload = {
            "sub": user_id,
            "email": email,
            "iat": datetime.datetime.utcnow(),
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=JWT_EXPIRATION_HOURS)
        }

        if custom_claims and isinstance(custom_claims, dict):
            payload.update(custom_claims)

        token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
        return token

    except Exception as e:
        logger.exception("Failed to generate JWT")
        raise RuntimeError("Token generation failed") from e


def verify_jwt(token: str) -> dict:
    """
    Verifies the JWT token and returns the decoded payload.
    Raises specific errors for expired or invalid tokens.
    """
    try:
        decoded = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return decoded

    except ExpiredSignatureError:
        logger.warning("Token expired during verification")
        raise ValueError("Token expired")

    except InvalidTokenError:
        logger.warning("Invalid token received")
        raise ValueError("Invalid token")

    except Exception as e:
        logger.exception("Unhandled token verification error")
        raise RuntimeError("Token verification failed") from e

SECRET_KEY = os.getenv("INVITE_SECRET_KEY", "ultra-secure-key")
INVITE_TOKEN_TTL = int(os.getenv("INVITE_TOKEN_TTL", 7 * 24 * 3600))

if not SECRET_KEY:
    raise RuntimeError("❌ INVITE_SECRET_KEY is not set in environment variables.")

def generate_invite_token(email: str) -> str:
    payload = {
        "email": email,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(seconds=INVITE_TOKEN_TTL),
        "scope": "invite_access"
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token

def build_invite_link(email: str) -> str:
    token = generate_invite_token(email)
    base_url = os.getenv("INVITE_BASE_URL", "https://luai.io/launch").rstrip("/")
    return f"{base_url}?token={token}"

def verify_invite_token(token: str) -> str:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload["email"]
    except jwt.ExpiredSignatureError:
        raise ValueError("Invite token expired.")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid invite token.")
