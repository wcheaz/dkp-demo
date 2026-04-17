## 1. Discovery and Initial Inventory

- [x] 1.1 Discover all `.md` files in `hidden/Trusses AI/` that need translation. Count the total number of files. Confirm the count is 196. Verify that none of these files have corresponding `_TRANSLATED.md` companions.

**Verify by:** Running `find "hidden/Trusses AI" -name "*.md" -not -name "translation-notes*" -not -name "*_TRANSLATED*" | wc -l` returns 196. Running `find "hidden/Trusses AI" -name "*_TRANSLATED.md" | wc -l` returns 0.

## 2. Translation by Project

For each of the 33 project folders, translate all `.md` files in that project's directories and update the corresponding `translation-notes.txt` files.

- [x] 2.1 Translate all `.md` files in project `001IK26A - Matlúch_House` (directories: `Truss Design Variant A/`). For each file, create the `_TRANSLATED.md` companion and append reasoning entries to both directories' `translation-notes.txt` files.

**Verify by:** The project contains exactly 2 `.md` files (`001IK26A.material.md`, `Floor Plan + 3D.md`). After translation, exactly 2 `_TRANSLATED.md` files exist. Each `_TRANSLATED.md` has the same line count and Markdown structure as its source. The `translation-notes.txt` in `Truss Design Variant A/` has a new `---`-prefixed entry for each file.

- [x] 2.2 Translate all `.md` files in project `002IK26A - Matlúch_Garage` (directory: `Truss Design Variant A/`). For each file, create the `_TRANSLATED.md` companion and append reasoning entries to the `translation-notes.txt` file.

**Verify by:** The project contains exactly 2 `.md` files. After translation, exactly 2 `_TRANSLATED.md` files exist. Source files are byte-identical to before translation. The `translation-notes.txt` has entries for both files.

- [x] 2.3 Translate all `.md` files in project `003IK26A - BigMat Dinostav_Domanicka` (directories: `Truss Design Variant A/`, `Supporting Documents/`). For each file across both directories, create the `_TRANSLATED.md` companions and append reasoning entries to each directory's `translation-notes.txt` file.

**Verify by:** The project contains exactly 3 `.md` files (2 in `Truss Design Variant A/`, 1 in `Supporting Documents/`). After translation, exactly 3 `_TRANSLATED.md` files exist, one per source in the same directories. Both `translation-notes.txt` files have new entries.

- [x] 2.4 Translate all `.md` files in project `006IK26A - SAKRA Group_Hrušovská` (directory: `Truss Design Variant A/`). Create the `_TRANSLATED.md` companions and append reasoning entries to the `translation-notes.txt` file.

**Verify by:** The project contains exactly 2 `.md` files. After translation, exactly 2 `_TRANSLATED.md` files exist with matching line counts and structure. Source files unchanged.

- [x] 2.5 Translate all `.md` files in project `015IK26A - Slážik_Family House Belince` (directory: `Truss Design Variant A/`). Create the `_TRANSLATED.md` companions and append reasoning entries to the `translation-notes.txt` file.

**Verify by:** The project contains exactly 2 `.md` files. After translation, exactly 2 `_TRANSLATED.md` files exist with matching line counts and structure. Source files unchanged.

- [x] 2.6 Translate all `.md` files in project `022IK26B - Plecho_Filová` (directories: `Truss Design Variant A/`, `Truss Design Variant B/`). Create the `_TRANSLATED.md` companions and append reasoning entries to both directories' `translation-notes.txt` files.

**Verify by:** The project contains exactly 4 `.md` files (2 in each variant directory). After translation, exactly 4 `_TRANSLATED.md` files exist. Source files unchanged. Both `translation-notes.txt` files have entries.

- [x] 2.7 Translate all `.md` files in project `027IK26B - BigMat Sumega_Chalupiansky` (directories: `Truss Design Variant A/`, `Truss Design Variant B/`). Create the `_TRANSLATED.md` companions and append reasoning entries to both directories' `translation-notes.txt` files.

**Verify by:** The project contains exactly 4 `.md` files (2 in each variant directory). After translation, exactly 4 `_TRANSLATED.md` files exist with matching line counts and structure. Source files unchanged. Both `translation-notes.txt` files have entries.

- [x] 2.8 Translate all `.md` files in project `028IK26A - BigMat Skalica_REDIP` (directories: `Truss Design Variant A/`, `Supporting Documents/`, and 6 subdirectories under `Supporting Documents/`). Create the `_TRANSLATED.md` companions and append reasoning entries to all 8 directories' `translation-notes.txt` files.

