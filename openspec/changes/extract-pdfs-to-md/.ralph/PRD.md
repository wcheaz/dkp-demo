# Product Requirements Document

*Generated from OpenSpec artifacts*

## Proposal

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

## Specifications

pdf-text-extraction/spec.md
## ADDED Requirements

### Requirement: Script discovers all PDFs in target directory

The script SHALL recursively walk the target directory and collect all files with a `.pdf` extension (case-insensitive). It SHALL ignore all non-PDF files.

#### Scenario: Directory with mixed file types

- **GIVEN** a directory containing `.pdf`, `.jpg`, `.txt`, and `.md` files
- **WHEN** the script runs against that directory
- **THEN** only `.pdf` files are included in the processing queue

#### Scenario: Nested project subdirectories

- **GIVEN** the directory `hidden/Trusses AI/` with 33 project folders, each containing subdirectories with PDFs
- **WHEN** the script runs with default arguments
- **THEN** all PDFs in all nested subdirectories are discovered

### Requirement: Script skips PDFs with embedded raster images

For each discovered PDF, the script SHALL compute the total count of embedded raster images using `page.get_images()`. If the count is greater than zero, the script SHALL skip that PDF and record it in the summary as "skipped (images)".

#### Scenario: PDF with JPEG or PNG images

- **GIVEN** a PDF containing one or more embedded raster images (JPEG, PNG, etc.)
- **WHEN** the script processes that PDF
- **THEN** the PDF is skipped, no `.md` file is produced, and the file path is reported in the summary under "skipped (images)"

#### Scenario: PDF with vector drawings but no raster images

- **GIVEN** a PDF containing vector drawing blocks but zero embedded raster images per `get_images()`
- **WHEN** the script processes that PDF
- **THEN** the PDF is NOT skipped — text extraction proceeds normally

### Requirement: Script skips PDFs with zero extractable text

For each discovered PDF that passes the image check, the script SHALL compute the total character count of extractable text across all pages. If the total is zero, the script SHALL skip that PDF and record it in the summary as "skipped (no text)".

#### Scenario: Vector-only PDF with no text layer

- **GIVEN** a PDF where all content is vector paths with no extractable text (0 chars from `get_text()`)
- **WHEN** the script processes that PDF
- **THEN** the PDF is skipped, no `.md` file is produced, and the file path is reported in the summary under "skipped (no text)"

### Requirement: Script extracts text and writes Markdown files

For each PDF that passes both skip checks, the script SHALL extract text page-by-page using PyMuPDF and write a `.md` file. The output file SHALL be placed in the same directory as the source PDF, with the same base name and a `.md` extension (e.g., `001IK26A.material.pdf` produces `001IK26A.material.md`).

#### Scenario: Single-page material PDF

- **GIVEN** a 1-page material PDF named `015IK26A.material.pdf` containing tabular lumber data
- **WHEN** the script processes that PDF
- **THEN** a file `015IK26A.material.md` is created in the same directory containing all extracted text

#### Scenario: Multi-page Floor Plan PDF

- **GIVEN** a 5-page Floor Plan PDF with annotations on page 1 and title blocks on pages 2-5
- **WHEN** the script processes that PDF
- **THEN** a single `.md` file is created containing text from all 5 pages separated by page markers

### Requirement: Multi-page PDFs use page separators

When a PDF has more than one page, the script SHALL separate each page's text with a page marker. The marker SHALL follow the format `---` (horizontal rule) followed by `## Page N` (heading) where N is the 1-indexed page number. Single-page PDFs SHALL NOT include any page separator or heading.

#### Scenario: Single-page PDF has no page markers

- **GIVEN** a 1-page material PDF
- **WHEN** the script writes the `.md` file
- **THEN** the file contains the extracted text with no `---` separator and no `## Page` heading

#### Scenario: Three-page PDF has two page separators

- **GIVEN** a 3-page PDF
- **WHEN** the script writes the `.md` file
- **THEN** the file contains `## Page 1` heading, followed by page 1 text, then `---`, then `## Page 2`, page 2 text, `---`, `## Page 3`, page 3 text

### Requirement: Tabular data is wrapped in code blocks

When consecutive lines of extracted text contain multiple whitespace-separated columns (heuristic: 3 or more consecutive lines each containing 2 or more multi-space gaps), the script SHALL wrap that block of lines in a Markdown code fence (triple backticks). Lines that do not match this pattern SHALL be output as regular text.

