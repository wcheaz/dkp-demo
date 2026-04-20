## Why

The prior change `2026-04-16-extract-pdfs-to-md` extracted 196 PDFs into Markdown files under `hidden/Trusses AI/`, but the content remains in Slovak and Czech. These `.md` files hold the readable context — material takeoffs, structural load annotations, technical reports, floor-plan notes — that an AI truss-design agent needs. Without English translations, the agent cannot reason over the content. This change translates every extracted `.md` file from Slovak/Czech into English.

## What Changes

- For each of the 196 `.md` files in `hidden/Trusses AI/`, produce a companion `{basename}_TRANSLATED.md` in the same directory containing the full English translation.
- Append per-file translation reasoning to the existing `translation-notes.txt` in the same directory (these files already exist in all 63 directories from the prior `vazniky-english-copy` change).
- No script is required. The agent reads each source `.md`, translates the Slovak/Czech text to English inline, writes the companion `_TRANSLATED.md`, and appends a reasoning note to the nearby `translation-notes.txt`.
- A clean copy of the full `hidden/Trusses AI/` directory tree at `hidden/Trusses AI English/` containing only the translated `_TRANSLATED.md` files (renamed back to `.md` without the suffix), `translation-notes.txt` files, and the directory structure — no original Slovak/Czech `.md` files, no PDFs, no images, no other files.

## Capabilities

### New Capabilities

- `md-translation`: Translates Slovak/Czech Markdown files into English by producing companion `*_TRANSLATED.md` files and recording reasoning in nearby `translation-notes.txt` files.
- `english-only-copy`: Creates a clean copy of the `hidden/Trusses AI/` tree at `hidden/Trusses AI English/` containing only translated Markdown and translation notes.

### Modified Capabilities

_(none)_

## Impact

- **Disk space**: Each `_TRANSLATED.md` is roughly the same size as its source (English text is comparable in length to Slovak/Czech). 196 files at ~5 KB each ≈ ~1 MB added. The `hidden/Trusses AI English/` clean copy adds another ~1 MB.
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
8. After all translations are complete, create a clean copy of the directory tree at `hidden/Trusses AI English/` containing only `_TRANSLATED.md` files (renamed to `.md` by dropping the `_TRANSLATED` suffix) and `translation-notes.txt` files. No original `.md` files, no PDFs, no images, no other files are copied.

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
- [ ] `hidden/Trusses AI English/` exists as a clean copy with the same directory structure, containing 196 `.md` files (translations renamed from `_TRANSLATED.md` to `.md`) and corresponding `translation-notes.txt` files. No PDFs, images, or untranslated `.md` files are present.

## Human Handoff Items

1. **Review translated Markdown**: Spot-check `_TRANSLATED.md` files for translation accuracy, especially technical terms (load values, structural terminology, construction vocabulary).
2. **Git commit decision**: Decide whether to commit the generated `_TRANSLATED.md` files and updated `translation-notes.txt` files.
