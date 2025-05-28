"""
File: javascript_scanner.py

Description:
This module scans raw JavaScript code for security flaws using static analysis and pattern
recognition. It is part of Nuvai's advanced multi-language scanning engine and focuses on
client-side logic issues, injection risks, data exposure, and unsafe API practices – all
of which are common in AI-generated and no-code JS codebases.

Implemented Checks:
- Dangerous function usage (eval, Function, setTimeout with string)
- DOM-based XSS (innerHTML, outerHTML, document.write)
- Insecure storage access (localStorage, sessionStorage, document.cookie)
- Hardcoded secrets (keys, tokens, passwords)
- Debug statements (console.log, debugger)
- Insecure HTTP API calls
- Direct access to URL params without sanitization
- Use of XMLHttpRequest without proper CORS/security headers
- Insecure assignments to location.href or window.name
- Missing validation on user-generated content

Note: Regex-based detection. Future updates may incorporate AST-based analysis.
"""

import re

class JavaScriptScanner:
    def __init__(self, code):
        self.code = code
        self.findings = []

    def run_all_checks(self):
        self.check_dangerous_eval()
        self.check_dom_xss()
        self.check_insecure_storage()
        self.check_hardcoded_secrets()
        self.check_debug_statements()
        self.check_insecure_http()
        self.check_unsanitized_url_params()
        self.check_xmlhttp_request()
        self.check_unprotected_navigation()
        self.check_unvalidated_user_content()
        return self.findings

    def add_finding(self, level, ftype, message, recommendation):
        self.findings.append({
            "level": level,
            "type": ftype,
            "message": message,
            "recommendation": recommendation
        })

    def check_dangerous_eval(self):
        if re.search(r'\b(eval|Function|setTimeout|setInterval)\s*\(', self.code):
            self.add_finding("CRITICAL", "Dynamic Code Execution", "Use of eval or similar constructs detected.", "Avoid dynamic code execution. Use strict logic paths.")

    def check_dom_xss(self):
        if re.search(r'(innerHTML|outerHTML|document\.write)', self.code):
            self.add_finding("HIGH", "DOM-based XSS", "Direct DOM manipulation using unsanitized data.", "Avoid setting HTML using user input. Sanitize all dynamic content.")

    def check_insecure_storage(self):
        if re.search(r'(localStorage|sessionStorage|document\.cookie)', self.code):
            self.add_finding("WARNING", "Insecure Storage Usage", "Sensitive data accessed from browser storage.", "Avoid using local/session storage or cookies for secrets.")

    def check_hardcoded_secrets(self):
        if re.search(r'(api|token|secret|key|password)\s*[:=]\s*["\']\w{8,}["\']', self.code, re.IGNORECASE):
            self.add_finding("HIGH", "Hardcoded Secret", "Sensitive key or token found in source code.", "Store secrets in secure backend or config files.")

    def check_debug_statements(self):
        if re.search(r'(console\.log|debugger)', self.code):
            self.add_finding("INFO", "Debug Statement Detected", "Debugging code found.", "Remove console.log or debugger statements before production")

    def check_insecure_http(self):
        if re.search(r'fetch\("http:|axios\.get\("http:', self.code):
            self.add_finding("HIGH", "Insecure HTTP Request", "HTTP connection used instead of HTTPS.", "Use secure HTTPS URLs for all network requests.")

    def check_unsanitized_url_params(self):
        if re.search(r'location\.search|URLSearchParams', self.code) and not re.search(r'sanitize|encode', self.code):
            self.add_finding("HIGH", "Unsanitized URL Parameter", "Use of URL parameters without validation.", "Validate or sanitize user input from URLs.")

    def check_xmlhttp_request(self):
        if re.search(r'new\s+XMLHttpRequest\(\)', self.code):
            self.add_finding("WARNING", "Unrestricted XMLHttpRequest", "Raw XHR usage found.", "Use fetch() with proper CORS and security headers.")

    def check_unprotected_navigation(self):
        if re.search(r'(location\.href|window\.name)\s*=\s*', self.code):
            self.add_finding("MEDIUM", "Uncontrolled Redirect", "URL redirection logic found.", "Avoid assigning user input to location.href or window.name.")

    def check_unvalidated_user_content(self):
        if re.search(r'(userInput|userData|data)\s*[:=]', self.code) and re.search(r'(innerHTML|document\.write)', self.code):
            self.add_finding("HIGH", "Unvalidated User Content", "Untrusted data written directly to DOM.", "Escape or sanitize all user-generated content.")
