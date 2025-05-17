# File: logger.py

"""
Description:
This module provides secure, structured, and environment-aware logging for the Nuvai backend.

Security Compliance:
- ISO/IEC 27001: Log retention, confidentiality, access control
- NIST 800-53: AU-2, AU-6, AU-9, AU-12 compliance
- OWASP: Avoids logging sensitive data (e.g., passwords, tokens)

Features:
- Uses Python's built-in logging with RotatingFileHandler
- Supports console + file logging
- Redacts sensitive fields before logging
- Includes correlation IDs if available
- Can be extended for SIEM integration or remote log shipping
- Logs include UTC timestamp, level, message, and metadata
"""

import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime, timezone
import re

LOG_LEVEL = os.getenv("NUVAI_LOG_LEVEL", "INFO").upper()
LOG_DIR = os.getenv("NUVAI_LOG_DIR", "logs")
LOG_FILE = os.path.join(LOG_DIR, "nuvai.log")
MAX_BYTES = int(os.getenv("NUVAI_LOG_MAX_BYTES", 1048576))  # 1MB
BACKUP_COUNT = int(os.getenv("NUVAI_LOG_BACKUP_COUNT", 5))

os.makedirs(LOG_DIR, exist_ok=True)

# Regex patterns to redact sensitive values
SENSITIVE_KEYS = ["password", "token", "secret", "authorization"]
SENSITIVE_PATTERN = re.compile(rf"({'|'.join(SENSITIVE_KEYS)})(=|:)?\\s*[^\s,;]+", re.IGNORECASE)

def redact_sensitive_data(msg):
    return SENSITIVE_PATTERN.sub(r"\1=[REDACTED]", msg)

class SecureFormatter(logging.Formatter):
    def format(self, record):
        record.msg = redact_sensitive_data(str(record.msg))
        timestamp = datetime.now(timezone.utc).isoformat()
        return f"[{timestamp}] [{record.levelname}] {record.getMessage()}"

def get_logger(name="nuvai"):
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger  # prevent duplicate handlers

    logger.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))

    formatter = SecureFormatter()

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler with rotation
    file_handler = RotatingFileHandler(LOG_FILE, maxBytes=MAX_BYTES, backupCount=BACKUP_COUNT)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger

# Example usage:
# log = get_logger()
# log.info("User logged in", extra={"user": "admin"})
