# Product Requirements Document

*Generated from OpenSpec artifacts*

## Proposal

## Why

The directory `hidden/Väzníky AI/` contains 33 roof-truss project folders with Slovak-language file and directory names. For English-language testing and collaboration, an English-translated copy of this directory tree is needed. Only filesystem names are translated — file contents (PDFs, images, spreadsheets) are copied verbatim.

## What Changes

- Create a new directory `hidden/Trusses AI/` as a full structural copy of `hidden/Väzníky AI/`.
- Translate every subdirectory name and file name (Slovak, German, Czech) to English using the glossary in `hidden/VAZNIKY_BASIC_OVERVIEW_TRANSLATION.md` and the supplementary German/Czech translation table below.
- Preserve the original `hidden/Väzníky AI/` directory completely untouched.
- Place a `translation-notes.txt` file inside every directory (including the root of `Trusses AI/`) that briefly documents the translations applied to items in that directory (Slovak, German, or Czech to English).
- File contents are NEVER modified — they are byte-for-byte copies (PDF, JPG, PNG, DOCX, XLS, DWG, TXT, etc.).

## Capabilities

### New Capabilities
- `vazniky-english-copy`: One-shot directory tree copy with translated filesystem names and per-directory translation-notes files.

### Modified Capabilities
_(none — this is a new standalone artifact)_

## Impact

- **Disk space**: Roughly doubles the storage used by `hidden/` (~246 MB additional).
- **Git**: The new `hidden/Trusses AI/` directory will contain many binary files (PDFs, images). `.gitignore` rules or Git LFS may need consideration before committing.
- **No code, API, or dependency changes**: This is purely a data/file-organization task.

## Scope

### In Scope
1. Recursively copy `hidden/Väzníky AI/` to `hidden/Trusses AI/`.
2. Rename every directory from Slovak to English.
3. Rename every file from Slovak to English.
4. Create `translation-notes.txt` in each directory explaining what was translated and why.
5. Preserve the project-code prefix on top-level project folders (e.g., `001IK26A - `) since those are identifiers, not translatable text.
6. Preserve file extensions exactly as-is.
7. Preserve the `N.material.pdf` naming pattern for material takeoff PDFs (where N is the project code).

### Non-Goals
- Do NOT translate file contents (PDFs, images, documents, spreadsheets).
- Do NOT modify, move, or delete the original `hidden/Väzníky AI/` directory.
- Do NOT rename the original directory.
- Do NOT create any code, scripts, or automation beyond this one-time copy.
- Do NOT translate the project-code portion of top-level folder names (e.g., `001IK26A`, `033JO26A` — these are identifiers).
- Do NOT commit binary files to git as part of this change (that is a separate decision).

## Translation Source

All translations use the glossary in `hidden/VAZNIKY_BASIC_OVERVIEW_TRANSLATION.md` as the primary source. Supplementary translations for German and Czech terms found in the directory are listed below.

### Slovak translations (primary glossary)

| Slovak | English |
|---|---|
| Väzníky AI | Trusses AI |
| Návrh väzníka A / B | Truss Design Variant A / B |
| Finálny návrh | Final Design |
| Podklady / podklady | Supporting Documents |
| Pôdorys / Pôdorys+3D | Floor Plan / Floor Plan + 3D |
| Strecha / Strechy | Roof / Roofs |
| Krov | Roof Framing |
| Rez / Rezy | Section / Sections |
| Pohľady / pohlady / pohlad | Elevations / View |
| Stavebná časť | Construction Section |
| Situácia / situacia | Site Plan |
| Základy | Foundations |
| Strop / Stropná doska | Ceiling / Floor Slab |
| dom | House |
| garáž / garaz | Garage |
| ustúpené podlažie | Set-back Floor |
| Polyfunkčný objekt | Mixed-use Building |
| správa | Report |
| Nový textový dokument | New Text Document |

### German translations (found in project 058JO26A)

