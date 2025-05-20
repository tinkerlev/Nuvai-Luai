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
from src.nuvai.utils.templates.early_access import generate_early_access_email
from src.nuvai.utils.templates.followup_email import generate_followup_email
from src.nuvai.utils.templates.launch_email import generate_launch_email

# Load environment variables
load_dotenv()

logger = get_logger("EmailUtils")

# Load config
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USERNAME")
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
    if not EMAIL_ENABLED:
        logger.warning("Reset email skipped — SMTP not configured.")
        return

    if REDIS_ENABLED:
        try:
            if redis_client.get(token):
                logger.warning(f"Replay attempt blocked for token: {token[:6]}***")
                raise RuntimeError("Token has already been used or issued.")
            redis_client.setex(token, RESET_TOKEN_TTL, "valid")
        except Exception as e:
            logger.warning(f"[REDIS] Token validation failed: {e}")
    else:
        logger.warning("Redis is not enabled — reset tokens won't be validated for replay.")

    try:
        safe_token = quote(token, safe="")
        reset_link = f"{RESET_URL_BASE}?token={safe_token}"

        subject = "🔐 Reset Your Luai Password"
        body = (
            f"Hello,\n\n"
            f"We received a request to reset your password. If you initiated this, click below:\n"
            f"{reset_link}\n\n"
            f"If you didn't request this, ignore this email.\n\n"
            f"- Luai Security Team"
        )

        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = SENDER_EMAIL
        msg["To"] = recipient_email
        msg["Message-ID"] = make_msgid()
        msg.set_content(body)
        msg.add_header("X-Luai-Event", "password_reset")

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

def notify_new_early_access_user(recipient_email: str, first_name: str = "there") -> None:
    """
    Called when a new user registers for early access.
    It fetches the email content from early_access.py and sends the welcome email.
    """
    if not EMAIL_ENABLED:
        logger.warning("Early access email skipped — SMTP not configured.")
        return

    try:
        subject, html_body = generate_early_access_email(first_name)
        plain_text = f"""Hi {first_name},\n\nYou're now part of Luai early access.\nWe'll notify you the moment it's ready.\n\n– The Luai Team"""

        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = SENDER_EMAIL
        msg["To"] = recipient_email
        msg["Message-ID"] = make_msgid()
        msg.set_content(plain_text)
        msg.add_alternative(html_body, subtype="html")
        msg.add_header("X-Luai-Event", "early_access")

        context = ssl.create_default_context()
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls(context=context)
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)

        logger.info(f"✅ Early access email sent to {recipient_email[:3]}***")

    except Exception as e:
        logger.error(f"❌ Failed to send early access email: {e}")
        raise RuntimeError("Could not send early access email.")


def send_followup_email(recipient_email: str, first_name: str) -> None:
    """
    Sends the follow-up email to users who signed up for early access but haven't interacted yet.
    """
    if not EMAIL_ENABLED:
        logger.warning("Follow-up email skipped — SMTP not configured.")
        return

    try:
        subject, html_body = generate_followup_email(first_name)
        plain_text = f"""Hi {first_name},\n\nThanks again for signing up for early access to Luai!\nWe're almost ready. Soon you'll be able to scan your code instantly and stay secure with AI-powered analysis.\n\n– The Luai Team"""

        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = SENDER_EMAIL
        msg["To"] = recipient_email
        msg["Message-ID"] = make_msgid()
        msg.set_content(plain_text)
        msg.add_alternative(html_body, subtype="html")
        msg.add_header("X-Luai-Event", "follow_up")

        context = ssl.create_default_context()
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls(context=context)
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)

        logger.info(f"📬 Follow-up email sent to {recipient_email[:3]}***")

    except Exception as e:
        logger.error(f"❌ Failed to send follow-up email: {e}")
        raise RuntimeError("Could not send follow-up email.")

def send_launch_email(recipient_email: str, first_name: str, invite_link: str):
    if not EMAIL_ENABLED:
        logger.warning("Launch email skipped — SMTP not configured.")
        return

    try:
        subject, html_body = generate_launch_email(first_name, invite_link)
        plain_text = f"""Hi {first_name},\n\nLuai is now live! Start scanning your code now using your unique link:\n{invite_link}\n\n– The Luai Team"""

        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = SENDER_EMAIL
        msg["To"] = recipient_email
        msg["Message-ID"] = make_msgid()
        msg.set_content(plain_text)
        msg.add_alternative(html_body, subtype="html")
        msg.add_header("X-Luai-Event", "launch")

        context = ssl.create_default_context()
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls(context=context)
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)

        logger.info(f"🚀 Launch email sent to {recipient_email[:3]}***")

    except Exception as e:
        logger.error(f"❌ Failed to send launch email: {e}")
        raise RuntimeError("Could not send launch email.")