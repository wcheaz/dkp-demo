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
