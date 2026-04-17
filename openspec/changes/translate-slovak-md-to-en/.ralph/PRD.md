# Product Requirements Document

*Generated from OpenSpec artifacts*

## Proposal

## Why

The prior change `2026-04-16-extract-pdfs-to-md` extracted 196 PDFs into Markdown files under `hidden/Trusses AI/`, but the content remains in Slovak and Czech. These `.md` files hold the readable context — material takeoffs, structural load annotations, technical reports, floor-plan notes — that an AI truss-design agent needs. Without English translations, the agent cannot reason over the content. This change translates every extracted `.md` file from Slovak/Czech into English.

## What Changes

- For each of the 196 `.md` files in `hidden/Trusses AI/`, produce a companion `{basename}_TRANSLATED.md` in the same directory containing the full English translation.
- Append per-file translation reasoning to the existing `translation-notes.txt` in the same directory (these files already exist in all 63 directories from the prior `vazniky-english-copy` change).
- No script is required. The agent reads each source `.md`, translates the Slovak/Czech text to English inline, writes the companion `_TRANSLATED.md`, and appends a reasoning note to the nearby `translation-notes.txt`.

## Capabilities

### New Capabilities

- `md-translation`: Translates Slovak/Czech Markdown files into English by producing companion `*_TRANSLATED.md` files and recording reasoning in nearby `translation-notes.txt` files.

### Modified Capabilities

_(none)_

## Impact

- **Disk space**: Each `_TRANSLATED.md` is roughly the same size as its source (English text is comparable in length to Slovak/Czech). 196 files at ~5 KB each ≈ ~1 MB added.
- **No existing files modified**: Source `.md` files remain untouched. `translation-notes.txt` files are appended to, not overwritten.
- **No new dependencies**: The agent performs translation directly using its built-in multilingual capability. No external API, library, or model is needed.

## Scope

### In Scope

1. Discover all `.md` files under `hidden/Trusses AI/` (excluding `translation-notes.txt` and `*_TRANSLATED.md`).
2. For each source `.md` file (e.g., `001IK26A.material.md`), produce `{basename}_TRANSLATED.md` (e.g., `001IK26A.material_TRANSLATED.md`) in the same directory.
3. The translated file preserves the same Markdown structure: headings, code fences, page separators, line breaks, numeric tables, and dimension values remain structurally identical to the source.
4. Numeric values, dimension annotations, project codes, unit symbols, and proper nouns are NOT translated — they pass through verbatim.
5. After translating each file, append a note to the `translation-notes.txt` in the same directory. The note follows the existing format: `filename.md → filename_TRANSLATED.md: <brief reasoning for key translation decisions in that file>`.
6. Skip files already having a `_TRANSLATED.md` companion (idempotent resume).
7. Work directory-by-directory to keep translation notes coherent.

### Non-Goals

- Do NOT modify the original `.md` files.
- Do NOT translate PDFs, JPGs, or any non-MD files.
- Do NOT translate filenames or directory names (already done in the prior `vazniky-english-copy` change).
- Do NOT write a translation script — the agent translates inline.
- Do NOT process `hidden/Väzníky AI/` — only `hidden/Trusses AI/`.
- Do NOT commit the generated `_TRANSLATED.md` files to git as part of this change (git commit decision is a human handoff).
- Do NOT create new `translation-notes.txt` files — they already exist in all directories that contain `.md` files.

## Success Criteria

The change is complete when:

- [ ] Every source `.md` file in `hidden/Trusses AI/` (196 total) has a corresponding `_TRANSLATED.md` companion in the same directory.
- [ ] Each `_TRANSLATED.md` reads as natural English while preserving the exact Markdown structure (headings, code fences, tables, page breaks) of the source.
- [ ] Numeric values, dimensions, project codes, and unit symbols in `_TRANSLATED.md` files are identical to the source.
- [ ] The `translation-notes.txt` in each of the 63 directories has been appended with translation reasoning entries for every file translated in that directory.
- [ ] Re-running the change discovers all 196 files already translated and performs zero new translations.
- [ ] Original `.md` files are byte-identical before and after.

## Human Handoff Items

1. **Review translated Markdown**: Spot-check `_TRANSLATED.md` files for translation accuracy, especially technical terms (load values, structural terminology, construction vocabulary).
2. **Git commit decision**: Decide whether to commit the generated `_TRANSLATED.md` files and updated `translation-notes.txt` files.

## Specifications

md-translation/spec.md
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



## Design

## Context

The directory `hidden/Trusses AI/` contains 196 Markdown files across 63 directories and 33 project folders. These files were extracted from PDFs by the prior change `2026-04-16-extract-pdfs-to-md`. All content is in Slovak or Czech — material takeoffs, floor-plan annotations, structural load notes, technical reports, and construction specifications.

