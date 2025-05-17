# 🛡️ Nuvai Security Policy

🗓️ Version: 1.0 | Last updated: May 2025

Welcome to the security core of **Nuvai** –
a project where offensive mindset meets defensive discipline.

Built with the mindset of a penetration tester and the structure of ISO/IEC 27001, Nuvai is not just a code scanner – it's a commitment to secure, responsible development in the age of AI.

Nuvai is currently in active development (alpha stage). While designed with strict security principles, it is not yet production-hardened.

---

## 🔥 Our Security Philosophy

Security is not a feature. It's a foundation. From the first commit, we’ve taken a threat-driven approach:

* Detect vulnerabilities that AI-generated code may silently introduce
* Educate developers about real-world attack surfaces
* Integrate seamlessly into workflows without compromising security
* Comply with global standards (ISO, OWASP, NIST)

We know what attackers look for — because we think like them.

---

## 🧠 What We Secure (by Design)

✔️ Input validation and output sanitization in all modules
✔️ File uploads are scanned, isolated, and auto-cleaned
✔️ Logs are scrubbed of sensitive data (tokens, paths, secrets)
✔️ Reports avoid reflection or injection vectors (HTML-safe by default)
✔️ Language detection based on *content*, not just file extensions
✔️ Separation of analysis engine from frontend logic
✔️ CLI and API rate-limiting planned for future versions
✔️ Modular rule engine allows for controlled community contribution

📄 Our Threat Model: [docs/threat-model.md](./docs/threat-model.md) *(WIP)*

---

## 📢 Found a Vulnerability?

We deeply appreciate responsible disclosures.
Please **do not post issues publicly** before contacting us directly.

### 📬 Report privately to:

**📧 [elirandeeb@gmail.com](mailto:elirandeeb@gmail.com)**

Your report should include:

* A clear, concise summary of the issue
* Steps to reproduce (if applicable)
* Screenshots or logs (if safe to share)
* Your name or handle (if you'd like recognition)

⏱️ You’ll receive a response within **48 hours**, and if validated, we’ll patch within **7–10 business days**.

🔐 PGP key available upon request for encrypted vulnerability reports.

> Scope includes all code within this repository. Out-of-scope reports (e.g. test files, examples) may not qualify for acknowledgment.

---

## 🧷 Coordinated Disclosure

We follow a coordinated disclosure model:

1. You report the issue privately
2. We investigate and confirm it
3. You may get credited in our next release
4. We fix the issue and publish a secure update
5. Only then do we encourage public write-ups or blogs

> 🧠 Ethical researchers help us make Nuvai safer for everyone. If you contribute, you're part of the mission.

---

## 🧩 Security Standards We Align With

* ✅ [ISO/IEC 27001](https://www.iso.org/isoiec-27001-information-security.html)
* ✅ [OWASP Top 10](https://owasp.org/www-project-top-ten/)
* ✅ [NIST SP 800-218 – Secure Software Development Framework (SSDF) v1.1](https://csrc.nist.gov/publications/detail/sp/800-218/final)
* 🔄 Additional compliance support coming in future releases

---

## 👥 Maintainer Contact

**Eliran Loai Deeb**
Cybersecurity specialist, ethical hacker, and creator of Nuvai
📧 [elirandeeb@gmail.com](mailto:elirandeeb@gmail.com)
🌐 [https://github.com/tinkerlev/Nuvai](https://github.com/tinkerlev/Nuvai)

---

## 🚀 Final Note

If you're reading this, you're already part of the security community.
Whether you're a curious researcher, an ethical hacker, or just someone who wants to help — thank you.

Together, we build safer tools for a safer internet.
