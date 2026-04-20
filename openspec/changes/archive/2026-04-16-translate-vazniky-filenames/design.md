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