| German | English | Context |
|---|---|---|
| Ans (Ansicht) | View / Elevation | Architectural view |
| 3D Ans | 3D View | 3D visualization |
| EG (Erdgeschoss) | Ground Floor | 1st floor at ground level |
| OG (Obergeschoss) | Upper Floor | Floor above ground |
| Schnitt | Section | Vertical cross-section |
| Entwässerung | Drainage | Water drainage plan |
| Beze jména (Czech) | Untitled | Placeholder CAD filename |

The full glossary in `VAZNIKY_BASIC_OVERVIEW_TRANSLATION.md` is the authoritative reference when ambiguous Slovak terms are encountered. For German and Czech terms not listed above, the implementing agent should use standard architectural/engineering German-English translation.

## Success Criteria

The change is complete when:

- [ ] Directory `hidden/Trusses AI/` exists with the same number of top-level project folders (33) as `hidden/Väzníky AI/`.
- [ ] Every subdirectory and file inside `hidden/Trusses AI/` has an English name.
- [ ] Every directory inside `hidden/Trusses AI/` (including the root) contains a `translation-notes.txt` file.
- [ ] No Slovak-language, German-language, or Czech-language directory or file names exist inside `hidden/Trusses AI/` (project-code prefixes excluded).
- [ ] The original `hidden/Väzníky AI/` directory is completely unchanged (verified by diff or checksum).
- [ ] File contents are byte-identical between source and destination (spot-check at least 5 PDFs across different projects).
- [ ] Project-code prefixes (`001IK26A`, `033JO26A`, etc.) are preserved on top-level folders.
- [ ] German-language filenames in project 058JO26A are translated to English (e.g., `EG` → `Ground Floor`, `Schnitt` → `Section`, `Entwässerung` → `Drainage`).

## Human Handoff Items

1. **Git commit decision**: Decide whether to commit the ~246 MB of binary files to git, use Git LFS, or keep them gitignored.
2. **Translation review**: Spot-check a sample of translated filenames against the original Slovak to confirm accuracy.
3. **Future file-content translation**: This change explicitly does NOT translate file contents. If PDF content translation is desired later, that is a separate change.

## Specifications

vazniky-english-copy/spec.md
## ADDED Requirements

### Requirement: Full directory tree copy with English names

The system SHALL create a complete recursive copy of `hidden/Väzníky AI/` at `hidden/Trusses AI/` where every directory name and file name is translated to English. The original `hidden/Väzníky AI/` directory SHALL remain completely untouched.

The top-level directory name translation SHALL be: `Väzníky AI` → `Trusses AI`.

#### Scenario: Top-level directory created with English name

- **WHEN** the copy process begins
- **THEN** a new directory `hidden/Trusses AI/` is created
- **AND** the original `hidden/Väzníky AI/` directory is unchanged (same file count, same names, same contents)

#### Scenario: All 33 project folders are copied with translated names

- **WHEN** the copy process completes
- **THEN** `hidden/Trusses AI/` contains exactly 33 top-level project folders
- **AND** each folder retains its project-code prefix (e.g., `001IK26A - `, `033JO26A - `, `044AC26A - `)
- **AND** the translatable portion of each folder name is in English (e.g., `001IK26A - Matlúch_dom` → `001IK26A - Matlúch_House`)

### Requirement: Slovak directory name translation

The system SHALL translate Slovak directory names to English using the glossary in `hidden/VAZNIKY_BASIC_OVERVIEW_TRANSLATION.md`. The following translations SHALL be applied consistently:

| Slovak | English |
|---|---|
| Návrh väzníka A | Truss Design Variant A |
| Návrh väzníka B | Truss Design Variant B |
| Finálny návrh | Final Design |
| Podklady / podklady | Supporting Documents |
| Stavebná časť | Construction Section |
| PDF ARCH | PDF ARCH (kept as-is — already English abbreviation) |
| PDF ELEKTRO | PDF Electrical |
| PDF EPH | PDF Energy Performance |
| PDF POŽIAR | PDF Fire Protection |
| PDF STATIKA | PDF Structural Engineering |
| PDF TZB | PDF Building Services |
| RD MORAVCIK MM | RD Moravčík MM |
| ARCH | Architecture |
| ST | Structural Assessment |
| Návrh | Proposal |

