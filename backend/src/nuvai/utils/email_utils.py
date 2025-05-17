# File: email_utils.py

import os
import smtplib
import ssl
import redis
from email.message import EmailMessage
from email.utils import make_msgid
from urllib.parse import quote
from dotenv import load_dotenv
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.backends import default_backend
from src.nuvai.utils.logger import get_logger

# Load environment variables
load_dotenv()

logger = get_logger("EmailUtils")

# Load config
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
RESET_URL_BASE = os.getenv("RESET_URL_BASE", "https://localhost:5173/reset-password")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
SENDER_EMAIL = os.getenv("MAIL_FROM", SMTP_USER)

# S/MIME optional
SMIME_CERT_PATH = os.getenv("SMIME_CERT_PATH")
SMIME_KEY_PATH = os.getenv("SMIME_KEY_PATH")
SMIME_KEY_PASSWORD = os.getenv("SMIME_KEY_PASSWORD")

RESET_TOKEN_TTL = int(os.getenv("RESET_TOKEN_TTL", 3600))

# Flags
EMAIL_ENABLED = all([SMTP_SERVER, SMTP_USER, SMTP_PASSWORD])
if not EMAIL_ENABLED:
    logger.warning("[EMAIL] SMTP configuration incomplete. Email features disabled.")

try:
    redis_client = redis.StrictRedis.from_url(REDIS_URL, decode_responses=True)
    redis_client.ping()
    REDIS_ENABLED = True
except Exception as e:
    logger.warning(f"[EMAIL] Redis unavailable: {e}")
    REDIS_ENABLED = False


def send_reset_email(recipient_email: str, token: str) -> None:
    """
    Sends a password reset email with a single-use token link.
    Token is stored in Redis with TTL for replay prevention.
    """
    if not EMAIL_ENABLED:
        logger.warning("Reset email skipped — SMTP not configured.")
        return

    if REDIS_ENABLED and redis_client.get(token):
        logger.warning(f"Replay attempt blocked for token: {token[:6]}***")
        raise RuntimeError("Token has already been used or issued.")

    try:
        if REDIS_ENABLED:
            redis_client.setex(token, RESET_TOKEN_TTL, "valid")

        safe_token = quote(token, safe="")
        reset_link = f"{RESET_URL_BASE}?token={safe_token}"

        subject = "🔐 Reset Your Nuvai Password"
        body = (
            f"Hello,\n\n"
            f"We received a request to reset your password. If you initiated this, click below:\n"
            f"{reset_link}\n\n"
            f"If you didn't request this, ignore this email.\n\n"
            f"- Nuvai Security Team"
        )

        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = SENDER_EMAIL
        msg["To"] = recipient_email
        msg["Message-ID"] = make_msgid()
        msg.set_content(body)

        msg.add_header("X-Nuvai-Event", "password_reset")

        if SMIME_CERT_PATH and SMIME_KEY_PATH:
            try:
                with open(SMIME_KEY_PATH, "rb") as key_file:
                    load_pem_private_key(
                        key_file.read(),
                        password=SMIME_KEY_PASSWORD.encode() if SMIME_KEY_PASSWORD else None,
                        backend=default_backend()
                    )
                logger.warning("[SECURE NOTICE] S/MIME signing stub exists but not implemented.")
            except Exception as e:
                logger.warning(f"S/MIME signing failed: {e}")

        context = ssl.create_default_context()
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls(context=context)
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)

        logger.info(f"Reset email sent to {recipient_email[:3]}***")

    except Exception as e:
        logger.error(f"Failed to send reset email: {e}")
        raise RuntimeError("Could not send reset email.")
