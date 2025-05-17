"""
File: jsx_scanner.py

Description:
This module scans JSX (JavaScript XML) code used in React applications to identify potential
security issues introduced through unsafe rendering, user input injection, and misconfigured
components. It is part of Nuvai's advanced static analysis engine.

Implemented Checks:
- Usage of dangerouslySetInnerHTML (XSS risk)
- Unescaped rendering of props and state
- Inline event handlers that may expose logic
- console.log or debugger statements in JSX
- Hardcoded secrets inside components
- Insecure use of localStorage/sessionStorage/cookies
- Missing key prop in array-rendered components
- Access to document/window in JSX logic
- Use of fetch or axios with HTTP instead of HTTPS
- Dynamic href/src/ref assignment
- Unescaped user input from props/state

Note: Regex-based JSX inspection. Parsing-based React support planned for future upgrades.
"""

import re

class JSXScanner:
    def __init__(self, code):
        self.code = code
        self.findings = []

    def run_all_checks(self):
        self.check_dangerously_set_inner_html()
        self.check_unescaped_props()
        self.check_inline_event_handlers()
        self.check_debug_statements()
        self.check_hardcoded_tokens()
        self.check_insecure_storage()
        self.check_missing_key_prop()
        self.check_insecure_dom_access()
        self.check_insecure_fetch()
        self.check_dynamic_attributes()
        self.check_user_input_reflection()
        return self.findings

    def add_finding(self, level, ftype, message, recommendation):
        self.findings.append({
            "level": level,
            "type": ftype,
            "message": message,
            "recommendation": recommendation
        })

    def check_dangerously_set_inner_html(self):
        if re.search(r'dangerouslySetInnerHTML\s*=\s*\{', self.code):
            self.add_finding("CRITICAL", "dangerouslySetInnerHTML", "Use of dangerouslySetInnerHTML detected.", "Avoid direct HTML injection. Sanitize inputs and use libraries like DOMPurify.")

    def check_unescaped_props(self):
        if re.search(r'\{\s*(props|this\.props|state|this\.state)\.[a-zA-Z0-9_]+\s*\}', self.code):
            self.add_finding("HIGH", "Unescaped Prop Rendering", "Unescaped prop/state rendered directly.", "Ensure user input is sanitized before rendering.")

    def check_inline_event_handlers(self):
        if re.search(r'on\w+\s*=\s*\{\s*\(.*\)\s*=>', self.code):
            self.add_finding("MEDIUM", "Inline Event Handler", "Arrow function used directly in JSX event handler.", "Extract event logic into named functions outside JSX.")

    def check_debug_statements(self):
        if re.search(r'console\.log|debugger', self.code):
            self.add_finding("INFO", "Debug Code Present", "console.log or debugger found.", "Remove debug statements before production.")

    def check_hardcoded_tokens(self):
        if re.search(r'(token|apiKey|secret)\s*[:=]\s*["\']\w{8,}["\']', self.code):
            self.add_finding("HIGH", "Hardcoded Secret", "Token or API key found in JSX component.", "Use .env variables or secure backend storage.")

    def check_insecure_storage(self):
        if re.search(r'(localStorage|sessionStorage|document\.cookie)', self.code):
            self.add_finding("WARNING", "Insecure Storage Access", "Direct access to browser storage detected.", "Avoid storing sensitive values in unprotected storage.")

    def check_missing_key_prop(self):
        if re.search(r'map\((\w+)\s*=>\s*<\w+', self.code) and not re.search(r'key\s*=\s*\{', self.code):
            self.add_finding("INFO", "Missing key Prop", "JSX array rendering missing key prop.", "Always assign a unique key when mapping lists.")

    def check_insecure_dom_access(self):
        if re.search(r'(document|window)\.(getElementById|getElementsByClassName|querySelector)', self.code):
            self.add_finding("WARNING", "Unsafe DOM Access", "DOM access via document/window detected.", "Use React refs or stateful logic instead.")

    def check_insecure_fetch(self):
        if re.search(r'(fetch|axios)\(\s*["\']http:', self.code):
            self.add_finding("HIGH", "Insecure API Request", "API request made over HTTP.", "Use only secure HTTPS endpoints.")

    def check_dynamic_attributes(self):
        if re.search(r'(href|src|ref)\s*=\s*\{\s*(props|state)', self.code):
            self.add_finding("HIGH", "Dynamic Attribute Injection", "Dynamic assignment to href/src/ref.", "Ensure these attributes are validated and sanitized.")

    def check_user_input_reflection(self):
        if re.search(r'\{\s*(user|data|input)\s*\}', self.code):
            self.add_finding("HIGH", "User Input Reflection", "User input rendered directly.", "Escape or sanitize all reflected user content.")