**Verify by:** The project contains 17 `.md` files across 6 directories (Truss Design Variant A, Construction Section, Electrical Installations, Fire Protection Project, Heating System, Plumbing). After translation, exactly 17 `_TRANSLATED.md` files exist, one per source in the same directories. All 6 `translation-notes.txt` files have new entries. All line counts match between source and translated files.

- [x] 2.9 Translate all `.md` files in project `029IK26A - Bigmat Skalica_Zeleňáková` (directories: `Truss Design Variant A/`, `Supporting Documents/`, and 2 subdirectories under `Supporting Documents/`). Create the `_TRANSLATED.md` companions and append reasoning entries to all 4 directories' `translation-notes.txt` files.

**Verify by:** The project contains 10 `.md` files across 2 directories with `.md` files (Truss Design Variant A: 2, Supporting Documents/Architecture: 8). All 10 `_TRANSLATED.md` files exist with matching line counts. Both `translation-notes.txt` files have content-translation entries.

- [x] 2.10 Translate all `.md` files in project `032IK26A - Nagy` (directories: `Truss Design Variant A/`, `Final Design/Proposal/`). Create the `_TRANSLATED.md` companions and append reasoning entries to both directories' `translation-notes.txt` files.

**Verify by:** The project contains exactly 2 `.md` files (1 in each directory). After translation, exactly 2 `_TRANSLATED.md` files exist with matching line counts and structure. Source files unchanged. Both `translation-notes.txt` files have entries.

- [x] 2.11 Translate all `.md` files in project `033JO26A - SIPKON_Mikloš` (directories: `Truss Design Variant A/`, `Supporting Documents/`). Create the `_TRANSLATED.md` companions and append reasoning entries to both directories' `translation-notes.txt` files.

**Verify by:** The project contains exactly 3 `.md` files (2 in `Truss Design Variant A/`, 1 in `Supporting Documents/`). After translation, exactly 3 `_TRANSLATED.md` files exist. Both `translation-notes.txt` files have entries.

- [x] 2.12 Translate all `.md` files in project `034IK26B - Boča_Vyhnálik` (directories: `Truss Design Variant A/`, `Truss Design Variant B/`). Create the `_TRANSLATED.md` companions and append reasoning entries to both directories' `translation-notes.txt` files.

**Verify by:** The project contains exactly 4 `.md` files (2 in each variant directory). After translation, exactly 4 `_TRANSLATED.md` files exist with matching line counts and structure. Source files unchanged. Both `translation-notes.txt` files have entries.

- [x] 2.13 Translate all `.md` files in project `035IK26A - Kartik_Tapfer` (directories: `Truss Design Variant A/`, `Supporting Documents/`). Create the `_TRANSLATED.md` companions and append reasoning entries to both directories' `translation-notes.txt` files.

**Verify by:** The project contains exactly 3 `.md` files (2 in `Truss Design Variant A/`, 1 in `Supporting Documents/`). After translation, exactly 3 `_TRANSLATED.md` files exist. Both `translation-notes.txt` files have entries.

- [ ] 2.14 Translate all `.md` files in project `039JO26A - SIPKON_Lutostav` (directories: `Truss Design Variant A/`, `Supporting Documents/`). Create the `_TRANSLATED.md` companions and append reasoning entries to both directories' `translation-notes.txt` files.

**Verify by:** The project contains exactly 3 `.md` files (2 in `Truss Design Variant A/`, 1 in `Supporting Documents/`). After translation, exactly 3 `_TRANSLATED.md` files exist. Both `translation-notes.txt` files have entries.

- [ ] 2.15 Translate all `.md` files in project `040IK26A - Kišš` (directory: `Truss Design Variant A/`). Create the `_TRANSLATED.md` companion and append reasoning entry to the `translation-notes.txt` file.

**Verify by:** The project contains exactly 2 `.md` files. After translation, exactly 2 `_TRANSLATED.md` files exist with matching line counts and structure. Source files unchanged.

- [ ] 2.16 Translate all `.md` files in project `041JO26A - EKO-MONT_Mixed-use Building Janíkovce` (directories: `Truss Design Variant A/`, `Supporting Documents/`). Create the `_TRANSLATED.md` companions and append reasoning entries to both directories' `translation-notes.txt` files.

**Verify by:** The project contains exactly 3 `.md` files (2 in `Truss Design Variant A/`, 1 in `Supporting Documents/`). After translation, exactly 3 `_TRANSLATED.md` files exist. Both `translation-notes.txt` files have entries.

