# File: backend/src/nuvai/utils/sanitize.py

import re
import unicodedata
from html import escape as html_escape

MAX_LENGTH_EMAIL = 120
MAX_LENGTH_TEXT = 255
MAX_LENGTH_NAME = 50

DISALLOWED_PATTERN = re.compile(r"[<>\"'`;\\(){}[\]]")

def sanitize_email(email: str) -> str:
    """
    Sanitizes and validates email input according to strict RFC-like rules.
    Strips whitespace, enforces lowercase, normalizes encoding.
    """
    if not isinstance(email, str):
        raise TypeError("Email must be a string.")

    email = unicodedata.normalize("NFKC", email.strip().lower())
    email = email[:MAX_LENGTH_EMAIL]

    # Strict pattern — excludes suspicious characters
    email_regex = (
        r"^(?!.*[<>{}[\]\"';])"  # disallow dangerous characters
        r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    )

    if not re.fullmatch(email_regex, email):
        raise ValueError("Invalid email format.")

    return email


def sanitize_text(text: str, max_length: int = MAX_LENGTH_TEXT) -> str:
    """
    Basic text sanitization for storage:
    - Strips leading/trailing spaces
    - Normalizes encoding
    - Truncates
    - Rejects dangerous characters
    """
    if not isinstance(text, str):
        raise TypeError("Expected string input.")

    text = unicodedata.normalize("NFKC", text.strip())
    if DISALLOWED_PATTERN.search(text):
        raise ValueError("Text contains disallowed characters.")
    return text[:max_length]


def sanitize_name(name: str, max_length: int = MAX_LENGTH_NAME) -> str:
    """
    Allows only letters, hyphens, apostrophes, spaces.
    Prevents scripts or control characters.
    """
    name = sanitize_text(name, max_length)
    if not re.fullmatch(r"[a-zA-Z\s\-']{1," + str(max_length) + r"}", name):
        raise ValueError("Name contains invalid characters.")
    return name


def sanitize_for_display(text: str, max_length: int = MAX_LENGTH_TEXT) -> str:
    """
    Escapes output for safe use in HTML or UI.
    Useful for previewing untrusted input.
    """
    clean = sanitize_text(text, max_length)
    return html_escape(clean)


def safe_int(value, fallback: int = 0) -> int:
    """
    Tries to safely convert any value to an integer.
    Returns fallback value on failure.
    """
    try:
        return int(value)
    except (ValueError, TypeError):
        return fallback
