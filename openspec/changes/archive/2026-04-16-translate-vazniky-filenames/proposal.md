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