#### Scenario: Material PDF with lumber table

- **GIVEN** a material PDF where extracted text contains lines like `C24  45  70  340,3  1,0718`
- **WHEN** the script writes the `.md` file
- **THEN** those consecutive tabular lines are wrapped in a code fence block

#### Scenario: Prose text is not wrapped

- **GIVEN** a technical report PDF with flowing prose paragraphs
- **WHEN** the script writes the `.md` file
- **THEN** prose lines are output as regular text, not wrapped in code fences

### Requirement: Original PDFs remain untouched

The script SHALL NOT modify, move, rename, or delete any original PDF file. After script execution, every PDF in the target directory SHALL be byte-identical to its pre-execution state.

#### Scenario: Script runs on directory with existing PDFs

- **GIVEN** a directory containing PDFs with known checksums
- **WHEN** the script runs to completion
- **THEN** all original PDF files have identical checksums to their pre-run values

### Requirement: Script prints summary to stdout

Upon completion, the script SHALL print a summary to stdout containing: total PDFs found, number extracted, number skipped with reason (images, no text), and number failed with file paths. Failed PDFs are those where extraction raised an exception.

#### Scenario: Full run on hidden/Trusses AI/

- **GIVEN** the directory `hidden/Trusses AI/` containing 267 PDFs (196 text-only, 52 with images, 19 with no text)
- **WHEN** the script completes
- **THEN** stdout contains counts matching: 267 found, 196 extracted, 52 skipped (images), 19 skipped (no text), 0 failed

#### Scenario: PDF fails to open

- **GIVEN** a corrupted PDF that raises an exception when opened by PyMuPDF
- **WHEN** the script encounters that PDF
- **THEN** the error is caught, the file path is recorded as failed, and processing continues with remaining PDFs

### Requirement: Script accepts target directory as CLI argument

The script SHALL accept an optional positional argument specifying the target directory. If omitted, the default SHALL be `hidden/Trusses AI/` (resolved relative to the project root). The script SHALL exit with a non-zero code and an error message if the specified directory does not exist.

#### Scenario: Default directory

- **GIVEN** the script is invoked as `python scripts/extract_pdfs_to_md.py`
- **WHEN** the script starts
- **THEN** it processes `hidden/Trusses AI/` relative to the project root

#### Scenario: Custom directory

- **GIVEN** the script is invoked as `python scripts/extract_pdfs_to_md.py /some/other/path`
- **WHEN** `/some/other/path` exists and contains PDFs
- **THEN** it processes that directory instead of the default

#### Scenario: Non-existent directory

- **GIVEN** the script is invoked with a directory path that does not exist
- **WHEN** the script starts
- **THEN** it prints an error message to stderr and exits with a non-zero code

### Requirement: Script is idempotent

Running the script multiple times on the same directory SHALL produce identical `.md` output. Re-running SHALL overwrite existing `.md` files with the same content.

#### Scenario: Re-run produces identical files

- **GIVEN** the script has already been run on a directory producing a set of `.md` files
- **WHEN** the script is run again on the same directory
- **THEN** every `.md` file is overwritten with identical content (verified by checksum)



## Design

## Context

The directory `hidden/Trusses AI/` contains 267 PDFs across 33 project folders. A previous change (`2026-04-16-translate-vazniky-filenames`) translated filesystem names to English but left all file contents untouched. The PDFs contain Slovak/Czech text: material takeoffs, architectural plan annotations, technical reports, structural assessments, and more.

Analysis of the PDF population reveals:

- **196 PDFs**: extractable text, no embedded raster images → in scope
- **52 PDFs**: contain embedded raster images → out of scope (images carry meaning)
- **19 PDFs**: vector-only, zero extractable text → out of scope (needs OCR)

The 196 in-scope PDFs fall into three structural patterns:

1. **Material PDFs** (40 files, `*.material.pdf`): Generated by Microsoft Excel, 1 page each, ~1000-1200 chars. Contains tabular lumber specs, pricing, roof dimensions. Font analysis shows bold labels (Arial-BoldMT) paired with regular values (Calibri).

2. **Floor Plan + 3D PDFs** (40 files): Generated by Pamir (truss CAD software), 3-5 pages each. Page 1 contains dense annotations (load values, construction notes, dimensions). Pages 2-5 are plan views with only title-block metadata (project number, date, page number). These PDFs have vector drawing blocks but no raster images per `get_images()`.

