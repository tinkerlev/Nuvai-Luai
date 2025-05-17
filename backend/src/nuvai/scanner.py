# File: scanner.py

"""
Description:
This is the central dispatcher module for the Nuvai scanning engine.
It identifies the programming language of the target file (based on extension and content heuristics),
imports the appropriate scanning module, and runs a complete analysis using that module.

Security Enhancements:
- Validates file extension and checks for content-based hints
- Handles unexpected and malformed content safely
- Prevents bypasses using misleading extensions (e.g., .txt with JavaScript content)
- Supports future expansion for advanced content analysis and AI-based detection

Supported Languages:
- Python (.py)
- JavaScript (.js)
- HTML (.html)
- JSX (.jsx)
- TypeScript (.ts)
- PHP (.php)
- C++ (.cpp)

Returns structured findings, errors, or recommendations for next actions.
Provides tailored remediation tips based on detected vulnerabilities.
"""

import os
import logging
import re

logger = logging.getLogger(__name__)

SUPPORTED_LANGUAGES = {
    ".py": ("python", "PythonScanner"),
    ".js": ("javascript", "JavaScriptScanner"),
    ".html": ("html", "HTMLScanner"),
    ".jsx": ("jsx", "JSXScanner"),
    ".php": ("php", "PHPScanner"),
    ".cpp": ("cpp", "CppScanner"),
    ".ts": ("typescript", "TypeScriptScanner"),
}

CONTENT_SIGNATURES = {
    "python": [r"def ", r"import "],
    "javascript": [r"function ", r"console\\.log"],
    "html": [r"<html", r"<!DOCTYPE"],
    "jsx": [r"<\\w+", r"import React"],
    "php": [r"<\\?php", r"echo "],
    "cpp": [r"#include", r"std::"],
    "typescript": [r"interface ", r"import .* from \".*\""],
}

def get_language(file_path, code=None):
    ext = os.path.splitext(file_path)[1].lower()
    language = SUPPORTED_LANGUAGES.get(ext, (None, None))[0]

    if not language and code:
        for lang, patterns in CONTENT_SIGNATURES.items():
            for pat in patterns:
                if re.search(pat, code):
                    return lang
    return language

def scan_code(code, language):
    try:
        code = code.strip()
        if not code or not language:
            return [{
                "level": "ERROR",
                "type": "Missing Input",
                "message": "Missing source code or language type.",
                "recommendation": "Please check the input and try again."
            }]

        scanner = None
        if language == "python":
            from .python_scanner import PythonScanner
            scanner = PythonScanner(code)
        elif language == "javascript":
            from .javascript_scanner import JavaScriptScanner
            scanner = JavaScriptScanner(code)
        elif language == "html":
            from .html_scanner import HTMLScanner
            scanner = HTMLScanner(code)
        elif language == "jsx":
            from .jsx_scanner import JSXScanner
            scanner = JSXScanner(code)
        elif language == "php":
            from .php_scanner import PHPScanner
            scanner = PHPScanner(code)
        elif language == "cpp":
            from .cpp_scanner import CppScanner
            scanner = CppScanner(code)
        elif language == "typescript":
            from .typescript_scanner import TypeScriptScanner
            scanner = TypeScriptScanner(code)
        else:
            return [{
                "level": "ERROR",
                "type": "Unsupported Language",
                "message": f"The language '{language}' is currently not supported.",
                "recommendation": "Check for updates or verify file extension."
            }]

        findings = scanner.run_all_checks()

        if not findings:
            return [{
                "level": "INFO",
                "type": "No Issues Detected",
                "message": "The scan completed but no issues were found.",
                "recommendation": "Continue following secure coding practices."
            }]

        # Add tips if issues were found
        findings.append({
            "level": "TIP",
            "type": "Security Guidance",
            "message": "Consider applying secure development best practices.",
            "recommendation": (
                "- Validate all user inputs strictly.\n"
                "- Avoid insecure default configurations.\n"
                "- Use secure libraries and keep them updated.\n"
                "- Avoid exposing debug or verbose logs in production.\n"
                "- Perform code reviews and vulnerability assessments regularly."
            )
        })

        return findings

    except ImportError as e:
        logger.exception("Scanner module import failed")
        return [{
            "level": "ERROR",
            "type": "Scanner Import Failure",
            "message": str(e),
            "recommendation": f"Ensure the '{language}_scanner.py' file is present and properly named."
        }]

    except Exception as e:
        logger.exception("Unhandled exception during scan")
        return [{
            "level": "ERROR",
            "type": "Unexpected Scanner Error",
            "message": "A critical error occurred during scanning.",
            "recommendation": "Please try again or contact support."
        }]