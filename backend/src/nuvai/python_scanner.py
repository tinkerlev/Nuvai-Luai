"""
File: python_scanner.py

Description:
This module performs static security analysis on Python source code.
It is part of Nuvai's multi-language vulnerability engine, focusing on detecting high-risk coding patterns
commonly introduced by AI tools, no-code platforms, or inexperienced developers.

Implemented Checks:
- eval/exec usage
- OS command injection (os.system)
- Template injection (Jinja2, etc)
- Unescaped HTML (XSS)
- Hardcoded secrets (passwords, API keys)
- Debug mode enabled in Flask/Django
- Insecure deserialization (pickle)
- SSRF via requests.get with user input
- Path traversal via open("../...")
- Weak hashes (MD5, SHA1)
- Use of input() without sanitization
- JWT verification disabled
- Sensitive data in logs (password/token/secret)
- Dangerous or unreviewed comments (TODO, FIXME, password)
- Suspicious paths, config files, or .env leaks
- use of wildcard imports (import *)
- debugging artifacts (print, pdb.set_trace)
- use of insecure modules (telnetlib, http.client, etc)

Note: Regex-based scanning for speed. Future versions may include AST-based logic.
"""

import re

class PythonScanner:
    def __init__(self, code):
        self.code = code
        self.findings = []

    def run_all_checks(self):
        self.check_eval_exec()
        self.check_command_injection()
        self.check_template_injection()
        self.check_xss()
        self.check_hardcoded_secrets()
        self.check_debug_mode()
        self.check_pickle_usage()
        self.check_ssrf_patterns()
        self.check_path_traversal()
        self.check_weak_hashes()
        self.check_raw_input()
        self.check_insecure_jwt()
        self.check_sensitive_logging()
        self.check_unreviewed_comments()
        self.check_exposed_internal_paths()
        self.check_wildcard_imports()
        self.check_debug_artifacts()
        self.check_insecure_modules()
        return self.findings

    def add_finding(self, level, ftype, message, recommendation):
        self.findings.append({
            "level": level,
            "type": ftype,
            "message": message,
            "recommendation": recommendation
        })

    def check_eval_exec(self):
        if re.search(r'\b(eval|exec)\s*\(', self.code):
            self.add_finding("CRITICAL", "Dynamic Code Execution", "Use of eval() or exec() can lead to arbitrary code execution.", "Avoid using eval/exec. Use safer alternatives like literal_eval or dictionaries.")

    def check_command_injection(self):
        if re.search(r'os\.system\s*\(', self.code):
            self.add_finding("CRITICAL", "OS Command Injection", "Use of os.system with input can allow shell injection.", "Use subprocess.run with argument arrays and input sanitization.")

    def check_template_injection(self):
        if re.search(r'render_template\(.+\)', self.code) and "request" in self.code:
            self.add_finding("WARNING", "Template Injection Risk", "Template rendering may use unescaped user input.", "Ensure Jinja templates escape variables by default, or sanitize input manually.")

    def check_xss(self):
        if re.search(r'<script>|document\.write\s*\(', self.code):
            self.add_finding("WARNING", "XSS-like Output", "Detected potentially unsafe JavaScript in output.", "Ensure output is properly escaped when generating HTML.")

    def check_hardcoded_secrets(self):
        if re.search(r'(api|token|secret|key|password)\s*[:=]\s*["\']\w{6,}["\']', self.code, re.IGNORECASE):
            self.add_finding("HIGH", "Hardcoded Secrets", "Credentials or tokens appear to be hardcoded in code.", "Move all secrets to environment variables or a secure vault.")

    def check_debug_mode(self):
        if re.search(r'DEBUG\s*=\s*True', self.code) or 'app.config["DEBUG"] = True' in self.code:
            self.add_finding("INFO", "Debug Mode Enabled", "Debug mode is active. May leak internal details in production.", "Disable debug mode in production environments.")

    def check_pickle_usage(self):
        if re.search(r'pickle\.(load|loads)\s*\(', self.code):
            self.add_finding("CRITICAL", "Insecure Deserialization", "Pickle deserialization allows remote code execution if input is untrusted.", "Avoid pickle. Use safer formats like JSON for untrusted input.")

    def check_ssrf_patterns(self):
        if re.search(r'requests\.get\s*\(.*\)', self.code) and re.search(r'input\(', self.code):
            self.add_finding("HIGH", "Potential SSRF", "requests.get using unsanitized input can allow server-side request forgery.", "Validate URLs and restrict internal IPs or schemes.")

    def check_path_traversal(self):
        if re.search(r'open\s*\(.*\.\./', self.code):
            self.add_finding("CRITICAL", "Path Traversal Risk", "File access using relative '../' paths can expose sensitive files.", "Validate and sanitize file paths. Use pathlib where possible.")

    def check_weak_hashes(self):
        if re.search(r'(md5|sha1)\s*\(', self.code):
            self.add_finding("MEDIUM", "Weak Hash Function", "MD5 and SHA1 are insecure and susceptible to collisions.", "Use SHA-256 or stronger algorithms.")

    def check_raw_input(self):
        if re.search(r'\binput\s*\(', self.code):
            self.add_finding("MEDIUM", "Unvalidated User Input", "Use of input() without validation may lead to logic bugs or injection.", "Always validate and sanitize user input.")

    def check_insecure_jwt(self):
        if 'jwt.decode' in self.code and 'verify=False' in self.code:
            self.add_finding("HIGH", "Insecure JWT Handling", "JWT decoding is performed with verification turned off.", "Always verify JWT tokens in production.")

    def check_sensitive_logging(self):
        if re.search(r'logging\.\w+\s*\([^)]*(password|token|secret)', self.code, re.IGNORECASE):
            self.add_finding("WARNING", "Sensitive Data in Logs", "Logging statements may leak sensitive values.", "Avoid logging secrets, or mask them before logging.")

    def check_unreviewed_comments(self):
        if re.search(r'#\s*(TODO|FIXME|DEBUG|HACK|password)', self.code, re.IGNORECASE):
            self.add_finding("INFO", "Suspicious Comment", "Comment in code suggests incomplete or insecure logic.", "Review and clean up TODOs or sensitive comments.")

    def check_exposed_internal_paths(self):
        if re.search(r'\b(/etc/|/home/|\\\\|\\|credentials.json|\.env)\b', self.code):
            self.add_finding("MEDIUM", "Exposed System Path", "Sensitive or system-related paths detected.", "Avoid referencing internal or absolute paths directly in code.")

    def check_wildcard_imports(self):
        if re.search(r'import \*|from .* import \*', self.code):
            self.add_finding("WARNING", "Wildcard Import", "Using wildcard imports can lead to namespace collisions.", "Import specific components explicitly.")

    def check_debug_artifacts(self):
        if re.search(r'pdb\.set_trace\(\)|print\(', self.code):
            self.add_finding("INFO", "Debugging Artifact", "Code contains print statements or debugging breakpoints.", "Remove or disable debugging lines before production.")

    def check_insecure_modules(self):
        if re.search(r'import\s+(telnetlib|smtplib|http\.client)', self.code):
            self.add_finding("WARNING", "Insecure Module Usage", "Detected usage of insecure or unencrypted modules.", "Use secure alternatives such as HTTPS libraries or encrypted protocols.")
