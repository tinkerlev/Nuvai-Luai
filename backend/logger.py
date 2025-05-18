# File: logger.py
import logging
import os
import re
import stat
from logging.handlers import RotatingFileHandler

# Filter sensitive data from logs
class SensitiveDataFilter(logging.Filter):
    SENSITIVE_PATTERNS = [
        re.compile(r'(password|token|secret|api[_-]?key)', re.IGNORECASE)
    ]

    def filter(self, record):
        msg = str(record.getMessage())
        for pattern in self.SENSITIVE_PATTERNS:
            if pattern.search(msg):
                record.msg = "[FILTERED] Sensitive information removed from log."
                break
        return True

def set_secure_permissions(file_path):
    try:
        os.chmod(file_path, stat.S_IRUSR | stat.S_IWUSR)  # rw-------
    except Exception as e:
        print(f"Warning: Unable to set permissions for {file_path}: {e}")

def setup_logger(name="nuvai", log_level="INFO"):
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.addFilter(SensitiveDataFilter())

    # File Handler with rotation
    log_dir = os.path.join(os.path.expanduser("~"), ".nuvai_logs")
    os.makedirs(log_dir, exist_ok=True)
    file_path = os.path.join(log_dir, "nuvai.log")

    file_handler = RotatingFileHandler(file_path, maxBytes=1_000_000, backupCount=5)
    file_handler.setFormatter(formatter)
    file_handler.addFilter(SensitiveDataFilter())

    set_secure_permissions(file_path)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    logger.propagate = False

    return logger

# Example usage
logger = setup_logger(log_level=os.getenv("NUVAI_LOG_LEVEL", "DEBUG" if os.getenv("RENDER") == "true" else "INFO")
logger.debug("Logger initialized.")
