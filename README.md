# README.md

## 🔐 Welcome to Nuvai-Luai AI-Powered Secure Code Scanner
![CI Status](https://github.com/tinkerlev/nuvai/actions/workflows/ci.yml/badge.svg)

**Where AI meets precision, with the rigor of real-world penetration testing.**

Nuvai is an advanced static code analysis engine designed for both technical and non-technical users. It scans source code in multiple programming languages to detect vulnerabilities — especially in AI-generated, No-Code, and Low-Code environments.

---

## 🧠 What is Nuvai?
Nuvai automatically detects security flaws in your code using intelligent pattern recognition, code heuristics, and content-based detection.

It’s built with:
- 🔍 Deep code inspection logic
- 🔒 ISO/IEC 27001-aligned architecture
- 🧠 AI awareness and resilience against generated code patterns
- 📄 Professional-grade reporting

---

## 🚀 Features
- ✅ **Multi-language scanning:** Python, JavaScript, HTML, JSX, TypeScript, PHP, C++
- ⚠️ **Detects vulnerabilities:** Code injection, XSS, SSRF, insecure deserialization, hardcoded secrets, weak crypto, and more
- 📁 **Flexible reports:** JSON, TXT, HTML, and PDF
- 🧠 **AI-Aware:** Scans AI-generated or low-code scripts for critical flaws
- 💬 **Guided remediation tips** for every issue
- 🌐 **User-friendly Web UI** built in React
- 🖥️ **Works via CLI, GUI, or API**

---

## ✅ Continuous Integration (CI)

Every change is automatically tested with GitHub Actions:

- 🧪 **Backend tests** with `pytest`
- ⚛️ **Frontend tests** with `vitest` and React Testing Library

You can view test results directly on each pull request.

## 🗂️ Folder Structure
```bash
Nuvai/
├── assets/                        # Static images and branding assets
├── backend/                       # Flask backend for the API
│   ├── utils.py                   # Low-level helpers (e.g. extractors)
│   ├── update_init.py             # Auto-generation for missing __init__.py files
│   ├── scanner_controller.py      # Scan orchestration logic
│   └── tests/                     # Backend tests
│       ├── test_scan.py           # Valid file scan test
│       └── test_scan_empty_file.py # Empty, unsupported, insecure file tests
├── config/                        # (Planned) Centralized configuration
├── examples/                      # Sample vulnerable code snippets
├── frontend/                      # React-based frontend
│   ├── src/                       # Source code directory
│   │   ├── App.jsx                # Main App component
│   │   ├── index.css              # Global styles
│   │   ├── main.jsx               # Entry point for React DOM rendering
│   │   ├── api/                   # API client logic
│   │   │   ├── client.js          # Axios instance with defaults
│   │   │   └── scan.js            # Scan API call definition
│   │   ├── components/            # Reusable React components
│   │   │   └── FileUpload.jsx     # File upload handler UI
│   │   └── pages/                 # React page-level components
│   │       ├── Home.jsx           # Home page view
│   │       └── ScanResult.jsx     # Scan results renderer
│   └── __tests__/                 # Frontend test suite (Vitest)
│       └── App.test.jsx           # UI-level test for App component
├── src/                           # Core scanner engine
│   └── nuvai/                     # Language-specific scanners and utils
│       ├── scanner.py             # Main scan dispatcher
│       ├── scanner_controller.py  # Scan flow orchestrator
│       ├── cpp_scanner.py         # C++ analysis rules
│       ├── html_scanner.py        # HTML analysis rules
│       ├── javascript_scanner.py  # JS analysis rules
│       ├── jsx_scanner.py         # JSX rules
│       ├── php_scanner.py         # PHP rules
│       ├── python_scanner.py      # Python security checks
│       ├── typescript_scanner.py  # TypeScript rules
│       ├── utils.py               # Regex, entropy check, etc.
│       ├── report_saver.py        # Formats output as PDF/HTML/TXT
│       ├── config.py              # Severity and rule settings
│       └── logger.py              # Audit trail and log manager
├── run.py                         # CLI interface
├── server.py                      # Entry point for Flask API
├── install.sh                     # Installer script (cross-platform)
├── requirements.txt               # Python dependencies
├── docker-compose.yml             # Docker orchestration
├── Dockerfile                     # Backend Docker config
├── README.md
├── SECURITY.md                    # Security best practices
├── CONTRIBUTING.md                # Contribution guide
└── .gitignore                     # Git exclusions
```

---

## 🛠️ Getting Started
### Linux / WSL / Kali (recommended):
```bash
chmod +x install.sh
./install.sh
```

### Windows:
1. Install WSL or use Git Bash
2. Run:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install flask flask-cors
```

### macOS:
```bash
brew install python3
python3 -m venv .venv
source .venv/bin/activate
pip install flask flask-cors
```

### Web UI Setup
```bash
cd frontend
npm install && npm run dev
```

---

## 🧪 How to Run a Scan
### CLI Mode:
```bash
python3 run.py examples/vulnerable_app.py
```
Scan a full folder:
```bash
python3 run.py /path/to/codebase
```

### Web Mode:
```bash
source .venv/bin/activate
cd backend && python3 server.py
```
Then visit: [https://localhost:5173](https://localhost:5173)

---

## 📄 Report Formats
- `.json` — for APIs and automation
- `.html` — for browsers and documentation
- `.pdf` — for audits and clients
- `.txt` — for logs and fast review

Reports saved to: `~/security_reports/`

---

## 🔒 Built with Security in Mind (ISO/IEC 27001)
- ✔ Input validation + output encoding
- ✔ Temporary files are deleted after scan
- ✔ No user secrets or logs exposed
- ✔ Modular logging for audit readiness
- ✔ Supports offline and privacy-respecting usage

---

## 📍 Roadmap
- [x] Static engine with 7+ language scanners
- [x] Advanced PDF/HTML/JSON export
- [x] React frontend
- [ ] OAuth2 Login support (frontend/backend)
- [ ] Docker build + CI pipeline
- [ ] Plugin SDK for adding new rules
- [ ] Support SARIF/OWASP ZAP exports

---

## 🤝 Contribute
See [`CONTRIBUTING.md`](./CONTRIBUTING.md) for full instructions.
You can:
- Write rules and scanners
- Improve documentation or UI
- Report bugs and ideas

---

## 👨‍💻 Created by
**Eliran Loai Deeb**  
GitHub: [@tinkerlev](https://github.com/tinkerlev)  
LinkedIn: [linkedin.com/in/loai-deeb](https://www.linkedin.com/in/loai-deeb)

Want to support or collaborate? See [SPONSORSHIP.md](./SPONSORSHIP.md)

---

> Built with ❤️ for builders, red teamers, and ethical coders.

Stay secure. Stay smart. 🛡️
