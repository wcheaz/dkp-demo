#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path


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
    print(f"Target directory: {target}")
    print(f"PDFs found: {len(pdfs)}")


if __name__ == "__main__":
    main()