#### Scenario: Standard subdirectory names translated

- **WHEN** a directory named `Návrh väzníka A` is encountered
- **THEN** it is copied as `Truss Design Variant A`

#### Scenario: Lowercase variant subdirectory names translated

- **WHEN** a directory named `podklady` (lowercase) is encountered
- **THEN** it is copied as `Supporting Documents`

#### Scenario: Deep nested directory names translated

- **WHEN** a directory named `STAVEBNÁ ČASŤ` is encountered at any nesting depth
- **THEN** it is copied as `Construction Section`

### Requirement: Slovak file name translation

The system SHALL translate Slovak file names to English. File extensions SHALL be preserved exactly. The `N.material.pdf` naming pattern (where N is the project code) SHALL be preserved as-is since the project code is an identifier.

Key file-name translations:

| Slovak pattern | English pattern |
|---|---|
| Pôdorys+3D.pdf | Floor Plan + 3D.pdf |
| Pôdorys / podorys | Floor Plan |
| Strecha / strechy / strechu | Roof |
| Krov / krovu | Roof Framing |
| Rez / rezy / rez | Section |
| Pohľady / pohlady / pohlad | Elevations / View |
| Situácia / situacia / situácia | Site Plan |
| Základy / základov | Foundations |
| Strop / stropná doska | Ceiling / Floor Slab |
| dom / domu | House |
| garáž / garaz | Garage |
| správa / Správa | Report |
| podorys strechy | Floor Plan Roof |
| ustúpené podlažie | Set-back Floor |
| Nový textový dokument | New Text Document |
| Koordinačná situácia | Coordination Site Plan |
| Technická správa / TS | Technical Report |
| Sprievodná a technická správa | Cover and Technical Report |
| Statický posudok | Structural Assessment |
| preklady | Lintels |
| výstuž / vystuž / vystuze | Reinforcement |
| schody | Stairs |
| trám | Beam |
| príloha / Príloha | Appendix |
| zariadovacie predmety | Sanitary Fixtures |
| schéma zapojenia | Wiring Diagram |
| uloženie potrubia | Pipe Routing |
| zaťaženie snehom | Snow Load |
| zaťaženie vetrom | Wind Load |
| pracovný / pracovné / pracovná | Working (Draft) |
| polyfunkčný objekt | Mixed-use Building |
| Rodinný dom / RODINNÝ DOM | Family House |
| novostavba | New Construction |
| zadanie | Brief / Specification |
| vykaz | Quantity Takeoff |
| strop nad 1NP | Ceiling above 1st Floor |
| oporný múr | Retaining Wall |
| žb stropná doska | RC Floor Slab |
| Bleskozvod | Lightning Conductor |
| Rozvádzač | Distribution Board |
| požiarny projekt | Fire Protection Project |
| Elektroinštalácie | Electrical Installations |
| Energetické hodnotenie | Energy Performance Assessment |
| Vykurovanie | Heating System |
| Zdravotechnika | Plumbing |
| Plyn | Gas |
| zameranie | Survey |

#### Scenario: Material PDF naming preserved

- **WHEN** a file named `001IK26A.material.pdf` is encountered
- **THEN** it is copied as `001IK26A.material.pdf` (unchanged — project code is an identifier)

#### Scenario: Floor Plan + 3D files translated

- **WHEN** a file named `Pôdorys+3D.pdf` is encountered
- **THEN** it is copied as `Floor Plan + 3D.pdf`

#### Scenario: Compound descriptive filenames translated

- **WHEN** a file named `RD Marcinko Cabaj - sprievodná a technická správa.pdf` is encountered
- **THEN** it is copied as `RD Marcinko Cabaj - Cover and Technical Report.pdf`

### Requirement: German file name translation

The system SHALL translate German-language filenames to English. These appear primarily in project `058JO26A - SIPKON_Petruš/Podklady/`.

