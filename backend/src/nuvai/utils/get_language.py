# File: get_language.py

from typing import Optional


EXTENSION_LANGUAGE_MAP = {
    "py": "python",
    "js": "javascript",
    "jsx": "javascript",
    "ts": "typescript",
    "tsx": "typescript",
    "html": "html",
    "htm": "html",
    "css": "css",
    "java": "java",
    "c": "c",
    "cpp": "cpp",
    "h": "cpp",
    "hpp": "cpp",
    "cs": "csharp",
    "go": "go",
    "rb": "ruby",
    "php": "php",
    "sh": "bash",
    "sql": "sql",
    "json": "json",
    "xml": "xml",
    "yml": "yaml",
    "yaml": "yaml",
}


def get_language(filename: str) -> str:
    """
    Detect the language of the file based on its extension.

    Args:
        filename (str): The name of the uploaded file.

    Returns:
        str: Detected language name. Returns 'plaintext' if unknown.
    """
    if not filename or "." not in filename:
        return "plaintext"

    ext = filename.strip().lower().split(".")[-1]
    return EXTENSION_LANGUAGE_MAP.get(ext, "plaintext")