Every directory that contains `.md` files already has a `translation-notes.txt` file (created by the prior `vazniky-english-copy` change). These notes currently record filename and directory-name translations. This change appends content-translation reasoning to those existing files.

The 196 `.md` files fall into three structural categories (same as the extraction change):

| Category | Count | Typical structure | Translation challenge |
|---|---|---|---|
| Material PDFs (`*.material.md`) | 40 | Short (~40 lines). Tabular lumber specs in code fences, followed by roof dimension data and pricing. | Dense technical vocabulary: lumber grades, joint plates, roof geometry terms. Tables must preserve numeric alignment. |
| Floor Plan + 3D (`Floor Plan + 3D.md`) | 40 | 1-5 pages. Page 1 has dense ALL-CAPS annotation blocks (load values, construction notes, support requirements). Pages 2-5 are sparse title-block metadata. | ALL-CAPS Slovak construction annotations with abbreviations. Must translate while preserving dimension references like `+5 300`, `A-A`, `B-B`. |
| Supporting documents | 116 | Heterogeneous. Prose reports, numbered lists, section headings, mixed tables. Ranges from ~10 lines to ~800 lines. | Most varied. May contain formal report language, building code references, engineering specifications, and mixed Slovak/Czech prose. |

No Python script or external tool is used. The agent reads each `.md`, translates inline, writes the companion file, and appends notes.

## Goals / Non-Goals

**Goals:**

- Produce 196 `_TRANSLATED.md` files, one per source `.md`, with accurate English translations.
- Preserve exact Markdown structure in every translated file.
- Record translation reasoning per file in the nearby `translation-notes.txt`.
- Enable idempotent resume: if a `_TRANSLATED.md` already exists, skip that file.

**Non-Goals:**

- No script or automation tool.
- No modification of source `.md` files.
- No translation of filenames, directory names, or non-MD files.
- No OCR or image processing.
- No new `translation-notes.txt` files (all already exist).
- No git commit (human handoff).

## Decisions

### D1: No script — agent translates directly

**Choice**: The agent reads each source `.md`, translates it inline using its built-in multilingual capability, writes the `_TRANSLATED.md` file, and appends a reasoning note.

**Rationale**: Slovak/Czech construction vocabulary is well within the agent's capability. The 196 files total only ~988 KB and ~17,500 lines. No external translation API or library is needed. This avoids the overhead of writing, debugging, and maintaining a script while producing equivalent or better quality because the agent can reason about context-specific terminology per file.

### D2: Companion file naming — `{basename}_TRANSLATED.md`

**Choice**: For source file `X.md`, produce `X_TRANSLATED.md` in the same directory.

**Example**: `001IK26A.material.md` → `001IK26A.material_TRANSLATED.md`

**Rationale**: Co-locating the translation with the source makes discovery trivial. The `_TRANSLATED` suffix is unambiguous and does not collide with any existing naming convention. The `.md` extension is preserved so the file renders as Markdown in any viewer.

### D3: Translation notes format — append to existing `translation-notes.txt`

**Choice**: After translating a file, append a block to the `translation-notes.txt` in the same directory using this format:

```
---
Content translation: filename.md → filename_TRANSLATED.md
Key decisions:
- Slovak/Czech term → English term: <reasoning>
- <any other notable translation choices>
```

**Rationale**: The existing `translation-notes.txt` files use a `Directory: ... ===` header format for filename translations. The new content-translation entries are appended below, separated by a `---` divider. This keeps all translation reasoning in one file per directory without disturbing existing content.

**Alternative considered**: Separate `translation-reasoning.txt` per file. Rejected — too many small files, and the reasoning is often short (1-5 lines). One file per directory is cleaner.

### D4: Structural preservation rules

**Choice**: The following rules apply to every translated file:

