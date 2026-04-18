## 1. Discovery and Initial Inventory

- [x] 1.1 Discover all `.md` files in `hidden/Trusses AI/` that need translation. Count the total number of files. Confirm the count is 196. Verify that none of these files have corresponding `_TRANSLATED.md` companions.

**Verify by:** Running `find "hidden/Trusses AI" -name "*.md" -not -name "translation-notes*" -not -name "*_TRANSLATED*" | wc -l` returns 196. Running `find "hidden/Trusses AI" -name "*_TRANSLATED.md" | wc -l` returns 0.

## 2. Translation — Batch 1 (67 files, 3 large projects)

- [x] 2.1 Translate all `.md` files in the following projects. For each source file, create the `_TRANSLATED.md` companion in the same directory and append a reasoning entry to that directory's `translation-notes.txt`.

Projects:
- `064IK26A - LŠ_Greguš` (35 files across 7 directories: `Truss Design Variant A/`, `Supporting Documents/PDF ARCH/`, `PDF Building Services/`, `PDF Electrical/`, `PDF Energy Performance/`, `PDF Fire Protection/`, `PDF Structural Engineering/`)
- `028IK26A - BigMat Skalica_REDIP` (17 files across 6 directories: `Truss Design Variant A/`, `Supporting Documents/Construction Section/`, `RD MORAVCIK MM/Electrical Installations/`, `Fire Protection Project/`, `Heating System/`, `Plumbing/`)
- `046JO26A - Plešivka_Kochan` (15 files across 2 directories: `Truss Design Variant A/`, `Supporting Documents/`)

**Verify by:** Running `find "hidden/Trusses AI/064IK26A - LŠ_Greguš" "hidden/Trusses AI/028IK26A - BigMat Skalica_REDIP" "hidden/Trusses AI/046JO26A - Plešivka_Kochan" -name "*_TRANSLATED.md" | wc -l` returns 67. Each translated file has the same line count as its source. All source `.md` files are byte-identical to before. Every affected directory's `translation-notes.txt` has new `---`-prefixed content-translation entries.

## 3. Translation — Batch 2 (63 files, 5 medium projects)

- [x] 3.1 Translate all `.md` files in the following projects. For each source file, create the `_TRANSLATED.md` companion in the same directory and append a reasoning entry to that directory's `translation-notes.txt`.

Projects:
- `108JO26A - Marcinko` (13 files across 2 directories: `Truss Design Variant A/`, `Supporting Documents/`)
- `035IK26A - Kartik_Tapfer` (12 files across 2 directories: `Truss Design Variant A/`, `Supporting Documents/`)
- `029IK26A - Bigmat Skalica_Zeleňáková` (10 files across 2 directories: `Truss Design Variant A/`, `Supporting Documents/Architecture/`)
- `105IK26A - Hiltonko_Hippová` (8 files across 2 directories: `Truss Design Variant A/`, `Supporting Documents/`)
- `047IK26A - Hiltonko_Valo` (8 files across 2 directories: `Truss Design Variant A/`, `Supporting Documents/`)

**Verify by:** Running `find "hidden/Trusses AI/108JO26A - Marcinko" "hidden/Trusses AI/035IK26A - Kartik_Tapfer" "hidden/Trusses AI/029IK26A - Bigmat Skalica_Zeleňáková" "hidden/Trusses AI/105IK26A - Hiltonko_Hippová" "hidden/Trusses AI/047IK26A - Hiltonko_Valo" -name "*_TRANSLATED.md" | wc -l` returns 63. Each translated file has the same line count as its source. All source `.md` files are byte-identical to before. Every affected directory's `translation-notes.txt` has new content-translation entries.

## 4. Translation — Batch 3 (66 files, 25 remaining projects)

- [x] 4.1 Translate all `.md` files in the following 25 projects. For each source file, create the `_TRANSLATED.md` companion in the same directory and append a reasoning entry to that directory's `translation-notes.txt`.

