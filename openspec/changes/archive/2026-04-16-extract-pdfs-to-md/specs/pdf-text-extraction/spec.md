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