| German | English |
|---|---|
| Ans / Ansicht | View |
| 3D Ans | 3D View |
| Ans N+W | View N+W |
| Ans S+O | View S+O |
| EG | Ground Floor |
| OG | Upper Floor |
| Schnitt | Section |
| Entwässerung | Drainage |

#### Scenario: German filenames in project 058JO26A translated

- **WHEN** a file named `EG 24.09.25.pdf` is encountered
- **THEN** it is copied as `Ground Floor 24.09.25.pdf`

#### Scenario: German compound filenames translated

- **WHEN** a file named `Entwässerung 24.09.25.pdf` is encountered
- **THEN** it is copied as `Drainage 24.09.25.pdf`

### Requirement: Czech file name translation

The system SHALL translate Czech-language filenames to English. The known Czech term is `Beze jména` (meaning "Untitled"), found in projects 041JO26A and 044AC26A.

| Czech | English |
|---|---|
| Beze jména | Untitled |

#### Scenario: Czech placeholder filename translated

- **WHEN** a file named `Beze jména.dwg` is encountered
- **THEN** it is copied as `Untitled.dwg`

### Requirement: Translation notes file per directory

The system SHALL create a `translation-notes.txt` file in every directory inside `hidden/Trusses AI/`, including the root `hidden/Trusses AI/` directory itself. Each `translation-notes.txt` file SHALL contain:

1. A header line identifying the directory path (relative to `hidden/Trusses AI/`).
2. For each translated item (directory or file) in that directory, one line in the format: `Slovak/German/Czech name → English name`.
3. A note for any items that were NOT translated and why (e.g., project-code prefixes, material PDFs).

#### Scenario: Translation notes in root directory

- **WHEN** the copy process completes
- **THEN** `hidden/Trusses AI/translation-notes.txt` exists
- **AND** it lists all 33 top-level folder translations (e.g., `001IK26A - Matlúch_dom → 001IK26A - Matlúch_House`)

#### Scenario: Translation notes in subdirectory

- **WHEN** the directory `hidden/Trusses AI/001IK26A - Matlúch_House/Supporting Documents/` is created
- **THEN** a `translation-notes.txt` file exists inside it
- **AND** it lists translations for all files in that directory (e.g., `podorys dom.jpg → Floor Plan House.jpg`)

#### Scenario: Translation notes in deeply nested directory

- **WHEN** a deeply nested directory like `hidden/Trusses AI/028IK26A - BigMat Skalica_REDIP/Supporting Documents/RD Moravčík MM/Electrical Installations/` is created
- **THEN** a `translation-notes.txt` file exists inside it listing all translations for that directory

### Requirement: File contents preserved byte-for-byte

The system SHALL copy every file's contents without any modification. The copy SHALL be byte-identical to the original. This applies to all file types: PDF, JPG, PNG, DOCX, XLS, DWG, TXT, and any others.

#### Scenario: PDF contents identical after copy

- **WHEN** a PDF file is copied from source to destination with a translated name
- **THEN** the file contents are byte-identical (verifiable via `diff` or `md5sum`)

#### Scenario: Existing TXT file contents preserved

- **WHEN** a file named `info k CP-návrh väzníka.txt` is copied and renamed
- **THEN** the text file's contents remain exactly as in the original (not translated)

### Requirement: Original directory remains untouched

The system SHALL NOT modify, move, rename, or delete anything inside `hidden/Väzníky AI/` at any point during the process.

#### Scenario: Original directory integrity verified after copy

- **WHEN** the copy process completes
- **THEN** every file in `hidden/Väzníky AI/` has the same checksum as before the process started
- **AND** every directory name in `hidden/Väzníky AI/` is unchanged
- **AND** no new files have been added to `hidden/Väzníky AI/`

### Requirement: Project-code prefixes preserved

The system SHALL preserve the project-code prefix on top-level project folder names. These prefixes follow the pattern `NNNXX26A` or `NNNXX26B` (e.g., `001IK26A`, `033JO26A`, `044AC26A`). Only the descriptive portion after the prefix (following ` - `) SHALL be translated.

#### Scenario: Project code with descriptive name

