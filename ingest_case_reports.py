#!/usr/bin/env python3
"""
Ingest open-access case reports (PDF/HTML/TXT) and extract anesthesia-relevant insights.

Usage:
  python ingest_case_reports.py --input_dir "/path/to/case_reports" --output_dir "case_report_insights"
  # If --input_dir is omitted, the script tries:
  #   1) CASE_REPORTS_DIR environment variable
  #   2) ./case_reports directory
  #   3) interactive prompt for a directory

Optional:
  --glob "*.pdf"  # restrict to certain files

Dependencies:
  - Core: standard library only
  - Optional for better extraction:
      pip install pypdf beautifulsoup4
"""

import os
import sys
import json
import argparse
import glob as globlib
from typing import Optional


def read_text_file(file_path: str) -> str:
    with open(file_path, 'r', errors='ignore') as f:
        return f.read()


def extract_text_from_pdf(file_path: str) -> Optional[str]:
    # Try pypdf first (lightweight and simple)
    try:
        from pypdf import PdfReader  # type: ignore
        reader = PdfReader(file_path)
        pages_text = []
        for page in reader.pages:
            page_text = page.extract_text() or ""
            pages_text.append(page_text)
        text = "\n".join(pages_text)
        if text.strip():
            return text
    except Exception:
        pass

    # Fallback: try pdfminer.six if available
    try:
        from pdfminer.high_level import extract_text  # type: ignore
        text = extract_text(file_path) or ""
        if text.strip():
            return text
    except Exception:
        pass

    return None


def extract_text_from_html(file_path: str) -> Optional[str]:
    # Prefer BeautifulSoup if available
    try:
        from bs4 import BeautifulSoup  # type: ignore
        with open(file_path, 'r', errors='ignore') as f:
            soup = BeautifulSoup(f, 'html.parser')
        # Remove script/style
        for tag in soup(["script", "style"]):
            tag.extract()
        text = soup.get_text(separator="\n")
        return text
    except Exception:
        pass

    # Minimal fallback: naive tag strip
    try:
        import re
        html = read_text_file(file_path)
        text = re.sub(r"<[^>]+>", " ", html)
        return text
    except Exception:
        return None


def clean_text(raw_text: str) -> str:
    # Basic cleanup: collapse whitespace and trim
    import re
    text = raw_text.replace("\r", "\n")
    text = re.sub(r"\n\s*\n\s*\n+", "\n\n", text)  # limit consecutive blank lines
    text = re.sub(r"\t+", " ", text)

    # Heuristic: down-weight references section for case reports
    # If a 'References' section exists near the end, truncate from there (optional)
    lower = text.lower()
    idx = lower.rfind("\nreferences")
    if idx != -1 and idx > len(text) * 0.6:  # only if it appears in the last 40% of the doc
        text = text[:idx].strip()

    return text.strip()


def extract_text_generic(file_path: str) -> Optional[str]:
    ext = os.path.splitext(file_path)[1].lower()
    if ext in [".txt", ".text"]:
        return read_text_file(file_path)
    if ext == ".pdf":
        return extract_text_from_pdf(file_path)
    if ext in [".html", ".htm"]:
        return extract_text_from_html(file_path)
    # Unknown type: try reading as text
    try:
        return read_text_file(file_path)
    except Exception:
        return None


def process_text_with_bot(text: str) -> dict:
    from clinical_insight_bot import ClinicalInsightBot
    bot = ClinicalInsightBot()
    return bot.process_emr_text(text)


def main():
    parser = argparse.ArgumentParser(description="Ingest case reports and extract anesthesia insights")
    parser.add_argument("--input_dir", required=False, help="Directory containing case report files (PDF/HTML/TXT)")
    parser.add_argument("--output_dir", default="case_report_insights", help="Directory to write JSON outputs")
    parser.add_argument("--glob", default="*", help="Glob pattern to select files (e.g., '*.pdf')")
    args = parser.parse_args()

    input_dir = args.input_dir
    if not input_dir:
        # Try environment variable
        input_dir = os.environ.get("CASE_REPORTS_DIR")
    if not input_dir:
        # Try default ./case_reports
        default_dir = os.path.abspath(os.path.join(os.getcwd(), "case_reports"))
        if os.path.isdir(default_dir):
            input_dir = default_dir
    if not input_dir:
        # Interactive prompt
        print("--input_dir not provided. You can set CASE_REPORTS_DIR env var or enter a directory now.")
        user_dir = input("Enter path to directory with case reports (or press Enter to cancel): ").strip()
        if not user_dir:
            print("No input directory provided. Example usage:\n  python ingest_case_reports.py --input_dir '/path/to/case_reports' --glob '*.pdf'")
            sys.exit(2)
        input_dir = user_dir

    input_dir = os.path.abspath(input_dir)
    output_dir = os.path.abspath(args.output_dir)
    os.makedirs(output_dir, exist_ok=True)

    pattern = os.path.join(input_dir, args.glob)
    file_paths = [p for p in globlib.glob(pattern) if os.path.isfile(p)]
    if not file_paths:
        print(f"No files found with pattern: {pattern}")
        sys.exit(1)

    print(f"Found {len(file_paths)} file(s). Processing...\n")
    failures = []

    for file_path in file_paths:
        base = os.path.basename(file_path)
        stem, _ = os.path.splitext(base)
        out_json = os.path.join(output_dir, f"{stem}.json")

        try:
            raw = extract_text_generic(file_path)
            if not raw or not raw.strip():
                print(f"[skip] Could not extract text: {base}")
                failures.append((base, "text_extraction_failed"))
                continue

            text = clean_text(raw)
            insights = process_text_with_bot(text)

            with open(out_json, 'w') as f:
                json.dump(insights, f, indent=2)

            print(f"[ok] {base} -> {out_json}")

        except Exception as e:
            print(f"[err] {base}: {e}")
            failures.append((base, str(e)))

    if failures:
        print("\nCompleted with some errors:")
        for name, reason in failures:
            print(f"  - {name}: {reason}")
        # Guidance for missing deps
        print("\nIf PDF/HTML extraction failed, try:\n  pip install pypdf beautifulsoup4\n")
    else:
        print("\nAll files processed successfully.")


if __name__ == "__main__":
    main()


