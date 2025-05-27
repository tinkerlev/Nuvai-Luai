# File: scanner_controller.py
import logging
import re
import mimetypes
from src.nuvai import get_language, scan_code

logger = logging.getLogger(__name__)

SUPPORTED_LANGUAGES = ["python", "javascript", "php", "html", "cpp", "jsx", "typescript"]
BLOCKED_PATTERNS = [
    r"rm\s+-rf", r"shutdown", r"format\s+c:", r"base64,", r"<script>", r"<iframe>", r"<\?php",
    r"eval\s*\(", r"exec\s*\(", r"system\s*\(", r"subprocess\.popen", r"powershell", r"import os",
    r"fork\(", r"document\.write", r"curl\s+", r"wget\s+", r"DROP\s+TABLE"
]

MAX_ALLOWED_SIZE_HARD = 2_000_000  # 2MB
MAX_RECOMMENDED_SIZE = 750_000     # 750KB

def is_potentially_malicious(code: str) -> bool:
    for pattern in BLOCKED_PATTERNS:
        if re.search(pattern, code, flags=re.IGNORECASE):
            return True
    return False

def is_binary_content(code: str) -> bool:
    try:
        code.encode("utf-8").decode("utf-8")
        return False
    except UnicodeDecodeError:
        return True

def get_extension(filename: str) -> str:
    if filename.count('.') > 1:
        return ".".join(filename.lower().split(".")[-2:])
    return filename.lower().rsplit('.', 1)[-1] if '.' in filename else ''

def is_supported_mimetype(filename: str) -> bool:
    mime, _ = mimetypes.guess_type(filename)
    return mime and mime.startswith("text/")

def scan_code_controller(code: str, filename: str) -> list:
    try:
        code = code.strip()
        ext = get_extension(filename)

        if not code or not filename:
            return [{
                "level": "ERROR",
                "type": "Missing Input",
                "message": "No code or filename provided.",
                "recommendation": "Please upload a valid source code file."
            }]

        if len(code) > MAX_ALLOWED_SIZE_HARD:
            return [{
                "level": "ERROR",
                "type": "File Too Large",
                "message": "The uploaded file exceeds the hard size limit (2 MB).",
                "recommendation": "Split your file or scan parts incrementally."
            }]
        
        findings = []

        if len(code) > MAX_RECOMMENDED_SIZE:
            findings.append({
                "level": "INFO",
                "type": "Large File Warning",
                "message": "The file exceeds the recommended scan size (750 KB).",
                "recommendation": "Consider splitting the file for faster analysis."
            })

        if is_binary_content(code):
            return [{
                "level": "ERROR",
                "type": "Binary Content Detected",
                "message": "The file appears to be non-textual or corrupted.",
                "recommendation": "Upload only plain text source code files."
            }]

        if not is_supported_mimetype(filename):
            findings.append({
                "level": "WARNING",
                "type": "Unverified MIME Type",
                "message": "The file has an unknown or unsupported MIME type.",
                "recommendation": "Make sure you are uploading a code file (not an executable or image)."
            })

        if is_potentially_malicious(code):
            return [{
                "level": "CRITICAL",
                "type": "Blocked Malicious Pattern",
                "message": "The code contains patterns commonly associated with abuse or injection.",
                "recommendation": "Remove or sanitize dangerous logic before scanning."
            }]

        language = get_language(filename)
        if language not in SUPPORTED_LANGUAGES:
            return [{
                "level": "ERROR",
                "type": "Unsupported Language",
                "message": f"The detected language '{language}' is not supported.",
                "recommendation": f"Supported languages: {', '.join(SUPPORTED_LANGUAGES)}."
            }]

        findings += scan_code(code, language)
        return findings

    except Exception as e:
        logger.exception("Unhandled error during code scan")
        return [{
            "level": "ERROR",
            "type": "Unexpected Failure",
            "message": "An internal error occurred while processing your request.",
            "recommendation": "Please try again later or contact the Nuvai support team."
        }]
