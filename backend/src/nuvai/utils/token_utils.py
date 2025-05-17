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
JWT_SECRET = os.getenv("JWT_SECRET")
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
