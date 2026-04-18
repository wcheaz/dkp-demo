## ADDED Requirements

### Requirement: Companion translated file for each source Markdown file

For every `.md` file in `hidden/Trusses AI/` (excluding `translation-notes.txt` and `*_TRANSLATED.md`), the system SHALL produce a companion file named `{basename}_TRANSLATED.md` in the same directory containing a complete English translation of the source file's Slovak/Czech content.

#### Scenario: Material PDF Markdown file translated

- **WHEN** the source file `001IK26A.material.md` exists in a directory and no `001IK26A.material_TRANSLATED.md` exists
- **THEN** a file `001IK26A.material_TRANSLATED.md` is created in the same directory
- **AND** the translated file contains English text for all Slovak/Czech prose
- **AND** the translated file preserves all code fences, table alignment, and numeric values verbatim

#### Scenario: Floor Plan Markdown file translated

- **WHEN** the source file `Floor Plan + 3D.md` exists in a directory and no `Floor Plan + 3D_TRANSLATED.md` exists
- **THEN** a file `Floor Plan + 3D_TRANSLATED.md` is created in the same directory
- **AND** page separators (`---\n## Page N`) are preserved exactly
- **AND** ALL-CAPS construction annotations are translated to English while preserving dimension references

#### Scenario: Supporting document Markdown file translated

- **WHEN** a supporting document `.md` file exists (e.g., `Domanická_RD_Floor Plan Roof_670_297.md`) and no corresponding `_TRANSLATED.md` exists
- **THEN** a companion `_TRANSLATED.md` file is created
- **AND** prose sections, numbered lists, and section headings are translated to natural English

#### Scenario: All 196 source files have companions

- **WHEN** the change is complete
- **THEN** every one of the 196 `.md` files under `hidden/Trusses AI/` has a corresponding `_TRANSLATED.md` file
- **AND** no source `.md` file was modified (byte-identical to before the change)

### Requirement: Source files remain untouched

The system SHALL NOT modify the content, name, permissions, or modification timestamp of any source `.md` file. Source files SHALL be read-only for the duration of this change.

#### Scenario: Source file integrity preserved

- **WHEN** a source `.md` file is processed for translation
- **THEN** the source file's content is identical before and after processing
- **AND** no lines are added, removed, or reordered in the source file

### Requirement: Markdown structure preserved in translation

Every `_TRANSLATED.md` file SHALL preserve the exact Markdown structure of its source file. This includes heading levels, code fences, page separators, line breaks, and the number of lines.

#### Scenario: Code fences preserved in material file

- **WHEN** a source file contains a triple-backtick code fence with tabular lumber data
- **THEN** the translated file contains the same code fence with the same opening and closing markers
- **AND** column alignment inside the code fence is preserved
- **AND** Slovak/Czech column headers (e.g., `Kvalita`, `Tl.`, `Š.`, `Celk. Dl.`, `Celk. Kub.`) are translated to their English equivalents
- **AND** all numeric values pass through unchanged

#### Scenario: Page separators preserved in multi-page file

- **WHEN** a source file contains `---\n## Page N\n` separators
- **THEN** the translated file contains the same separators at the same positions

#### Scenario: Line count matches source

- **WHEN** a source file has N lines
- **THEN** the translated file has exactly N lines (one translated line per source line)

### Requirement: Numeric values and identifiers pass through verbatim

The system SHALL NOT translate or modify numeric values, dimension annotations, unit symbols, project codes, or proper nouns. These SHALL pass through to the translated file character-for-character.

#### Scenario: Numeric table data preserved

- **WHEN** a source file contains numeric values in a table (e.g., `45  70  340,3  1,0718`)
- **THEN** the translated file contains the same numeric values at the same positions

#### Scenario: Dimension references preserved

- **WHEN** a source file contains dimension annotations (e.g., `+5 300`, `8000  9600`, `A-A`, `B-B`)
- **THEN** the translated file contains the same dimension annotations unchanged

#### Scenario: Unit symbols preserved

- **WHEN** a source file contains unit symbols (e.g., `m2`, `m3`, `N/m²`, `CZK`, `mm`)
- **THEN** the translated file contains the same unit symbols unchanged

#### Scenario: Project codes preserved

- **WHEN** a source file contains a project code (e.g., `001IK26A`)
- **THEN** the translated file contains the same project code unchanged

#### Scenario: Proper nouns preserved

- **WHEN** a source file contains a person name (e.g., `Iveta Krajčova`), company name (e.g., `BigMat Dinostav`), or place name (e.g., `Veľké Lovce`)
- **THEN** the translated file contains the same proper noun unchanged

### Requirement: Translation notes appended per file

After translating a `.md` file, the system SHALL append a reasoning entry to the `translation-notes.txt` file in the same directory. The entry SHALL follow a fixed format and describe the key translation decisions made for that file.

#### Scenario: Translation note appended for material file

- **WHEN** `001IK26A.material.md` is translated to `001IK26A.material_TRANSLATED.md`
- **THEN** the file `translation-notes.txt` in the same directory has a new entry appended at the end
- **AND** the entry starts with a `---` divider line
- **AND** the entry includes the line `Content translation: 001IK26A.material.md → 001IK26A.material_TRANSLATED.md`
- **AND** the entry lists key translation decisions (e.g., Slovak term → English term with reasoning)

#### Scenario: Translation note appended for floor plan file

- **WHEN** `Floor Plan + 3D.md` is translated to `Floor Plan + 3D_TRANSLATED.md`
- **THEN** the `translation-notes.txt` in the same directory has a new entry appended with the file's translation reasoning

#### Scenario: Existing translation notes content preserved

- **WHEN** a `translation-notes.txt` file already contains filename translation entries from the prior change
- **THEN** those existing entries remain unchanged
- **AND** new content-translation entries are appended after the existing content

### Requirement: Idempotent resume via companion file check

The system SHALL skip any source `.md` file that already has a corresponding `_TRANSLATED.md` companion in the same directory. This enables safe resume after partial completion.

#### Scenario: Already-translated file skipped

- **WHEN** a source file `X.md` exists and `X_TRANSLATED.md` already exists in the same directory
- **THEN** the source file is skipped (no re-translation)
- **AND** no duplicate entry is appended to `translation-notes.txt`

#### Scenario: Partial run resumed correctly

- **WHEN** a previous run translated 80 of 196 files before stopping
- **THEN** a subsequent run skips those 80 files and translates only the remaining 116

### Requirement: Consistent terminology via fixed glossary

The system SHALL use the fixed technical glossary defined in the design document (decision D7) for all recurring Slovak/Czech construction terms. Terms not in the glossary SHALL be translated using the agent's best judgment, with the reasoning recorded in `translation-notes.txt`.

#### Scenario: Glossary term used consistently across files

- **WHEN** the term `zaťaženie snehom` appears in multiple source files
- **THEN** it is translated to `Snow load` in every translated file
- **AND** no file translates it to a different English equivalent

#### Scenario: Non-glossary term translated with reasoning

- **WHEN** a Slovak/Czech term appears that is not in the fixed glossary
- **THEN** the agent translates it using contextual judgment
- **AND** the reasoning for that translation choice is recorded in the file's `translation-notes.txt` entry
