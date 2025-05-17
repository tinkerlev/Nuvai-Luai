"""
File: html_scanner.py

Description:
This module performs static analysis on HTML files to detect a wide range of client-side
security issues. It is part of Nuvai's advanced multi-language scanning system and targets
misconfigurations, injection opportunities, and design flaws that may expose an application
via its markup layer.

Implemented Checks:
- Inline <script> elements with embedded JavaScript
- Unsafe inline event handlers (onclick, onload, etc.)
- Missing CSRF tokens in <form> elements
- <input type="password"> fields lacking autocomplete="off"
- Links using target="_blank" without rel="noopener"
- Suspicious HTML comments (TODO, DEBUG, passwords, etc.)
- Disclosure of sensitive paths, subdomains, IPs, emails, usernames
- Forms missing or using insecure action attributes (HTTP/external domains)
- Insecure <iframe> elements (missing sandbox, allow, referrerpolicy)
- Missing <meta http-equiv="Content-Security-Policy">
- Dangerous hidden inputs and external JavaScript sources
- Forms with no method or no encoding type
- Insecure autocomplete in other sensitive inputs (credit card, email)

Note: Regex-based scanner. DOM-aware parsing planned for future versions.
"""

import re

class HTMLScanner:
    def __init__(self, code):
        self.code = code
        self.findings = []

    def run_all_checks(self):
        self.check_inline_scripts()
        self.check_event_handlers()
        self.check_csrf_token()
        self.check_password_autocomplete()
        self.check_blank_target_links()
        self.check_suspicious_comments()
        self.check_sensitive_disclosures()
        self.check_insecure_form_actions()
        self.check_iframe_security()
        self.check_missing_csp_meta()
        self.check_hidden_inputs_or_external_js()
        self.check_form_encoding_and_method()
        self.check_autocomplete_on_inputs()
        return self.findings

    def add_finding(self, level, ftype, message, recommendation):
        self.findings.append({
            "level": level,
            "type": ftype,
            "message": message,
            "recommendation": recommendation
        })

    def check_inline_scripts(self):
        if re.search(r'<script[^>]*>[^<]+</script>', self.code, re.IGNORECASE):
            self.add_finding("HIGH", "Inline Script Detected", "Inline JavaScript block found.", "Use external scripts and implement CSP to block inline scripts.")

    def check_event_handlers(self):
        if re.search(r'on(click|load|error|input|submit)\s*=\s*"', self.code, re.IGNORECASE):
            self.add_finding("HIGH", "Inline Event Handler", "Detected unsafe inline JavaScript event attribute.", "Move event logic to scripts or external handlers.")

    def check_csrf_token(self):
        if re.search(r'<form[^>]*>', self.code) and not re.search(r'csrf', self.code, re.IGNORECASE):
            self.add_finding("WARNING", "Missing CSRF Token", "Form detected without a CSRF token.", "Implement CSRF protection via hidden input tokens.")

    def check_password_autocomplete(self):
        if re.search(r'<input[^>]*type="password"[^>]*>', self.code, re.IGNORECASE) and not re.search(r'autocomplete\s*=\s*"off"', self.code):
            self.add_finding("INFO", "Password Autocomplete Enabled", "Password input does not disable autocomplete.", "Use autocomplete=\"off\" for password fields.")

    def check_blank_target_links(self):
        if re.search(r'<a[^>]*target="_blank"[^>]*>', self.code) and not re.search(r'rel\s*=\s*"noopener"', self.code):
            self.add_finding("INFO", "Target _blank Missing Noopener", "_blank link missing rel=\"noopener\".", "Always use rel=\"noopener\" with target=\"_blank\".")

    def check_suspicious_comments(self):
        if re.search(r'<!--.*(TODO|FIXME|DEBUG|password).*-->', self.code, re.IGNORECASE):
            self.add_finding("INFO", "Suspicious HTML Comment", "Found development-related or sensitive comment.", "Remove all sensitive or debug-related comments before deployment.")

    def check_sensitive_disclosures(self):
        patterns = [r'/etc/', r'\buser(name)?\b', r'admin', r'\b[A-Za-z0-9_.-]+@[A-Za-z0-9_.-]+\.[a-z]+\b', r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b']
        for pattern in patterns:
            if re.search(pattern, self.code):
                self.add_finding("WARNING", "Sensitive Information Leak", f"Pattern found: {pattern}", "Review and scrub sensitive references from HTML.")

    def check_insecure_form_actions(self):
        if re.search(r'<form[^>]*action\s*=\s*"http:', self.code):
            self.add_finding("HIGH", "Insecure Form Action", "Form submits over HTTP.", "Use HTTPS for all form submissions.")
        if re.search(r'<form[^>]*action\s*=\s*"https?://[^>]+"', self.code) and not re.search(r'yourdomain\.com', self.code):
            self.add_finding("MEDIUM", "External Form Submission", "Form action points to external domain.", "Avoid submitting sensitive data to 3rd-party endpoints.")

    def check_iframe_security(self):
        if re.search(r'<iframe[^>]*>', self.code) and not re.search(r'sandbox|referrerpolicy|allow', self.code):
            self.add_finding("WARNING", "Unprotected Iframe", "<iframe> is missing important security attributes.", "Add sandbox and referrerpolicy attributes to all iframes.")

    def check_missing_csp_meta(self):
        if not re.search(r'<meta[^>]*http-equiv="Content-Security-Policy"', self.code, re.IGNORECASE):
            self.add_finding("INFO", "Missing CSP Meta Tag", "Content Security Policy meta tag not found.", "Define CSP using <meta> or server headers.")

    def check_hidden_inputs_or_external_js(self):
        if re.search(r'<input[^>]*type="hidden"[^>]*value="[^"]{20,}"', self.code):
            self.add_finding("WARNING", "Sensitive Hidden Input", "Hidden field contains long static value.", "Move sensitive tokens server-side.")
        if re.search(r'<script[^>]*src="http:', self.code):
            self.add_finding("HIGH", "Insecure External JS", "External JavaScript loaded over HTTP.", "Use HTTPS or host scripts locally.")

    def check_form_encoding_and_method(self):
        if re.search(r'<form[^>]*>', self.code):
            if not re.search(r'method\s*=\s*"(post|get)"', self.code):
                self.add_finding("INFO", "Form Method Missing", "Form does not specify GET or POST method.", "Define method attribute explicitly.")
            if not re.search(r'enctype\s*=\s*"', self.code):
                self.add_finding("INFO", "Form Encoding Missing", "Form lacks enctype attribute.", "Use enctype for file uploads or proper MIME handling.")

    def check_autocomplete_on_inputs(self):
        if re.search(r'<input[^>]+(credit|card|email|address)[^>]+>', self.code, re.IGNORECASE) and not re.search(r'autocomplete\s*=\s*"off"', self.code):
            self.add_finding("INFO", "Sensitive Input With Autocomplete", "Sensitive form field allows autocomplete.", "Use autocomplete=\"off\" on inputs for PII or financial data.")
