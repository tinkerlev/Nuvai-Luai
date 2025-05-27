import re

class TypeScriptScanner:
    def __init__(self, code):
        self.code = code
        self.findings = []

    def run_all_checks(self):
        self.check_dangerous_eval()
        self.check_any_type_usage()
        self.check_unsanitized_input()
        self.check_hardcoded_secrets()
        self.check_insecure_requests()
        self.check_null_checks()
        self.check_unhandled_promises()
        self.check_insecure_storage()
        self.check_debug_statements()
        self.check_unvalidated_navigation()
        self.check_sensitive_comments()
        return self.findings

    def add_finding(self, level, ftype, message, recommendation):
        self.findings.append({
            "level": level,
            "type": ftype,
            "message": message,
            "recommendation": recommendation
        })

    def check_dangerous_eval(self):
        if re.search(r'(eval|new Function|setTimeout\s*\(\s*\")', self.code):
            self.add_finding("CRITICAL", "Dynamic Code Execution", "Use of eval, new Function or setTimeout with string detected.", "Avoid dynamic code. Use strict logic flow.")

    def check_any_type_usage(self):
        if re.search(r'\:\s*any\b|as\s+any\b', self.code):
            self.add_finding("WARNING", "Unsafe Typing", "TypeScript type 'any' used.", "Use explicit types to maintain type safety.")

    def check_unsanitized_input(self):
        if re.search(r'(document|window)\.(getElementById|getElementsByClassName|querySelector).*\.value', self.code):
            self.add_finding("HIGH", "Unsanitized DOM Input", "DOM input accessed without validation.", "Sanitize all user input before use.")

    def check_hardcoded_secrets(self):
        if re.search(r'(api|token|secret|key|password)\s*[:=]\s*["\']\w{8,}["\']', self.code, re.IGNORECASE):
            self.add_finding("HIGH", "Hardcoded Secret", "Detected secret/token directly in code.", "Move sensitive credentials to environment variables.")

    def check_insecure_requests(self):
        if re.search(r'(fetch|axios)\(\s*\"http:', self.code):
            self.add_finding("HIGH", "Insecure API Request", "HTTP request made without HTTPS.", "Always use secure HTTPS endpoints.")

    def check_null_checks(self):
        if re.search(r'\w+\.\w+\s*\(', self.code) and not re.search(r'\?\.', self.code):
            self.add_finding("MEDIUM", "Missing Optional Chaining", "Function/property accessed without null check.", "Use optional chaining or explicit validation.")

    def check_unhandled_promises(self):
        if re.search(r'\.then\(.*\)[^\.catch]', self.code):
            self.add_finding("WARNING", "Unhandled Promise Rejection", "Promise used without catch() or try/catch.", "Always handle promise errors explicitly.")

    def check_insecure_storage(self):
        if re.search(r'(localStorage|sessionStorage|document\.cookie)', self.code):
            self.add_finding("WARNING", "Insecure Storage Usage", "Sensitive data stored in browser storage.", "Avoid storing secrets in local/session storage.")

    def check_debug_statements(self):
        if re.search(r'console\.log|debugger', self.code):
            self.add_finding("INFO", "Debug Statement", "console.log/debugger detected in code.", "Remove debug statements before shipping code.")

    def check_unvalidated_navigation(self):
        if re.search(r'(window\.location|document\.referrer)\s*=\s*', self.code):
            self.add_finding("HIGH", "Unvalidated Redirect", "Detected assignment to navigation location.", "Avoid redirecting users based on untrusted input.")

    def check_sensitive_comments(self):
        if re.search(r'//.*(todo|password|debug)', self.code, re.IGNORECASE):
            self.add_finding("INFO", "Sensitive Comment", "Potentially sensitive comment in code.", "Remove leftover debug or password hints.")
