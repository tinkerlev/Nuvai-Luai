"""
File: php_scanner.py

Description:
This module scans PHP source code for critical security vulnerabilities. As part of Nuvai's
multi-language static analysis engine, it is designed to detect risky coding patterns
in PHP-based applications – including those created via AI or no-code platforms.

Implemented Checks:
- Dangerous function usage (eval, system, exec, passthru, shell_exec, popen)
- SQL injection via unsanitized $_GET/$_POST/$_REQUEST
- Reflected XSS using echo/print of user input
- File inclusion attacks (LFI/RFI)
- Hardcoded credentials (database user/pass)
- Error reporting enabled in production
- Missing session_regenerate_id after login
- Insecure file uploads ($_FILES)
- Weak hashing (md5, sha1)
- CSRF protection missing in forms
- Insecure random number generators (rand, mt_rand)
- PHP version exposure via headers
- Cookie flags missing (HttpOnly, Secure)
- Superglobals passed into output logic

Note: Regex-based pattern matching – not full AST parsing.
"""

import re

class PHPScanner:
    def __init__(self, code):
        self.code = code
        self.findings = []

    def run_all_checks(self):
        self.check_eval_system()
        self.check_sql_injection()
        self.check_xss_echo()
        self.check_file_inclusion()
        self.check_hardcoded_credentials()
        self.check_error_reporting()
        self.check_session_regeneration()
        self.check_file_uploads()
        self.check_weak_hashing()
        self.check_csrf_protection()
        self.check_insecure_random()
        self.check_php_version_exposure()
        self.check_insecure_cookies()
        self.check_raw_superglobal_output()
        return self.findings

    def add_finding(self, level, ftype, message, recommendation):
        self.findings.append({
            "level": level,
            "type": ftype,
            "message": message,
            "recommendation": recommendation
        })

    def check_eval_system(self):
        if re.search(r'\b(eval|system|exec|passthru|shell_exec|popen)\s*\(', self.code):
            self.add_finding("CRITICAL", "Dangerous Function Execution", "Use of insecure function: eval/system/etc.", "Avoid dangerous functions. Use safer abstractions or escape/sanitize input.")

    def check_sql_injection(self):
        if re.search(r'\$_(GET|POST|REQUEST).*\.(SELECT|INSERT|UPDATE|DELETE)', self.code, re.IGNORECASE):
            self.add_finding("HIGH", "Possible SQL Injection", "Unsanitized user input detected in SQL query.", "Use PDO/MySQLi with prepared statements.")

    def check_xss_echo(self):
        if re.search(r'(echo|print)\s*\$_(GET|POST|REQUEST|COOKIE)', self.code):
            self.add_finding("HIGH", "Reflected XSS", "User input directly echoed without encoding.", "Escape output with htmlspecialchars().")

    def check_file_inclusion(self):
        if re.search(r'(include|require|include_once|require_once)\s*\(\s*\$_(GET|POST|REQUEST)', self.code):
            self.add_finding("HIGH", "File Inclusion", "File path dynamically included from user input.", "Avoid dynamic file inclusion. Use whitelisting.")

    def check_hardcoded_credentials(self):
        if re.search(r'(host|user|pass|dbname)\s*=\s*["\']\w+["\']', self.code, re.IGNORECASE):
            self.add_finding("HIGH", "Hardcoded Credentials", "Database credentials found in code.", "Use environment config files outside web root.")

    def check_error_reporting(self):
        if re.search(r'error_reporting\s*\(', self.code):
            self.add_finding("INFO", "Error Reporting Enabled", "PHP error reporting is active.", "Disable error reporting on production servers.")

    def check_session_regeneration(self):
        if 'session_start()' in self.code and 'session_regenerate_id' not in self.code:
            self.add_finding("WARNING", "Session Fixation Risk", "Session not regenerated after login.", "Call session_regenerate_id(true) after authentication.")

    def check_file_uploads(self):
        if re.search(r'\$_FILES\[.+\]', self.code) and not re.search(r'(mime_content_type|finfo_open|pathinfo)', self.code):
            self.add_finding("HIGH", "Unvalidated File Upload", "File upload found without validation.", "Check MIME type and store uploaded files outside webroot.")

    def check_weak_hashing(self):
        if re.search(r'(md5|sha1)\s*\(', self.code):
            self.add_finding("MEDIUM", "Weak Hash Algorithm", "Use of insecure hash function.", "Use password_hash() or SHA-256/SHA-512.")

    def check_csrf_protection(self):
        if re.search(r'<form', self.code) and not re.search(r'csrf_token', self.code, re.IGNORECASE):
            self.add_finding("WARNING", "Missing CSRF Token", "Form missing CSRF protection.", "Add CSRF token hidden field and validate it server-side.")

    def check_insecure_random(self):
        if re.search(r'\b(rand|mt_rand)\s*\(', self.code):
            self.add_finding("WARNING", "Insecure Random Generator", "Use of rand() or mt_rand() is insecure.", "Use random_int() or openssl_random_pseudo_bytes().")

    def check_php_version_exposure(self):
        if re.search(r'header\s*\(\s*"X-Powered-By:\s*PHP', self.code, re.IGNORECASE):
            self.add_finding("INFO", "PHP Version Disclosure", "PHP version exposed in HTTP headers.", "Disable expose_php in php.ini.")

    def check_insecure_cookies(self):
        if re.search(r'setcookie\s*\(', self.code) and not re.search(r'(HttpOnly|Secure)', self.code):
            self.add_finding("WARNING", "Insecure Cookie", "Cookies missing Secure or HttpOnly flags.", "Set flags to protect cookies from theft.")

    def check_raw_superglobal_output(self):
        if re.search(r'\$_(GET|POST|REQUEST|COOKIE|SERVER)\s*;', self.code):
            self.add_finding("MEDIUM", "Raw Superglobal Output", "Superglobal used without sanitization.", "Always validate and escape superglobal values.")
