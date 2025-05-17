
import re

class CppScanner:
    def __init__(self, code):
        self.code = code
        self.findings = []

    def run_all_checks(self):
        self.check_dangerous_functions()
        self.check_buffer_overflows()
        self.check_null_pointer_init()
        self.check_malloc_check()
        self.check_uninitialized_vars()
        self.check_infinite_loops()
        self.check_hardcoded_credentials()
        self.check_unsafe_file_access()
        self.check_insecure_macros()
        self.check_unsanitized_system()
        self.check_deprecated_calls()
        return self.findings

    def add_finding(self, level, ftype, message, recommendation):
        self.findings.append({
            "level": level,
            "type": ftype,
            "message": message,
            "recommendation": recommendation
        })

    def check_dangerous_functions(self):
        patterns = [r'\bgets\s*\(', r'\bstrcpy\s*\(', r'\bsprintf\s*\(', r'\bsystem\s*\(', r'\bpopen\s*\(']
        for pattern in patterns:
            if re.search(pattern, self.code):
                self.add_finding("CRITICAL", "Dangerous Function", f"Usage of dangerous function matching pattern: {pattern}", "Replace with safer alternatives like strncpy, snprintf, etc.")

    def check_buffer_overflows(self):
        if re.search(r'char\s+\w+\s*\[\s*\d+\s*\]\s*=\s*\".+\";', self.code):
            self.add_finding("HIGH", "Possible Buffer Overflow", "Potential buffer overflow in fixed-size character array.", "Use std::string or validate lengths before copying.")

    def check_null_pointer_init(self):
        if re.search(r'(int|char|void|float|double)\s*\*\s*\w+\s*=\s*NULL', self.code):
            self.add_finding("WARNING", "Unsafe Null Pointer", "Pointer initialized to NULL without safety guard.", "Ensure pointers are validated before dereferencing.")

    def check_malloc_check(self):
        if re.search(r'(malloc|calloc|realloc)\s*\(.*\)', self.code) and not re.search(r'if\s*\(.*!=\s*NULL\)', self.code):
            self.add_finding("HIGH", "Unchecked Memory Allocation", "Result of malloc/calloc not validated.", "Always check memory allocation results.")

    def check_uninitialized_vars(self):
        if re.search(r'(int|char|float|double)\s+\w+\s*;', self.code):
            self.add_finding("WARNING", "Uninitialized Variable", "Variable declared without initialization.", "Initialize all variables before usage.")

    def check_infinite_loops(self):
        if re.search(r'while\s*\(\s*1\s*\)', self.code):
            self.add_finding("MEDIUM", "Potential Infinite Loop", "Infinite loop without break condition.", "Ensure loop termination condition exists.")

    def check_hardcoded_credentials(self):
        if re.search(r'(user|pass|token|key)\s*=\s*\"\w{4,}\"', self.code):
            self.add_finding("HIGH", "Hardcoded Credentials", "Hardcoded credentials found in C++ code.", "Move credentials to secure config files or environment vars.")

    def check_unsafe_file_access(self):
        if re.search(r'fopen\s*\(\s*\w+', self.code) and re.search(r'argv|user|input', self.code):
            self.add_finding("HIGH", "User-Controlled File Access", "User input passed into fopen.", "Validate and sanitize file paths.")

    def check_insecure_macros(self):
        if re.search(r'#define\s+\w+\s+\d{4,}', self.code):
            self.add_finding("INFO", "Unsafe Macro Definition", "Potentially dangerous macro definition.", "Review macro usage and prefer constants.")

    def check_unsanitized_system(self):
        if re.search(r'system\s*\(\s*\w+\s*\)', self.code):
            self.add_finding("CRITICAL", "Unsanitized system() Call", "Raw system() used with unsanitized input.", "Avoid system() or validate command arguments.")

    def check_deprecated_calls(self):
        if re.search(r'gets\s*\(|bcopy\s*\(|index\s*\(', self.code):
            self.add_finding("WARNING", "Deprecated C Function", "Deprecated function call found.", "Use modern and safer C++ APIs.")