3. **Supporting documents** (116 files): Heterogeneous sources (ARCHICAD, PrimoPDF, PDFsharp, etc.), 1-16 pages. Range from short plan annotations (~500 chars) to full technical reports (~44K chars). May contain mixed prose, section headings, numbered lists, and tabular data.

Python 3.12+ is available. PyMuPDF (`fitz`) version 1.26.7 is already installed, along with `pymupdf4llm`. `pdftotext` (poppler-utils) is also available as a subprocess fallback.

## Goals / Non-Goals

**Goals:**

- Extract all extractable text from 196 image-free PDFs into well-structured Markdown files.
- Produce `.md` files that are readable by both humans and AI agents without further processing.
- Preserve the numeric data, labels, and structural relationships from the original PDFs.
- Provide a clear summary of what was extracted, what was skipped, and what failed.
- Place the script in `scripts/` following the project convention.

**Non-Goals:**

- No translation — output files contain original Slovak/Czech text verbatim.
- No PDF reconstruction — output is `.md` only.
- No OCR — vector-only and image-containing PDFs are skipped entirely.
- No table-perfection — tables extracted from PDFs will be best-effort Markdown approximations, not pixel-perfect recreations.
- No parallelism or performance optimization — 196 files is small enough for sequential processing.

## Decisions

### D1: Use PyMuPDF (`fitz`) as the primary extraction library

**Choice**: PyMuPDF's `page.get_text()` API.

**Rationale**: PyMuPDF is already installed and provides:
- Per-page text extraction with position information
- Font metadata (name, size, bold/italic) for Markdown formatting hints
- Image detection via `page.get_images()` for skip logic
- No subprocess overhead

**Alternative considered**: `pdftotext` (poppler-utils) via subprocess. Works well but provides no font metadata and requires subprocess management. Kept as a mental fallback but not used.

**Alternative considered**: `pymupdf4llm`. This library converts PDF pages to Markdown optimized for LLM consumption. However, it may add unnecessary processing overhead and its table detection behavior is opaque. Direct PyMuPDF `get_text()` gives more control over formatting decisions.

### D2: Text extraction mode — use `get_text("text")` with page iteration

**Choice**: Iterate pages, call `page.get_text("text")` per page, concatenate with page separators.

**Rationale**: The `"text"` mode returns clean, ordered text lines with natural line breaks. It handles the three PDF categories well:
- Material PDFs: lines come out in reading order, tabular data preserves column alignment via whitespace.
- Floor Plan + 3D: annotations appear in order on page 1, title blocks on subsequent pages.
- Supporting docs: prose flows naturally, section headings appear as separate lines.

**Alternative considered**: `get_text("dict")` for block-level analysis with font metadata. Provides bold detection and spatial positioning but adds significant complexity. The added value for this use case (agent context, not layout reproduction) does not justify the cost. If bold/heading detection is needed later, this can be upgraded.

**Alternative considered**: `get_text("blocks")`. Returns text blocks with bounding boxes but strips intra-block formatting. Less useful than `"text"` for our purposes.

### D3: Table formatting — pass-through with whitespace preservation

