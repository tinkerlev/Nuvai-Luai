import os
import uuid
import jwt
from datetime import datetime, timedelta
from redis import Redis
from jwt import ExpiredSignatureError, InvalidTokenError

redis_client = Redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"))
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "change-this-secret")
ALGORITHM = "HS256"
ACCESS_EXPIRATION = int(os.getenv("ACCESS_TOKEN_EXP_MINUTES", 60))
CSRF_EXPIRATION = int(os.getenv("CSRF_TOKEN_EXP_MINUTES", 60))

def create_tokens(user_id):
    now = datetime.utcnow()
    access_jti = str(uuid.uuid4())
    csrf_jti = str(uuid.uuid4())
    access_payload = {
        "jti": access_jti,
        "sub": user_id,
        "iat": now,
        "exp": now + timedelta(minutes=ACCESS_EXPIRATION),
        "type": "access"
    }
    csrf_payload = {
        "jti": csrf_jti,
        "sub": user_id,
        "iat": now,
        "exp": now + timedelta(minutes=CSRF_EXPIRATION),
        "type": "csrf"
    }
    access_token = jwt.encode(access_payload, SECRET_KEY, algorithm=ALGORITHM)
    csrf_token = jwt.encode(csrf_payload, SECRET_KEY, algorithm=ALGORITHM)
    return access_token, csrf_token

def verify_token(token, expected_type="access"):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != expected_type:
            raise InvalidTokenError("Invalid token type")
        jti = payload.get("jti")
        if jti and redis_client.get(f"blacklist:{jti}"):
            raise InvalidTokenError("Token has been revoked")
        return payload
    except ExpiredSignatureError:
        raise InvalidTokenError("Token has expired")
    except Exception as e:
        raise InvalidTokenError(f"Token verification failed: {str(e)}")

def blacklist_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_exp": False})
        jti = payload.get("jti")
        exp = payload.get("exp")
        if jti and exp:
            ttl = int(exp - datetime.utcnow().timestamp())
            if ttl > 0:
                redis_client.setex(f"blacklist:{jti}", ttl, "revoked")
    except Exception as e:
        pass
