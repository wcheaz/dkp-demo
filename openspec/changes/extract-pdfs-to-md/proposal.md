## Why

The directory `hidden/Trusses AI/` contains 267 PDFs with Slovak/Czech content — material takeoffs, architectural plans, technical reports, structural assessments. These documents hold critical context for an AI agent that designs roof trusses and generates pricing, but the content is locked in binary PDF format and written in Slovak/Czech. Extracting the text into structured Markdown files makes the data readable by both humans and AI agents, enabling downstream translation and agent consumption.

This change focuses solely on extraction. Translation of the resulting `.md` files will be a separate follow-up change.

## What Changes

- A Python script (`scripts/extract_pdfs_to_md.py`) that extracts text from PDFs in `hidden/Trusses AI/` and writes structured `.md` files alongside each PDF.
- The script targets 196 PDFs that contain extractable text and no embedded raster images. It skips PDFs with images (52), vector-only PDFs with no extractable text (19), and non-PDF files.
- Each `.md` file preserves page structure and formats tables, headings, and annotations as readable Markdown.

### PDF inventory

| Category | Count | Typical size | Source app | Structure |
|---|---|---|---|---|
| `*.material.pdf` | 40 | ~1000-1200 chars, 1 page | Microsoft Excel | Tabular material takeoff with lumber specs, pricing, roof dimensions |
| `Floor Plan + 3D.pdf` | 40 | ~900-1800 chars, 3-5 pages | Pamir (truss CAD) | Plan pages with text annotations (dimensions, load notes, section labels) |
| Supporting documents | 116 | 500-44000 chars, 1-16 pages | Mixed (ARCHICAD, PrimoPDF, PDFsharp, etc.) | Technical reports, floor plans, sections, elevations, structural assessments |

### Skipped PDFs (out of scope)

- 52 PDFs with embedded raster images — text extraction works but images carry meaning the `.md` cannot capture.
- 19 vector-only PDFs with no extractable text — require OCR, deferred to a follow-up change.

## Capabilities

### New Capabilities

- `pdf-text-extraction`: A Python script in `scripts/` that extracts text from PDFs into structured Markdown files, handling tables, multi-page documents, and mixed formatting.

### Modified Capabilities

_(none)_

## Impact

- **Disk space**: Negligible — `.md` files are plain text, typically 1-50 KB each. 196 files ≈ 2-5 MB total.
- **Git**: The generated `.md` files are text and git-friendly. The script is code in `scripts/`.
- **Dependencies**: Requires Python 3.12+ with `PyMuPDF` (already installed as `fitz` / `pymupdf`).
- **No API, server, or existing code changes**: This is a standalone CLI script.

## Scope

### In Scope

1. A Python script at `scripts/extract_pdfs_to_md.py` that processes PDFs from a given source directory.
2. The script extracts text from each PDF using PyMuPDF and writes a `.md` file in the same directory as the source PDF.
3. Output naming: for `001IK26A.material.pdf`, produce `001IK26A.material.md` alongside it.
4. The script formats extracted text as Markdown: tables for tabular data (material PDFs), page separators for multi-page PDFs, preserved section headings where detectable.
5. The script skips PDFs that contain embedded raster images (reports them in a summary log).
6. The script skips PDFs with zero extractable text (reports them in a summary log).
7. The script is idempotent — re-running overwrites existing `.md` files with the same result.
8. The script prints a summary to stdout: total PDFs found, extracted, skipped (with reasons), and failed (with file paths).
9. Default target directory is `hidden/Trusses AI/`, but the script accepts an arbitrary directory path as a CLI argument.
10. The script is runnable as `python scripts/extract_pdfs_to_md.py [directory]`.

### Non-Goals

- Do NOT translate any text. Output `.md` files contain the original Slovak/Czech text verbatim.
- Do NOT extract from PDFs with embedded raster images (52 PDFs).
- Do NOT extract from vector-only PDFs with no text (19 PDFs).
- Do NOT process `.jpg` or other non-PDF files.
- Do NOT modify or move the original PDFs.
- Do NOT build a GUI or web interface.
- Do NOT process `hidden/Väzníky AI/` — only `hidden/Trusses AI/`.
- Do NOT commit the generated `.md` files to git as part of this change (git commit decision is a human handoff).

## Success Criteria

The change is complete when:

- [ ] `scripts/extract_pdfs_to_md.py` exists and runs without errors.
- [ ] Running the script on `hidden/Trusses AI/` produces 196 `.md` files alongside their source PDFs.
- [ ] Material PDF `.md` files render as readable Markdown tables with correct numeric data.
- [ ] Floor Plan + 3D `.md` files contain all extracted annotations, dimensions, and load notes.
- [ ] Supporting document `.md` files preserve section structure and prose.
- [ ] The script prints a summary: 267 PDFs found, 196 extracted, 52 skipped (images), 19 skipped (no text), 0 failed.
- [ ] Original PDFs are untouched (byte-identical).
- [ ] Re-running the script produces identical `.md` output (idempotent).

## Human Handoff Items

1. **Review extracted Markdown**: Spot-check `.md` files for completeness and readability.
2. **Git commit decision**: Decide whether to commit the generated `.md` files.
3. **Image-containing and vector-only PDFs**: 71 PDFs remain unextracted; decide on OCR or alternative strategy.
4. **Translation**: A separate change will translate the 196 `.md` files from Slovak/Czech to English.
