#!/usr/bin/env python3
import argparse
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
