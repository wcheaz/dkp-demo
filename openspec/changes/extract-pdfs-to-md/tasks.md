## 1. Script Skeleton and CLI Interface

- [x] 1.1 Create `scripts/extract_pdfs_to_md.py` with `argparse` CLI accepting an optional positional `directory` argument (default: `hidden/Trusses AI/`). Resolve the path relative to the project root. Print error to stderr and exit non-zero if the directory does not exist.
- [x] 1.2 Implement `discover_pdfs(directory: Path) -> list[Path]` that recursively walks the directory and returns all `.pdf` files (case-insensitive extension match). No other file types are included.

**Verify by:** Running `python scripts/extract_pdfs_to_md.py` with a non-existent path produces an error. Running against `hidden/Trusses AI/` discovers 267 PDFs.

## 2. PDF Filtering (Image and Zero-Text Skip)

- [x] 2.1 Implement `should_skip(doc: fitz.Document) -> tuple[bool, str]` that returns `(True, "images")` if `sum(len(page.get_images(full=True)) for page in doc) > 0`, returns `(True, "no text")` if total extracted text characters across all pages is zero, and `(False, "")` otherwise.
- [x] 2.2 Wire the skip check into the main loop: for each PDF, open with PyMuPDF, run `should_skip`, and categorize into extracted / skipped-images / skipped-no-text / failed lists.

**Verify by:** Running the script on `hidden/Trusses AI/` produces skip counts of 52 (images) and 19 (no text). Spot-check that the 40 material PDFs and 40 Floor Plan + 3D PDFs are NOT skipped.

## 3. Test with Test PDF

- [x] 3.1 Run the script against `hidden/` directory and confirm it processes `hidden/test_text.pdf` and produces output matching the expected content in `hidden/test_text.md`. Before running, copy `hidden/test_text.md` to `tmp/test_text_expected.md` (the `tmp/` directory in the project root is gitignored and safe for scratch work). Then run the script. After the run, diff the new `hidden/test_text.md` against `tmp/test_text_expected.md` — they must match. Clean up `tmp/test_text_expected.md` when done.

**Verify by:** The script output for `test_text.pdf` is identical to the expected content in `hidden/test_text.md`. Do NOT proceed to the formatting and full extraction steps until this basic extraction test passes.

## 4. Text Extraction and Markdown Formatting

- [x] 4.1 Implement `extract_text_as_markdown(doc: fitz.Document) -> str` that iterates pages, calls `page.get_text("text")` on each, and joins them with page separators. For single-page PDFs: no separator, no page heading. For multi-page PDFs: each page preceded by `---\n## Page N\n\n` where N is 1-indexed.
- [x] 4.2 Implement `format_code_blocks(text: str) -> str` that detects consecutive lines matching the tabular heuristic (3+ consecutive lines each containing 2+ multi-space gaps of 2+ spaces) and wraps those runs in triple-backtick code fences. Non-matching lines pass through unchanged.

**Verify by:** Extract text from `001IK26A.material.pdf` and confirm the lumber table is wrapped in a code fence. Extract from a technical report PDF and confirm prose is NOT wrapped in code fences.

## 5. File Writing and Main Pipeline

- [x] 5.1 Implement the main pipeline: for each non-skipped PDF, call `extract_text_as_markdown`, then `format_code_blocks`, then write the result to `{pdf_path.with_suffix('.md')}` in the same directory. Wrap each PDF in a try/except so failures are caught and recorded without halting the run.
- [x] 5.2 Implement summary output: after processing all PDFs, print to stdout a summary with counts for: total found, extracted, skipped (images), skipped (no text), failed (with file paths for any failures).

## 6. Full Extraction Run

- [x] 6.1 Run `python scripts/extract_pdfs_to_md.py` on `hidden/Trusses AI/`. Confirm it produces 196 `.md` files alongside their source PDFs and prints the expected summary (267 found, 196 extracted, 52 skipped images, 19 skipped no text, 0 failed).

## 7. Verification and Idempotency Check

- [ ] 7.1 Spot-check 3 material PDF `.md` files: confirm they contain readable tabular data with correct numeric values in code fences.
- [ ] 7.2 Spot-check 3 Floor Plan + 3D `.md` files: confirm page 1 annotations (load values, dimensions, construction notes) are present and pages are separated with `## Page N` headings.
- [ ] 7.3 Spot-check 3 supporting document `.md` files: confirm section structure and prose are preserved.
- [ ] 7.4 Verify idempotency: checksum all `.md` files, re-run the script, checksum again — confirm all checksums are identical.
- [ ] 7.5 Verify original PDFs are untouched: spot-check 5 PDFs across different projects by comparing file size and modification timestamp (or checksum) before and after the run.