Projects (file counts in parentheses):
- `083JO26A - SIPKON_Apartment Building Golianovo` (6: `Truss Design Variant A/`, `Supporting Documents/`)
- `058JO26A - SIPKON_Petruš` (6: `Truss Design Variant A/`, `Supporting Documents/`)
- `060JO26B - SIPKON_Belančík` (4: `Truss Design Variant A/`, `Truss Design Variant B/`)
- `057IK26A - Sollár` (4: `Truss Design Variant A/`, `Truss Design Variant B/`)
- `053IK26B - Plecho_Family House Výčapovce` (4: `Truss Design Variant A/`, `Truss Design Variant B/`)
- `034IK26B - Boča_Vyhnálik` (4: `Truss Design Variant A/`, `Truss Design Variant B/`)
- `032IK26A - Nagy` (4: `Truss Design Variant A/`, `Final Design/Proposal/`)
- `027IK26B - BigMat Sumega_Chalupiansky` (4: `Truss Design Variant A/`, `Truss Design Variant B/`)
- `022IK26B - Plecho_Filová` (4: `Truss Design Variant A/`, `Truss Design Variant B/`)
- `003IK26A - BigMat Dinostav_Domanicka` (4: `Truss Design Variant A/`, `Supporting Documents/`)
- `078JO26A - SIPKON_Buocik` (3: `Truss Design Variant A/`, `Supporting Documents/`)
- `044AC26A - Stavmat_CALCUS` (3: `Truss Design Variant A/`, `Supporting Documents/`)
- `041JO26A - EKO-MONT_Mixed-use Building Janíkovce` (3: `Truss Design Variant A/`, `Supporting Documents/`)
- `033JO26A - SIPKON_Mikloš` (3: `Truss Design Variant A/`, `Supporting Documents/`)
- `039JO26A - SIPKON_Lutostav` (3: `Truss Design Variant A/`, `Supporting Documents/`)
- `001IK26A - Matlúch_House` (2: `Truss Design Variant A/`)
- `002IK26A - Matlúch_Garage` (2: `Truss Design Variant A/`)
- `006IK26A - SAKRA Group_Hrušovská` (2: `Truss Design Variant A/`)
- `015IK26A - Slážik_Family House Belince` (2: `Truss Design Variant A/`)
- `040IK26A - Kišš` (2: `Truss Design Variant A/`)
- `043IK26A - BigMat Skalica_Vŕba` (2: `Truss Design Variant A/`)
- `054IK26A - IP Roofs_Čechvala` (2: `Truss Design Variant A/`)
- `056JO26A - Maťko_Ježovský` (2: `Truss Design Variant A/`)
- `062IK26A - Máče` (2: `Truss Design Variant A/`)
- `065IK26A - Bigmat Remot_iTask Int` (2: `Truss Design Variant A/`)

**Verify by:** Running `find "hidden/Trusses AI" -name "*_TRANSLATED.md" | wc -l` returns 196 (cumulative across all 3 batches). Each translated file has the same line count as its source. All 196 source `.md` files are byte-identical to before translation. Every one of the 63 directories with `.md` files has `translation-notes.txt` with content-translation entries.

## 5. Create English-Only Clean Copy

- [x] 5.1 Create a clean copy of the `hidden/Trusses AI/` directory tree at `hidden/Trusses AI English/`. The clean copy MUST contain:
  - The identical directory structure (all 33 project folders and all subdirectories).
  - Every `*_TRANSLATED.md` file, renamed to `.md` by dropping the `_TRANSLATED` suffix (e.g., `001IK26A.material_TRANSLATED.md` becomes `001IK26A.material.md`).
  - Every `translation-notes.txt` file (copied as-is).
  - NOTHING else — no original Slovak/Czech `.md` files, no PDFs, no JPGs, no DWGs, no `_TRANSLATED.md` files (they are renamed).

**Verify by:** `hidden/Trusses AI English/` exists and contains exactly 33 top-level project folders. Running `find "hidden/Trusses AI English" -name "*.md" -not -name "translation-notes*" | wc -l` returns 196. Running `find "hidden/Trusses AI English" -name "translation-notes.txt" | wc -l` returns at least 63 (one per directory with `.md` files). Running `find "hidden/Trusses AI English" -name "*_TRANSLATED.md" | wc -l` returns 0. Running `find "hidden/Trusses AI English" -name "*.pdf" -o -name "*.jpg" -o -name "*.png" -o -name "*.dwg" | wc -l` returns 0. Spot-check 3 files: the content of each `.md` file in the English copy matches the corresponding `_TRANSLATED.md` in the source tree.

## 6. Final Verification

- [x] 6.1 Verify the full pipeline: 196 source `.md` files are unchanged, 196 `_TRANSLATED.md` companions exist in `hidden/Trusses AI/`, `translation-notes.txt` files are updated in all 63 directories, and `hidden/Trusses AI English/` contains only translated Markdown and notes.

**Verify by:** Running `find "hidden/Trusses AI" -name "*_TRANSLATED.md" | wc -l` returns 196. Running `find "hidden/Trusses AI English" -name "*.md" -not -name "translation-notes*" | wc -l` returns 196. For 3 random files, `diff` the source `.md` in `hidden/Trusses AI/` against its pre-translation state shows no differences. For 3 random files, `diff` the `_TRANSLATED.md` in `hidden/Trusses AI/` against the corresponding `.md` in `hidden/Trusses AI English/` shows identical content.
