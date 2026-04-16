#!/usr/bin/env python3
import argparse
import re
import sys
from pathlib import Path

import fitz


def find_project_root() -> Path:
    current = Path(__file__).resolve().parent
    while current != current.parent:
        if (current / ".git").is_dir():
            return current
        current = current.parent
    return Path(__file__).resolve().parent.parent


def discover_pdfs(directory: Path) -> list[Path]:
    pdfs = sorted(
        p for p in directory.rglob("*") if p.is_file() and p.suffix.lower() == ".pdf"
    )
    return pdfs


def should_skip(doc: fitz.Document) -> tuple[bool, str]:
    total_images = sum(len(page.get_images(full=True)) for page in doc)
    if total_images > 0:
        return (True, "images")
    total_chars = sum(len(page.get_text("text")) for page in doc)
    if total_chars == 0:
        return (True, "no text")
    return (False, "")


def extract_text_as_markdown(doc: fitz.Document) -> str:
    pages_text = []
    for page in doc:
        pages_text.append(page.get_text("text").rstrip())

    if len(pages_text) == 1:
        return pages_text[0] + "\n"

    parts = []
    for i, text in enumerate(pages_text, 1):
        if i == 1:
            parts.append(f"## Page {i}\n\n{text}")
        else:
            parts.append(f"---\n## Page {i}\n\n{text}")
    return "\n".join(parts) + "\n"


def format_code_blocks(text: str) -> str:
    lines = text.split("\n")
    result: list[str] = []
    block: list[str] = []

    def is_tabular(line: str) -> bool:
        gaps = re.findall(r"  +", line)
        return len(gaps) >= 2

    def flush_block():
        if len(block) >= 3:
            result.append("```")
            result.extend(block)
            result.append("```")
        else:
            result.extend(block)
        block.clear()

    for line in lines:
        if is_tabular(line):
            block.append(line)
        else:
            if block:
                flush_block()
            result.append(line)

    if block:
        flush_block()

    return "\n".join(result)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract text from PDFs into Markdown files."
    )
    parser.add_argument(
        "directory",
        nargs="?",
        default="hidden/Trusses AI/",
        help="Target directory containing PDFs (default: hidden/Trusses AI/)",
    )
    args = parser.parse_args()

    project_root = find_project_root()
    target = Path(args.directory)

    if not target.is_absolute():
        target = project_root / target

    target = target.resolve()

    if not target.is_dir():
        print(f"Error: directory does not exist: {target}", file=sys.stderr)
        sys.exit(1)

    pdfs = discover_pdfs(target)

    extracted: list[Path] = []
    skipped_images: list[Path] = []
    skipped_no_text: list[Path] = []
    failed: list[tuple[Path, str]] = []

    for pdf_path in pdfs:
        try:
            doc = fitz.open(str(pdf_path))
            try:
                skip, reason = should_skip(doc)
                if skip:
                    if reason == "images":
                        skipped_images.append(pdf_path)
                    elif reason == "no text":
                        skipped_no_text.append(pdf_path)
                else:
                    md_text = extract_text_as_markdown(doc)
                    md_text = format_code_blocks(md_text)
                    md_path = pdf_path.with_suffix(".md")
                    md_path.write_text(md_text, encoding="utf-8")
                    extracted.append(pdf_path)
            finally:
                doc.close()
        except Exception as e:
            failed.append((pdf_path, str(e)))

    print(f"Total PDFs found: {len(pdfs)}")
    print(f"Extracted: {len(extracted)}")
    print(f"Skipped (images): {len(skipped_images)}")
    print(f"Skipped (no text): {len(skipped_no_text)}")
    print(f"Failed: {len(failed)}")
    for path, error in failed:
        print(f"  {path}: {error}")


if __name__ == "__main__":
    main()