- **WHEN** a folder named `001IK26A - Matlúch_dom` is encountered
- **THEN** it is copied as `001IK26A - Matlúch_House` (prefix `001IK26A` preserved, `dom` → `House`)

#### Scenario: Project code with no translatable text

- **WHEN** a folder named `032IK26A - Nagy` is encountered
- **THEN** it is copied as `032IK26A - Nagy` (surname, no translation needed)

### Requirement: Empty directories preserved

The system SHALL preserve empty directories in the copy. If a source directory is empty, the corresponding English-named directory SHALL be created (containing only its `translation-notes.txt`).

#### Scenario: Empty Podklady directory copied

- **WHEN** the directory `053IK26B - Plecho_RD Výčapovce/podklady` is empty in the source
- **THEN** the directory `053IK26B - Plecho_RD Výčapovce/Supporting Documents` is created in the destination with only a `translation-notes.txt` inside



## Design

## Context

`hidden/Väzníky AI/` contains 33 roof-truss project folders totaling ~246 MB across ~300 files. Directory and file names are primarily in Slovak, with some German and Czech terms. All files are binary (PDF, JPG, PNG, DOCX, XLS, DWG) or plain text (TXT). The task is to produce an English-named mirror of this tree at `hidden/Trusses AI/` without touching the original.

The authoritative translation glossary lives at `hidden/VAZNIKY_BASIC_OVERVIEW_TRANSLATION.md`. The proposal and specs supplement it with German/Czech translations and specific file-name patterns.

## Goals / Non-Goals

**Goals:**
- Produce a complete, navigable English-named copy of the directory tree.
- Every filesystem entry (directory or file) inside `hidden/Trusses AI/` has an English name.
- Every directory contains a `translation-notes.txt` documenting what was renamed.
- File contents are byte-identical to originals.
- The task is implementable by an autonomous loop without requiring human judgment on individual filenames.

**Non-Goals:**
- No file-content translation.
- No codebase changes (no scripts, no automation, no tooling).
- No git operations (commit decision deferred to human).
- No modification of the original directory.

## Decisions

### Decision 1: Manual per-project execution (no script)

**Choice**: Each project folder is processed one at a time by the implementing agent, using `mkdir -p`, `cp`, and `mv` commands.

**Rationale**: The total tree is 33 projects with ~300 files. Writing and debugging a translation script would take longer than processing each project directly. A script would also need to handle edge cases (compound filenames, mixed languages, ambiguous matches) that are easier to resolve in context. The task is one-shot — once done, the script has no reuse value.

**Alternatives considered**:
- Python/bash translation script: Overkill for a one-shot task. Adds risk of script bugs corrupting the copy. Requires its own testing.
- Bulk `find | rename` pipeline: Too fragile for compound Slovak filenames with diacritics and spaces.

### Decision 2: Directory-first, then files, then notes

**Choice**: Process each project in three ordered phases:
1. Create the full directory structure (all directories, translated names).
2. Copy all files into their translated directory paths with translated filenames.
3. Write `translation-notes.txt` into every directory.

**Rationale**: Creating directories first avoids "file copied to non-existent path" errors. Writing notes last ensures they capture the final state of each directory.

### Decision 3: Translation strategy — exact lookup table, not substring replacement

**Choice**: Build a complete mapping of every filename and directory name in the source tree to its English equivalent. The mapping is resolved per-item (whole-name match), not by replacing Slovak substrings inside compound names.

**Rationale**: Many filenames contain multiple Slovak words mixed with identifiers, dates, and punctuation (e.g., `tapfer_PSP_08_STRECHA.pdf`, `05_RD DH_Chalupiansky_PS_D_SO 01_pôdorys krovu.pdf`). Naive substring replacement would produce garbled results. Whole-name lookup ensures each name is translated correctly in context.

**Implementation approach**: For each file/directory encountered, the agent:
1. Checks if the name appears in the spec's translation tables (exact match, case-insensitive).
2. If not, applies known word-level translations to compound names while preserving structure (dates, identifiers, punctuation).
3. If still ambiguous, preserves the non-translatable portion as-is and notes it in `translation-notes.txt`.

