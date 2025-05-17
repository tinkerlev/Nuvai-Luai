# File: run.py

"""
Description:
This is the main CLI entry point for the Nuvai static code analysis engine.
It allows users to scan a code file or an entire folder for vulnerabilities and export results in multiple formats.

Features:
- Accepts file or folder path input via command line
- Auto-detects code language by file extension or content
- Runs static analysis using language-specific modules
- Outputs clear terminal results and saves report to file
- Supports export formats: json, txt, html, pdf (auto fallback if PDF not available)
- Prompts user for export format and filename
- Provides contextual security improvement suggestions based on findings
- Handles unexpected input or format errors gracefully

Suitable for technical and non-technical users.
"""

import argparse
import os
from src.nuvai import get_language, scan_code
from src.nuvai.report_saver import save_report

SUPPORTED_EXTENSIONS = [".py", ".js", ".html", ".jsx", ".php", ".cpp", ".ts"]

def load_code(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"❌ Failed to load file: {e}")
        return None

def print_results(file_path, findings):
    print(f"\n📄 File: {file_path}")
    if not findings:
        print("✅ No issues found.")
        return

    print("\n🔍 Security Findings:")
    for f in findings:
        print(f"\n[{f['level']}] {f['type']}")
        print(f"- Description: {f['message']}")
        print(f"- Recommendation: {f['recommendation']}")

    # Derive dynamic improvement tips based on findings
    unique_tips = set()
    for f in findings:
        if "input" in f['message'].lower():
            unique_tips.add("Use input validation and sanitization wherever user input is accepted.")
        if "hardcoded" in f['message'].lower():
            unique_tips.add("Move hardcoded secrets to environment variables or secret managers.")
        if "debug" in f['message'].lower():
            unique_tips.add("Disable debug mode in production environments.")
        if "logging" in f['message'].lower():
            unique_tips.add("Avoid logging sensitive information like passwords or tokens.")

    if unique_tips:
        print("\n💡 Security Improvement Tips:")
        for tip in sorted(unique_tips):
            print(f"- {tip}")

def prompt_export_settings():
    print("\n💾 Export Report")
    format_choice = input("Select export format (json / txt / html / pdf): ").strip().lower()
    while format_choice not in ["json", "txt", "html", "pdf"]:
        format_choice = input("❗ Invalid format. Please choose from (json / txt / html / pdf): ").strip().lower()
    return format_choice

def process_file(file_path):
    code = load_code(file_path)
    if not code:
        return []
    language = get_language(file_path, code)
    if not language:
        print(f"❌ Skipping unsupported file: {file_path}")
        return []
    findings = scan_code(code, language)
    print_results(file_path, findings)
    return findings

def main():
    parser = argparse.ArgumentParser(description="Nuvai AI Code Security Scanner")
    parser.add_argument("target", help="Path to the code file or folder to scan")
    args = parser.parse_args()

    all_findings = []

    if os.path.isfile(args.target):
        findings = process_file(args.target)
        all_findings.extend(findings)

    elif os.path.isdir(args.target):
        for root, _, files in os.walk(args.target):
            for fname in files:
                if os.path.splitext(fname)[1].lower() in SUPPORTED_EXTENSIONS:
                    full_path = os.path.join(root, fname)
                    findings = process_file(full_path)
                    all_findings.extend(findings)
    else:
        print("❌ Invalid path. Please provide a valid file or folder.")
        return

    format_choice = prompt_export_settings()
    saved = save_report(all_findings, format_choice)
    if saved:
        print(f"\n📁 Report saved to: {saved}")

if __name__ == "__main__":
    main()