- [ ] 2.17 Translate all `.md` files in project `043IK26A - BigMat Skalica_Vŕba` (directory: `Truss Design Variant A/`). Create the `_TRANSLATED.md` companions and append reasoning entry to the `translation-notes.txt` file.

**Verify by:** The project contains exactly 2 `.md` files. After translation, exactly 2 `_TRANSLATED.md` files exist with matching line counts and structure. Source files unchanged.

- [ ] 2.18 Translate all `.md` files in project `044AC26A - Stavmat_CALCUS` (directories: `Truss Design Variant A/`, `Supporting Documents/`). Create the `_TRANSLATED.md` companions and append reasoning entries to both directories' `translation-notes.txt` files.

**Verify by:** The project contains exactly 3 `.md` files (2 in `Truss Design Variant A/`, 1 in `Supporting Documents/`). After translation, exactly 3 `_TRANSLATED.md` files exist. Both `translation-notes.txt` files have entries.

- [ ] 2.19 Translate all `.md` files in project `046JO26A - Plešivka_Kochan` (directories: `Truss Design Variant A/`, `Supporting Documents/`). Create the `_TRANSLATED.md` companions and append reasoning entries to both directories' `translation-notes.txt` files.

**Verify by:** The project contains 15 `.md` files (2 in `Truss Design Variant A/`, 13 in `Supporting Documents/`). After translation, exactly 15 `_TRANSLATED.md` files exist across both directories. Both `translation-notes.txt` files have entries for each file.

- [ ] 2.20 Translate all `.md` files in project `047IK26A - Hiltonko_Valo` (directories: `Truss Design Variant A/`, `Supporting Documents/`). Create the `_TRANSLATED.md` companions and append reasoning entries to both directories' `translation-notes.txt` files.

**Verify by:** The project contains exactly 3 `.md` files (2 in `Truss Design Variant A/`, 1 in `Supporting Documents/`). After translation, exactly 3 `_TRANSLATED.md` files exist. Both `translation-notes.txt` files have entries.

- [ ] 2.21 Translate all `.md` files in project `053IK26B - Plecho_Family House Výčapovce` (directories: `Truss Design Variant A/`, `Truss Design Variant B/`). Create the `_TRANSLATED.md` companions and append reasoning entries to both directories' `translation-notes.txt` files.

**Verify by:** The project contains exactly 4 `.md` files (2 in each variant directory). After translation, exactly 4 `_TRANSLATED.md` files exist with matching line counts and structure. Source files unchanged. Both `translation-notes.txt` files have entries.

- [ ] 2.22 Translate all `.md` files in project `054IK26A - IP Roofs_Čechvala` (directory: `Truss Design Variant A/`). Create the `_TRANSLATED.md` companions and append reasoning entry to the `translation-notes.txt` file.

**Verify by:** The project contains exactly 2 `.md` files. After translation, exactly 2 `_TRANSLATED.md` files exist with matching line counts and structure. Source files unchanged.

- [ ] 2.23 Translate all `.md` files in project `056JO26A - Maťko_Ježovský` (directory: `Truss Design Variant A/`). Create the `_TRANSLATED.md` companions and append reasoning entry to the `translation-notes.txt` file.

**Verify by:** The project contains exactly 2 `.md` files. After translation, exactly 2 `_TRANSLATED.md` files exist with matching line counts and structure. Source files unchanged.

- [ ] 2.24 Translate all `.md` files in project `057IK26A - Sollár` (directories: `Truss Design Variant A/`, `Truss Design Variant B/`). Create the `_TRANSLATED.md` companions and append reasoning entries to both directories' `translation-notes.txt` files.

**Verify by:** The project contains exactly 4 `.md` files (2 in each variant directory). After translation, exactly 4 `_TRANSLATED.md` files exist with matching line counts and structure. Source files unchanged. Both `translation-notes.txt` files have entries.

- [ ] 2.25 Translate all `.md` files in project `058JO26A - SIPKON_Petruš` (directories: `Truss Design Variant A/`, `Supporting Documents/`). Create the `_TRANSLATED.md` companions and append reasoning entries to both directories' `translation-notes.txt` files.

**Verify by:** The project contains exactly 3 `.md` files (2 in `Truss Design Variant A/`, 1 in `Supporting Documents/`). After translation, exactly 3 `_TRANSLATED.md` files exist. Both `translation-notes.txt` files have entries.

- [ ] 2.26 Translate all `.md` files in project `060JO26B - SIPKON_Belančík` (directories: `Truss Design Variant A/`, `Truss Design Variant B/`). Create the `_TRANSLATED.md` companions and append reasoning entries to both directories' `translation-notes.txt` files.