### Decision 4: Project-code prefixes are never translated

**Choice**: The `NNNXX26A/B` prefix (e.g., `001IK26A`, `033JO26A`) at the start of top-level project folder names is treated as an opaque identifier and preserved verbatim. Only the text after ` - ` is considered for translation.

**Rationale**: These codes encode project number, designer initials, year, and variant. They are cross-referenced in the material PDFs and business systems.

### Decision 5: `translation-notes.txt` format

**Choice**: Plain text, one translation per line, with a header:

```
Directory: <relative path from hidden/Trusses AI/>
===
Slovak/German/Czech original → English translation
Slovak/German/Czech original → English translation
[not translated] filename.ext — reason (e.g., project code identifier)
```

**Rationale**: Plain text is universally readable, easy to create with shell commands, and lightweight. The `[not translated]` prefix makes it clear which items were intentionally kept.

### Decision 6: Compound filename translation approach

Many filenames mix translatable words with identifiers, dates, and punctuation. The approach is:

1. **Structured filenames** (e.g., `D2.04 - rez.pdf`, `05_Pôdorys 1.NP.pdf`): Translate the Slovak word(s) while preserving the numbering prefix and extension.
2. **Descriptive filenames** (e.g., `RD Marcinko Cabaj - sprievodná a technická správa.pdf`): Translate the full descriptive portion.
3. **Mixed-language filenames** (e.g., `SK260020 - 01 Pôdorys 1.NP - 24.02.2026.pdf`): Preserve the identifier and date, translate the Slovak words.
4. **Abbreviations** (e.g., `TS`, `RD`, `BD`, `ZTI`, `VYK`, `NP`, `PP`): These are established Slovak engineering abbreviations. Translate to their English equivalents per the glossary (TS → Technical Report, RD → Family House, BD → Apartment Building, NP → Floor, PP → Basement Level).

### Decision 7: Processing order

Process project folders in numerical order (001 → 108) to maintain consistency and make progress tracking straightforward. Within each project, process:
1. `Truss Design Variant A` (and B if present)
2. `Final Design` (if present)
3. `Supporting Documents` and all subdirectories depth-first

## Risks / Trade-offs

**[Risk] Ambiguous or unrecognized Slovak words** → Mitigation: The spec provides an exhaustive translation table covering all known names. Any name not in the table and not decomposable into known words should be preserved as-is and flagged in `translation-notes.txt` with `[not translated — unrecognized]`.

**[Risk] Filename collisions after translation** → Mitigation: Unlikely given the diversity of names, but if two different Slovak names map to the same English name in the same directory, append a numeric suffix (e.g., `_2`).

**[Risk] Disk space (~246 MB)** → Mitigation: Verify available disk space before starting with `df -h hidden/`. If space is insufficient, stop and hand off.

**[Risk] Filesystem encoding issues with diacritics** → Mitigation: All operations use UTF-8. The source directory already exists with these names on the current filesystem, so the encoding is known to work. Use quotes around all paths in shell commands.

**[Trade-off] Manual per-project processing is slower but more reliable** → Each project takes a few minutes to process correctly. A script would be faster to execute but slower to write, test, and debug. For 33 projects, manual is the right trade-off.

**[Trade-off] Some abbreviations kept semi-translated** → Abbreviations like `ARCH`, `ST`, `PDF ARCH` are kept partially as-is because they serve as section headers in the project documentation system. The translation notes will document the full English meaning.

## Rollback

If the copy needs to be discarded:
```bash
rm -rf "hidden/Trusses AI"
```

The original `hidden/Väzníky AI/` is never modified, so no rollback is needed for it.

## Open Questions

None. All translation decisions are resolved in the proposal, spec, and this design document. The implementing agent has complete information to process every known filename and directory name without requiring human input.

## Current Task Context

## Current Task
- 1.1 Verify sufficient disk space — run `df -h hidden/` and confirm at least 300 MB available. Stop and hand off if insufficient.
