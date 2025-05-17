# File: config.py

"""
Description:
This file centralizes environment-specific settings for Nuvai. It reads all
required configurations from environment variables and ensures that all
critical keys are validated at startup. No secrets are hardcoded.

Security Features:
- Secrets are loaded from environment only
- Supports dynamic configuration for dev/staging/prod
- Includes validation step for critical values
- Safe for public repos (as long as .env is ignored)
- Allows rate limiting and content size controls
- Loads optional .env file if present for local development
- Can integrate with feature flags or remote config in future
- Supports profile-based config switching (dev/test/prod)
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Optional .env loader for local development
def try_load_dotenv():
    dotenv_path = Path(__file__).resolve().parent.parent / ".env"
    if dotenv_path.exists():
        load_dotenv(dotenv_path)

# Load .env file if it exists
try:
    from dotenv import load_dotenv
    try_load_dotenv()
except ImportError:
    pass  # dotenv is optional for local development

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
        "PROFILE": os.getenv("NUVAI_PROFILE", "default")
    }

def validate_config():
    required = ["NUVAI_SECRET", "NUVAI_ENV"]
    for var in required:
        if not os.getenv(var):
            raise EnvironmentError(f"[SECURITY] Missing critical env var: {var}")
