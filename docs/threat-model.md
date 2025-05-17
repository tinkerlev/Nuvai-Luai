# 🧠 Nuvai – Threat Model (v1.0)

This document outlines the primary threat assumptions and mitigations guiding the design of **Nuvai**, our AI-enhanced vulnerability scanner. Threat modeling is an ongoing effort that evolves with the codebase.

---

## 🎯 Purpose

To identify, document, and prioritize potential threats to Nuvai's functionality, users, and infrastructure – especially in areas where untrusted code is processed.

---

## 🔐 Assets to Protect

* Uploaded code (user-submitted files)
* Internal scan logic and engine behavior
* Security reports and output data
* The Nuvai web interface and REST API
* Logs (especially if used for debugging or audits)

---

## ☠️ Threat Categories Considered

### 1. Malicious File Uploads

* Payloads attempting to exploit backend via file content
* Oversized files (DoS vectors)
* Unsupported file types posing parser risks

**Mitigation**:

* Max file size limit
* MIME type + content-based detection
* Scanning in isolated temp directories

### 2. Code Execution via Input

* Attempted remote code execution through embedded payloads in uploaded files
* Runtime evaluation vulnerabilities

**Mitigation**:

* No dynamic `eval` or execution of input
* Static-only scanning engine
* Strict parsing rules per language

### 3. Report Injection (XSS, HTML abuse)

* User-supplied code appearing unescaped in reports

**Mitigation**:

* Full HTML escaping in report templates
* No reflection of raw user input
* Output is rendered as plain text by default

### 4. API Abuse (future-proofing)

* Rate-limiting bypasses
* Abuse of batch scanning endpoints

**Planned Mitigations**:

* IP-based rate limiting
* User authentication layer (v2+)

### 5. Sensitive Data Exposure

* Logs or reports exposing API keys, secrets, paths

**Mitigation**:

* Log sanitization filters
* Masking of known token patterns

---

## 🛡️ Design Principles

* Principle of least privilege
* Separation of scanning logic from UI/API
* Fail-closed behavior for unsupported file types
* No execution or interpretation of user input

---

## 📌 Notes

This model will expand as Nuvai grows. Contributions are welcome via pull request or issue under `threat-model` label.

> Last updated: May 2025
