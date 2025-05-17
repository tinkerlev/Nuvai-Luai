# File: utils.py

"""
Description:
This utility module provides advanced helpers for Nuvai's scanning engine.
It includes core file analysis tools, secure logging, path validation, suspicious pattern detection,
and additional heuristics to catch obfuscated code, risky timing behavior, and encoded payloads.

Security Enhancements:
- Secure path resolution to prevent directory traversal
- Entropy-based secret detection (optional, passive)
- Detection of suspicious or obfuscated code patterns
- Dangerous filename and encoding heuristics
- Time-based or infinite loop detection
- Cross-platform safe I/O compatibility (Linux, macOS, Windows)
- API keys/token regex matching with flexible filtering

Future Additions:
- Memory-aware byte analysis
- Source fingerprinting (LLM/Copilot vs hand-written)
- Runtime signature behavior matcher
"""

import os
import platform
import logging
import re
from datetime import datetime


def setup_logging(level=logging.INFO):
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )


def print_colored(text, color="green"):
    colors = {
        "red": "\033[91m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "reset": "\033[0m",
    }
    print(f"{colors.get(color, '')}{text}{colors['reset']}")


def resolve_safe_path(base_path, target_path):
    full_path = os.path.abspath(os.path.join(base_path, target_path))
    if not full_path.startswith(os.path.abspath(base_path)):
        raise ValueError("Unsafe path detected!")
    return full_path


def is_supported_os():
    return platform.system() in ["Linux", "Darwin", "Windows"]


# --- Suspicious Pattern Matcher ---
def detect_suspicious_patterns(code):
    suspicious_patterns = [
        r"base64\\.(b64decode|decode)",
        r"eval\\(",
        r"exec\\(",
        r"importlib\\.import_module",
        r"__import__",
        r"socket\\.",
        r"subprocess\\.",
        r"os\\.popen",
        r"pickle\\.loads",
        r"document.write",
        r"setTimeout\\(",
        r"while\\(1\\)",
        r"new XMLHttpRequest"
    ]
    results = []
    for pattern in suspicious_patterns:
        if re.search(pattern, code):
            results.append(pattern)
    return results


def classify_code_source(code):
    if re.search(r"openai|ai|autogen|copilot|generated", code, re.IGNORECASE):
        return "ai-generated"
    elif "// author:" in code or "/* author:" in code:
        return "hand-written"
    else:
        return "unknown"


# --- Entropy estimation for secret-like strings ---
def estimate_entropy(data):
    import math
    if not data:
        return 0
    frequency = {char: data.count(char) for char in set(data)}
    entropy = -sum((f / len(data)) * math.log2(f / len(data)) for f in frequency.values())
    return entropy


# --- Dangerous pattern blocker (optional use) ---
def block_if_dangerous(code, aggressive=False):
    findings = detect_suspicious_patterns(code)
    if aggressive and findings:
        raise RuntimeError("Blocked dangerous code pattern(s): " + ", ".join(findings))
    return findings


# --- Secret detection using regex (for passive alerts only) ---
def detect_possible_secrets(code):
    secret_patterns = [
        r"(token|secret|apikey|password)[\s:=]+[\"\']?[A-Za-z0-9_\-]{8,}[\"\']?",
        r"AIza[0-9A-Za-z\-_]{35}",
        r"sk_live_[0-9a-zA-Z]{24}"
    ]
    for pattern in secret_patterns:
        if re.search(pattern, code, re.IGNORECASE):
            return True
    return False


# --- Check for binary or invalid UTF-8 files ---
def is_code_text_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            f.read()
        return True
    except:
        return False


# --- Check for recently created files (possible temp exploits) ---
def is_file_too_recent(file_path, seconds=10):
    return (os.path.exists(file_path) and
            (datetime.now().timestamp() - os.path.getctime(file_path)) < seconds)


# --- Detect encoded or obfuscated payloads ---
def detect_obfuscated_strings(code, threshold=40):
    encoded_strings = re.findall(r"[A-Za-z0-9+/=]{%d,}" % threshold, code)
    return encoded_strings if encoded_strings else []


# --- Detect risky time-based behavior ---
def detect_timing_based_attacks(code):
    delay_patterns = [r"time\\.sleep", r"setTimeout", r"sleep\\(", r"while\\s*\(true\)"]
    return [pat for pat in delay_patterns if re.search(pat, code)]


# --- Check filename for suspicious naming ---
def flag_suspicious_filename(filename):
    keywords = ["bot", "inject", "exploit", "shell", "reverse", "backdoor"]
    return any(kw in filename.lower() for kw in keywords)