1. Markdown headings (`##`, `###`) keep the same level and position.
2. Code fences (` ``` `) are preserved exactly. Content inside code fences is translated (Slovak labels become English) but numeric columns, alignment, and whitespace are preserved character-for-character.
3. Page separators (`---\n## Page N\n`) are preserved exactly.
4. Numeric values, dimensions (`+5 300`), unit symbols (`m2`, `N/m²`, `CZK`, `m3`), and project codes pass through unchanged.
5. Proper nouns (person names, company names, place names) pass through unchanged.
6. Line count must match the source (one translated line per source line).

**Rationale**: The downstream consumer is an AI agent that parses these files. Structural fidelity ensures the agent can correlate source and translation line-by-line. Code fences contain tabular data where column alignment matters for readability.

### D5: Idempotent resume — check for existing `_TRANSLATED.md`

**Choice**: Before translating a file, check whether `{basename}_TRANSLATED.md` already exists. If it does, skip that file.

**Rationale**: With 196 files, the loop may not complete in one session. Resume must be safe — re-translating an already-translated file wastes time and may introduce inconsistency if the second translation differs from the first. Presence of the companion file is sufficient proof of completion.

### D6: Processing order — directory by directory

**Choice**: Process files grouped by directory. For each directory: read all source `.md` files, translate them all, then update `translation-notes.txt` once with all entries for that directory.

**Rationale**: Grouping by directory means `translation-notes.txt` is opened and appended once per directory rather than once per file. The 63 directories are a natural batch unit. The agent can read the directory's existing notes, translate all files in it, and append all reasoning in one write.

### D7: Technical glossary for consistent terminology

**Choice**: Use the following fixed translations for recurring Slovak/Czech construction terms. This prevents the agent from choosing different English equivalents in different files.

| Slovak/Czech | English |
|---|---|
| Cenová nabídka | Price quote |
| Zakázka | Order |
| Zákazník | Customer |
| Výpis řeziva dle skladových | Lumber list by stock items |
| Kvalita | Grade |
| Tl. (Tloušťka) | Th. (Thickness) |
| Š. (Šířka) | W. (Width) |
| Celk. Dl. (Celková délka) | Total L. (Total Length) |
| Celk. Kub. (Celková kubatura) | Total Vol. (Total Volume) |
| Celkem | Total |
| Cena bez DPH | Price excl. VAT |
| Údaje o střeše | Roof data |
| Celková půdorysná plocha pod střechou | Total floor plan area under roof |
| Celková střešní plocha | Total roof area |
| Půdorysná plocha uvnitř budovy | Floor plan area inside building |
| Půdorysná plocha mimo budovu | Floor plan area outside building |
| Délka okapu | Eave length |
| Délka pozednice | Sole plate length |
| Délka valbových linií | Hip line length |
| Délka úžlabních linií | Valley line length |
| Délka hřebenu | Ridge length |
| Délka ztužení | Bracing length |
| Celkové rozpětí vazníků | Total truss span |
| Celkový počet vazníků | Total truss count |
| Styčník | Joint |
| Styčníkové desky | Gusset plates |
| Závěs | Hanger |
| Dřevěný prvek | Timber element |
| Pomurnica | Wall plate |
| Hranol | Beam |
| Kubatura | Volume |
| Zavětrování | Bracing |
| Valba | Hip roof |
| Sedlo | Gable |
| Pultový | Mono-pitch |
| Zaťaženie / zaťažení | Load |
| Stále zaťaženie | Permanent load |
| Zaťaženie snehom | Snow load |
| Zaťaženie vetrom | Wind load |
| Úžitkové zaťaženie | Live load |
| Podpora pre väzník | Truss support |
| Úložný priestor | Storage space |
| Poznámky na okraj | Marginal notes |
| Pôdorys | Floor plan |
| Strecha | Roof |
| Krov | Roof framing |
| Strop | Ceiling |
| Podlaha | Floor |
| Zateplenie | Insulation |
| Väzník | Truss |
| Priečka | Partition wall |

This glossary is not exhaustive. The agent should use it for consistency on known terms and exercise judgment for terms not listed, recording novel decisions in `translation-notes.txt`.

## Risks / Trade-offs

| Risk | Mitigation |
|---|---|
| Translation quality varies across 196 files | The fixed glossary (D7) ensures consistent terminology. The per-file reasoning in `translation-notes.txt` makes quality auditable. Human review (handoff item) covers edge cases. |
| ALL-CAPS annotations in Floor Plan files lose emphasis if lowercased | Preserve casing style where it conveys emphasis (e.g., section headers stay uppercase). Translate meaning, not formatting. |
| Code fence content in material PDFs must preserve column alignment | Translate only Slovak/Czech labels within tables. Numeric columns pass through verbatim. If label translation changes column width, pad with spaces to maintain alignment. |
| Large supporting documents (~800 lines) may be slow to translate inline | Accept the time cost. These are rare (a handful of files). The agent processes one file at a time, so memory is not a concern. |
| Resume after partial run may leave a directory with some files translated and some not | This is safe. The idempotent check (D5) means the next run picks up where it left off. Within a directory, `translation-notes.txt` entries accumulate correctly regardless of order. |
| No automated verification of translation accuracy | Accepted trade-off. There is no automated Slovak→English oracle. Verification is human review (handoff). Structural preservation (matching line count, preserved code fences, preserved numerics) is objectively checkable. |

## Open Questions

_(none — all key decisions are resolved above)_

## Current Task Context

## Current Task
- 1.1 Discover all `.md` files in `hidden/Trusses AI/` that need translation. Count the total number of files. Confirm the count is 196. Verify that none of these files have corresponding `_TRANSLATED.md` companions.