**Choice**: Output extracted text lines as-is. Where lines contain multiple whitespace-separated columns (material PDFs), wrap them in a Markdown code block (` ``` `) to preserve alignment.

**Rationale**: PDF tables don't have a reliable "this is a table" marker. Attempting to parse tabular structure from positional data would require spatial analysis per PDF type. Instead:
- Detect consecutive lines with similar whitespace patterns (heuristic: 3+ lines with 2+ multi-space gaps).
- If detected, wrap the block in a code fence.
- Otherwise, output as regular Markdown text.

This produces readable output without fragile table-parsing logic.

**Alternative considered**: Building explicit Markdown tables (`| col1 | col2 |`). Rejected because PDF column alignment is inconsistent across sources — some use whitespace, some use position offsets invisible in text extraction. Code blocks are safer and still readable.

### D4: Skip detection — per-file image check

**Choice**: For each PDF, compute `total_images = sum(len(page.get_images(full=True)) for page in doc)`. Skip if `total_images > 0`. Also skip if `total_text_chars == 0`.

**Rationale**: `page.get_images()` detects embedded raster images (JPEG, PNG, etc.). This is the correct check because:
- It correctly identifies the 52 image-containing PDFs.
- It correctly passes the 40 Floor Plan + 3D PDFs (which have vector drawing blocks but no raster images).
- It correctly passes the material PDFs and text-heavy supporting docs.

### D5: Output structure — one `.md` per PDF, same directory

**Choice**: For `path/to/file.pdf`, write `path/to/file.md` in the same directory.

**Rationale**: Co-locating the `.md` with the PDF makes it easy to find the extraction for any given PDF. The naming convention (`file.pdf` → `file.md`) is unambiguous. The proposal's original `.sk.md` suffix was dropped because translation is a separate change — the `.md` files are simply the raw extraction at this stage.

### D6: Page separator format

**Choice**: Use `---\n## Page N\n\n` as the page separator.

**Rationale**: Horizontal rule + heading gives clear visual separation in rendered Markdown and provides structure for AI agents parsing the file. The `---` acts as a thematic break, and `## Page N` is a navigable heading.

### D7: CLI interface

**Choice**: `python scripts/extract_pdfs_to_md.py [directory]` using `argparse`.

- Positional argument: `directory` (default: `hidden/Trusses AI/`)
- No flags needed for initial implementation
- Script resolves the directory path relative to project root

### D8: Idempotency

**Choice**: Always overwrite existing `.md` files. No skip-if-exists logic.

**Rationale**: The extraction is deterministic (same PDF → same `.md`). Overwriting is simpler than checking timestamps and ensures a clean re-run. The proposal requires idempotency (same output on re-run), not incrementality.

## Risks / Trade-offs

| Risk | Mitigation |
|---|---|
| Text extraction ordering is wrong for some PDFs | PyMuPDF's `"text"` mode follows a top-to-bottom, left-to-right reading order. For the three PDF categories analyzed, this produces correct results. If edge cases appear, they can be handled per-file in a follow-up. |
| Table data loses column alignment in Markdown | Code-block wrapping preserves whitespace alignment. Not as pretty as Markdown tables, but reliable. The AI agent consuming these files does not need visual table formatting. |
| Floor Plan + 3D pages 2-5 produce very sparse `.md` (just title blocks) | This is expected — the actual plan content is vector graphics. The sparse `.md` still captures the metadata (project number, date, software version). The annotations on page 1 are the valuable content. |
| Some supporting docs are large (44K chars) producing large `.md` files | No action needed. Large `.md` files are fine — AI agents handle long context. |
| Font-based bold detection not available with `get_text("text")` mode | Accepted trade-off. Bold labels in material PDFs are distinguishable by context (labels vs values). If heading detection becomes critical, upgrade to `get_text("dict")` in a follow-up. |
| 19 vector-only PDFs produce empty `.md` files | They are skipped entirely (zero-text check). The summary log reports them as skipped. |

## Open Questions

_(none — all key decisions are resolved above)_

## Current Task Context

## Current Task
- 3.1 Run the script against `hidden/` directory and confirm it processes `hidden/test_text.pdf` and produces output matching the expected content in `hidden/test_text.md`. Before running, copy `hidden/test_text.md` to `tmp/test_text_expected.md` (the `tmp/` directory in the project root is gitignored and safe for scratch work). Then run the script. After the run, diff the new `hidden/test_text.md` against `tmp/test_text_expected.md` — they must match. Clean up `tmp/test_text_expected.md` when done.
## Completed Tasks for Git Commit
- [x] 1.1 Create `scripts/extract_pdfs_to_md.py` with `argparse` CLI accepting an optional positional `directory` argument (default: `hidden/Trusses AI/`). Resolve the path relative to the project root. Print error to stderr and exit non-zero if the directory does not exist.
- [x] 1.2 Implement `discover_pdfs(directory: Path) -> list[Path]` that recursively walks the directory and returns all `.pdf` files (case-insensitive extension match). No other file types are included.
- [x] 2.1 Implement `should_skip(doc: fitz.Document) -> tuple[bool, str]` that returns `(True, "images")` if `sum(len(page.get_images(full=True)) for page in doc) > 0`, returns `(True, "no text")` if total extracted text characters across all pages is zero, and `(False, "")` otherwise.
- [x] 2.2 Wire the skip check into the main loop: for each PDF, open with PyMuPDF, run `should_skip`, and categorize into extracted / skipped-images / skipped-no-text / failed lists.
