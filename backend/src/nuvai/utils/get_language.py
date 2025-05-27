# File: get_language.py
import os 
import re
from typing import Optional


EXTENSION_LANGUAGE_MAP = {
    "py": "python",
    "js": "javascript",
    "jsx": "jsx",
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

CONTENT_SIGNATURES = {
    "python": [r"def ", r"import "],
    "javascript": [r"function ", r"console\\.log"],
    "html": [r"<html", r"<!DOCTYPE"],
    "jsx": [r"<\w+", r"import React"],
    "php": [r"<\?php", r"echo "],
    "cpp": [r"#include", r"std::"],
    "typescript": [r"interface ", r"import .* from \".*\""],
}

def get_language(filename: str, code: Optional[str] = None) -> str:
    if not filename or "." not in filename:
        return detect_from_content(code)

    ext = filename.strip().lower().split(".")[-1]
    lang = EXTENSION_LANGUAGE_MAP.get(ext)
    if not lang or (lang == "javascript" and code and "import React" in code):
        return detect_from_content(code)
    return lang or "plaintext"
def detect_from_content(code: Optional[str]) -> str:
    if not code:
        return "plaintext"

    for lang, patterns in CONTENT_SIGNATURES.items():
        for pattern in patterns:
            if re.search(pattern, code):
                return lang
    return "plaintext"

