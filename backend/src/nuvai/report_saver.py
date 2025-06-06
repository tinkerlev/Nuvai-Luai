# File: report_saver.py

import os
from datetime import datetime


def ensure_report_directory():
    home = os.path.expanduser("~")
    report_dir = os.path.join(home, "security_reports")
    os.makedirs(report_dir, exist_ok=True)
    return report_dir


def generate_filename(extension: str):
    date_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    return f"scanner_{date_str}.{extension}"


def save_report(findings, extension):
    report_dir = ensure_report_directory()
    filename = generate_filename(extension)
    full_path = os.path.join(report_dir, filename)

    if extension == "json":
        import json
        with open(full_path, "w", encoding="utf-8") as f:
            json.dump(findings, f, indent=4, ensure_ascii=False)

    elif extension == "txt":
        with open(full_path, "w", encoding="utf-8") as f:
            for fnd in findings:
                f.write(f"[{fnd['level']}] {fnd['type']}\n")
                f.write(f"- Description: {fnd['message']}\n")
                f.write(f"- Recommendation: {fnd['recommendation']}\n\n")

    elif extension == "html":
        with open(full_path, "w", encoding="utf-8") as f:
            f.write("<html><head><meta charset='UTF-8'><title>Scan Report</title>")
            f.write("<style>body { font-family: sans-serif; padding: 20px; } h2 { color: #B30000; }</style>")
            f.write("</head><body><h1>Nuvai Security Scan Report</h1>")
            for fnd in findings:
                f.write(f"<h2>[{fnd['level']}] {fnd['type']}</h2>")
                f.write(f"<p><strong>Description:</strong> {fnd['message']}</p>")
                f.write(f"<p><strong>Recommendation:</strong> {fnd['recommendation']}</p><hr>")
            f.write("</body></html>")

    elif extension == "pdf":
        try:
            from fpdf import FPDF
        except ImportError:
            print("⚠️ PDF export not available. To enable it, install fpdf using a virtual environment:")
            print("💡 Example: python3 -m venv .venv && source .venv/bin/activate && pip install fpdf")
            return None

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Nuvai Security Scan Report", ln=True, align="C")
        for fnd in findings:
            pdf.set_font("Arial", "B", 12)
            pdf.cell(200, 10, txt=f"[{fnd['level']}] {fnd['type']}", ln=True)
            pdf.set_font("Arial", size=11)
            pdf.multi_cell(0, 10, txt=f"Description: {fnd['message']}")
            pdf.multi_cell(0, 10, txt=f"Recommendation: {fnd['recommendation']}")
            pdf.ln()
        pdf.output(full_path)

    else:
        return None

    return full_path