**Verify by:** The project contains exactly 4 `.md` files (2 in each variant directory). After translation, exactly 4 `_TRANSLATED.md` files exist with matching line counts and structure. Source files unchanged. Both `translation-notes.txt` files have entries.

- [ ] 2.27 Translate all `.md` files in project `062IK26A - Máče` (directory: `Truss Design Variant A/`). Create the `_TRANSLATED.md` companions and append reasoning entry to the `translation-notes.txt` file.

**Verify by:** The project contains exactly 2 `.md` files. After translation, exactly 2 `_TRANSLATED.md` files exist with matching line counts and structure. Source files unchanged.

- [ ] 2.28 Translate all `.md` files in project `064IK26A - LŠ_Greguš` (directories: `Truss Design Variant A/`, `Supporting Documents/`, and 5 subdirectories under `Supporting Documents/`). Create the `_TRANSLATED.md` companions and append reasoning entries to all 7 directories' `translation-notes.txt` files.

**Verify by:** The project contains 29 `.md` files across 7 directories (2 in `Truss Design Variant A/`, 27 in 6 `Supporting Documents/` subdirectories). After translation, exactly 29 `_TRANSLATED.md` files exist. All 7 `translation-notes.txt` files have entries.

- [ ] 2.29 Translate all `.md` files in project `065IK26A - Bigmat Remot_iTask Int` (directory: `Truss Design Variant A/`). Create the `_TRANSLATED.md` companions and append reasoning entry to the `translation-notes.txt` file.

**Verify by:** The project contains exactly 2 `.md` files. After translation, exactly 2 `_TRANSLATED.md` files exist with matching line counts and structure. Source files unchanged.

- [ ] 2.30 Translate all `.md` files in project `078JO26A - SIPKON_Buocik` (directories: `Truss Design Variant A/`, `Supporting Documents/`). Create the `_TRANSLATED.md` companions and append reasoning entries to both directories' `translation-notes.txt` files.

**Verify by:** The project contains exactly 3 `.md` files (2 in `Truss Design Variant A/`, 1 in `Supporting Documents/`). After translation, exactly 3 `_TRANSLATED.md` files exist. Both `translation-notes.txt` files have entries.

- [ ] 2.31 Translate all `.md` files in project `083JO26A - SIPKON_Apartment Building Golianovo` (directories: `Truss Design Variant A/`, `Supporting Documents/`). Create the `_TRANSLATED.md` companions and append reasoning entries to both directories' `translation-notes.txt` files.

**Verify by:** The project contains exactly 3 `.md` files (2 in `Truss Design Variant A/`, 1 in `Supporting Documents/`). After translation, exactly 3 `_TRANSLATED.md` files exist. Both `translation-notes.txt` files have entries.

- [ ] 2.32 Translate all `.md` files in project `105IK26A - Hiltonko_Hippová` (directories: `Truss Design Variant A/`, `Supporting Documents/`). Create the `_TRANSLATED.md` companions and append reasoning entries to both directories' `translation-notes.txt` files.

**Verify by:** The project contains exactly 3 `.md` files (2 in `Truss Design Variant A/`, 1 in `Supporting Documents/`). After translation, exactly 3 `_TRANSLATED.md` files exist. Both `translation-notes.txt` files have entries.

- [ ] 2.33 Translate all `.md` files in project `108JO26A - Marcinko` (directories: `Truss Design Variant A/`, `Supporting Documents/`). Create the `_TRANSLATED.md` companions and append reasoning entries to both directories' `translation-notes.txt` files.

**Verify by:** The project contains exactly 3 `.md` files (2 in `Truss Design Variant A/`, 1 in `Supporting Documents/`). After translation, exactly 3 `_TRANSLATED.md` files exist. Both `translation-notes.txt` files have entries.

## 3. Final Verification

- [ ] 3.1 Verify that all 196 `.md` files have corresponding `_TRANSLATED.md` companions. Verify that no source `.md` file was modified (byte-identical to before). Verify that every directory with `.md` files has an updated `translation-notes.txt` with content-translation entries.

**Verify by:** Running `find "hidden/Trusses AI" -name "*.md" -not -name "translation-notes*" -not -name "*_TRANSLATED*" | wc -l` returns 196. Running `find "hidden/Trusses AI" -name "*_TRANSLATED.md" | wc -l` returns 196. For 3 random directories, `diff` the source `.md` file against its pre-translation backup shows no differences. Each directory's `translation-notes.txt` contains at least one `---`-prefixed content-translation entry.
