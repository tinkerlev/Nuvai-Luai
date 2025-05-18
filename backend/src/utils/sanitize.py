# File: sanitize.py

import re
import unicodedata
from html import escape as html_escape

MAX_LENGTH_EMAIL = 120
MAX_LENGTH_TEXT = 255
MAX_LENGTH_NAME = 50

# Prevent dangerous characters and XSS-like input
DISALLOWED_PATTERN = re.compile(r"[<>\"'`;\\(){}\[\]]")

def sanitize_email(email: str) -> str:
    """
    Strictly sanitize and validate an email.
    - Normalizes Unicode (NFKC)
    - Converts to lowercase
    - Enforces strict RFC-like pattern
    - Rejects dangerous characters
    """
    if not isinstance(email, str):
        raise TypeError("Email must be a string.")

    email = unicodedata.normalize("NFKC", email.strip().lower())[:MAX_LENGTH_EMAIL]

    email_regex = (
        r"^(?!.*[<>{}\[\]\"';])"  # disallow dangerous characters
        r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    )

    if not re.fullmatch(email_regex, email):
        raise ValueError("Invalid email format.")
    
    return email


def sanitize_text(text: str, max_length: int = MAX_LENGTH_TEXT) -> str:
    """
    Sanitize general text input:
    - Normalize Unicode
    - Strip spaces
    - Truncate
    - Reject dangerous characters
    """
    if not isinstance(text, str):
        raise TypeError("Expected string input.")

    text = unicodedata.normalize("NFKC", text.strip())
    if DISALLOWED_PATTERN.search(text):
        raise ValueError("Text contains disallowed characters.")
    
    return text[:max_length]


def sanitize_name(name: str, max_length: int = MAX_LENGTH_NAME) -> str:
    """
    Unicode-safe name sanitizer:
    - Allows all letters (עברית, عربى, 日本語)
    - Allows space, hyphen, apostrophe
    - Blocks emojis, symbols, control characters
    - Raises on suspicious input
    """
    if not isinstance(name, str):
        raise TypeError("Expected name to be a string.")

    name = unicodedata.normalize("NFKC", name.strip())[:max_length]

    if DISALLOWED_PATTERN.search(name):
        raise ValueError("Name contains disallowed characters.")

    if not all(
        unicodedata.category(ch).startswith("L") or ch in " -'"
        for ch in name
    ):
        raise ValueError("Name contains invalid characters.")

    return name


def sanitize_for_display(text: str, max_length: int = MAX_LENGTH_TEXT) -> str:
    """
    Escape text for HTML-safe output
    """
    clean = sanitize_text(text, max_length)
    return html_escape(clean)


def safe_int(value, fallback: int = 0) -> int:
    """
    Convert safely to int, fallback on failure
    """
    try:
        return int(value)
    except (ValueError, TypeError):
        return fallback
