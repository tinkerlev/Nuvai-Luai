import re
import unicodedata
from html import escape as html_escape

# Constants
MAX_LENGTH_EMAIL = 120
MAX_LENGTH_TEXT = 255
MAX_LENGTH_NAME = 50

def sanitize_email(email: str) -> str:
    """
    Sanitizes and validates email address.
    - Normalizes to NFKC
    - Strips whitespace
    - Converts to lowercase
    - Validates against RFC-compliant regex
    """
    if not isinstance(email, str):
        raise TypeError("Email must be a string.")

    email = unicodedata.normalize("NFKC", email.strip().lower())
    email = email[:MAX_LENGTH_EMAIL]

    email_regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    if not re.fullmatch(email_regex, email):
        raise ValueError("Invalid email format.")
    return email

def sanitize_text(text: str, max_length: int = MAX_LENGTH_TEXT) -> str:
    """
    General-purpose sanitization:
    - Normalizes Unicode to NFKC
    - Strips whitespace
    - Truncates to max length
    """
    if not isinstance(text, str):
        raise TypeError("Expected string input.")
    text = unicodedata.normalize("NFKC", text.strip())
    return text[:max_length]

def sanitize_name(name: str, max_length: int = MAX_LENGTH_NAME) -> str:
    """
    Sanitizes user/display names:
    - Allows only letters, spaces, hyphens, apostrophes
    """
    name = sanitize_text(name, max_length)
    if not re.fullmatch(r"[a-zA-Z\s\-']{1," + str(max_length) + r"}", name):
        raise ValueError("Name contains invalid characters.")
    return name

def sanitize_for_display(text: str, max_length: int = MAX_LENGTH_TEXT) -> str:
    """
    Escapes text for safe rendering in HTML:
    - Prevents XSS
    """
    text = sanitize_text(text, max_length)
    return html_escape(text)

def safe_int(value, fallback: int = 0) -> int:
    """Converts value to int safely, returns fallback on error."""
    try:
        return int(value)
    except (ValueError, TypeError):
        return fallback
