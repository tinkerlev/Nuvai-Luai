# File: config.py

import os
from pathlib import Path
from dotenv import load_dotenv

def try_load_dotenv():
    dotenv_path = Path(__file__).resolve().parent.parent / ".env"
    if dotenv_path.exists():
        load_dotenv(dotenv_path)

try:
    from dotenv import load_dotenv
    try_load_dotenv()
except ImportError:
    pass

def get_config():
    return {
        "ENV": os.getenv("NUVAI_ENV", "development"),
        "DEBUG": os.getenv("NUVAI_DEBUG", "False") == "True",
        "LOG_LEVEL": os.getenv("NUVAI_LOG_LEVEL", "INFO"),
        "JWT_SECRET": os.getenv("NUVAI_SECRET"),
        "MAX_UPLOAD_SIZE_MB": int(os.getenv("NUVAI_MAX_UPLOAD_SIZE", "2")),
        "RATE_LIMIT_REQ_PER_MIN": int(os.getenv("NUVAI_RATE_LIMIT", "30")),
        "ENABLE_ANALYTICS": os.getenv("NUVAI_ANALYTICS", "False") == "True",
        "ALLOW_EXTERNAL_API": os.getenv("NUVAI_ALLOW_API", "False") == "True",
        "PROFILE": os.getenv("NUVAI_PROFILE", "default"),
        "ALLOWED_ORIGINS": os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(","),
        "SMTP": {
            "SERVER": os.getenv("SMTP_SERVER", "smtp.luai.io"),
            "PORT": int(os.getenv("SMTP_PORT", "587")),
            "USERNAME": os.getenv("SMTP_USERNAME", "noreply@luai.io"),
            "PASSWORD": os.getenv("SMTP_PASSWORD"),
            "FROM": os.getenv("MAIL_FROM", "Luai <noreply@luai.io>")
        }
    }

def validate_config():
    required = ["NUVAI_SECRET", "NUVAI_ENV", "SMTP_PASSWORD", "SMTP_USERNAME", "SMTP_SERVER", "SMTP_PORT", "MAIL_FROM"]
    for var in required:
        if not os.getenv(var):
            raise EnvironmentError(f"[SECURITY] Missing critical env var: {var}")
