## 1. Prerequisites and Root Directory

- [x] 1.1 Verify sufficient disk space — run `df -h hidden/` and confirm at least 300 MB available. Stop and hand off if insufficient.
- [x] 1.2 Create root destination directory — run `mkdir -p "hidden/Trusses AI"` and verify it exists.

**Done when**: Directory `hidden/Trusses AI/` exists and disk space is confirmed sufficient.
**Verify by**: `ls -la hidden/ | grep "Trusses AI"` and `df -h hidden/`.

## 2. Simple Projects — 001, 002, 003, 006, 015

For each project below: create translated directory structure, copy files with translated names, write `translation-notes.txt` in every new directory. All files use `cp` (byte-for-byte copy). The standard subdirectory translations are: `Návrh väzníka A` → `Truss Design Variant A`, `Podklady`/`podklady` → `Supporting Documents`, `Pôdorys+3D.pdf` → `Floor Plan + 3D.pdf`. Project-code prefixes (`001IK26A - `, etc.) are preserved verbatim. `N.material.pdf` files are copied without renaming.

### 001IK26A - Matlúch_dom → 001IK26A - Matlúch_House

Dirs: `Truss Design Variant A`, `Supporting Documents`

Files in Truss Design Variant A:
- `001IK26A.material.pdf` → `001IK26A.material.pdf` (unchanged)
- `Pôdorys+3D.pdf` → `Floor Plan + 3D.pdf`

Files in Supporting Documents:
- `podorys dom.jpg` → `Floor Plan House.jpg`
- `podorys strechy domu.jpg` → `Floor Plan House Roof.jpg`
- `pohlady dom 1.jpg` → `Elevations House 1.jpg`
- `pohlady dom 2.jpg` → `Elevations House 2.jpg`
- `rez dom1.jpg` → `Section House 1.jpg`
- `rez dom2.jpg` → `Section House 2.jpg`

### 002IK26A - Matlúch_garáž → 002IK26A - Matlúch_Garage

Dirs: `Truss Design Variant A`, `Supporting Documents`

Files in Truss Design Variant A:
- `002IK26A.material.pdf` → `002IK26A.material.pdf` (unchanged)
- `Pôdorys+3D.pdf` → `Floor Plan + 3D.pdf`

Files in Supporting Documents:
- `podorys strechy garaz.jpg` → `Floor Plan Roof Garage.jpg`
- `pohlady garaz.jpg` → `Elevations Garage.jpg`
- `rez garaz.jpg` → `Section Garage.jpg`

### 003IK26A - BigMat Dinostav_Domanicka → 003IK26A - BigMat Dinostav_Domanická

Dirs: `Truss Design Variant A`, `Supporting Documents`

Files in Truss Design Variant A:
- `003IK26A.material.pdf` → `003IK26A.material.pdf` (unchanged)
- `Pôdorys+3D.pdf` → `Floor Plan + 3D.pdf`

Files in Supporting Documents:
- `Domanicka_RD_Krov_790_297.pdf` → `Domanická_RD_Roof Framing_790_297.pdf`
- `Domanicka_RD_Pdorys strechy_670_297.pdf` → `Domanická_RD_Floor Plan Roof_670_297.pdf`
- `info k CP-návrh väzníka.txt` → `Info for Truss Design.txt` (contents NOT translated)

### 006IK26A - SAKRA Group_Hrušovská → 006IK26A - SAKRA Group_Hrušovská

Dirs: `Truss Design Variant A`, `Supporting Documents`

Files in Truss Design Variant A:
- `006IK26A.material.pdf` → `006IK26A.material.pdf` (unchanged)
- `Pôdorys+3D.pdf` → `Floor Plan + 3D.pdf`

Files in Supporting Documents:
- `vaznikhrusovska.pdf` → `Truss Hrušovská.pdf`

### 015IK26A - Slážik_RD Belince → 015IK26A - Slážik_Family House Belince

Dirs: `Truss Design Variant A`, `Supporting Documents`

Files in Truss Design Variant A:
- `015IK26A.material.pdf` → `015IK26A.material.pdf` (unchanged)
- `Pôdorys+3D.pdf` → `Floor Plan + 3D.pdf`

Files in Supporting Documents:
- `Nový textový dokument.txt` → `New Text Document.txt` (contents NOT translated)

- [x] 2.1 Process project 001 — create dirs, copy files with translated names, write translation-notes.txt in both subdirectories.
- [x] 2.2 Process project 002 — create dirs, copy files with translated names, write translation-notes.txt in both subdirectories.
- [x] 2.3 Process project 003 — create dirs, copy files with translated names, write translation-notes.txt in both subdirectories.
- [x] 2.4 Process project 006 — create dirs, copy files with translated names, write translation-notes.txt in both subdirectories.
- [x] 2.5 Process project 015 — create dirs, copy files with translated names, write translation-notes.txt in both subdirectories.
- [x] 2.6 Verify batch — confirm 5 project folders exist in `hidden/Trusses AI/`, spot-check 3 files with `diff` against originals.

**Done when**: All 5 project folders exist with correct English names, all subdirectories contain translated files and `translation-notes.txt`.
**Verify by**: `ls "hidden/Trusses AI/" | grep -c "IK26\|JO26\|AC26"` returns 5, and `diff "hidden/Väzníky AI/001IK26A - Matlúch_dom/Návrh väzníka A/001IK26A.material.pdf" "hidden/Trusses AI/001IK26A - Matlúch_House/Truss Design Variant A/001IK26A.material.pdf"` shows no differences.

## 3. Two-Variant Projects — 022, 027, 034

These projects have two design variants (A and B). Directory `Návrh väzníka A` → `Truss Design Variant A`, `Návrh väzníka B` → `Truss Design Variant B`. Each variant contains `N.material.pdf` (unchanged) and `Pôdorys+3D.pdf` → `Floor Plan + 3D.pdf`.

### 022IK26B - Plecho_Filová → 022IK26B - Plecho_Filová

Dirs: `Truss Design Variant A`, `Truss Design Variant B`

Files in Truss Design Variant A:
- `022IK26A.material.pdf` → `022IK26A.material.pdf` (unchanged)
- `Pôdorys+3D.pdf` → `Floor Plan + 3D.pdf`

Files in Truss Design Variant B:
- `022IK26B.material.pdf` → `022IK26B.material.pdf` (unchanged)
- `Pôdorys+3D.pdf` → `Floor Plan + 3D.pdf`

Root-level files:
- `zameranie.jpg` → `Survey.jpg`

### 027IK26B - BigMat Sumega_Chalupiansky → 027IK26B - BigMat Sumega_Chalupiansky

Dirs: `Truss Design Variant A`, `Truss Design Variant B`, `Supporting Documents`

Files in Truss Design Variant A:
- `027IK26A.material.pdf` → `027IK26A.material.pdf` (unchanged)
- `Pôdorys+3D.pdf` → `Floor Plan + 3D.pdf`

Files in Truss Design Variant B:
- `027IK26B.material.pdf` → `027IK26B.material.pdf` (unchanged)
- `Pôdorys+3D.pdf` → `Floor Plan + 3D.pdf`

Files in Supporting Documents:
- `02_RD DH_Chalupiansky_PS_D_SO 01_pôdorys 1.NP.pdf` → `02_RD DH_Chalupiansky_PS_D_SO 01_Floor Plan 1st Floor.pdf`
- `03_RD DH_Chalupiansky_PS_D_SO 01_pôdorys krovu.pdf` → `03_RD DH_Chalupiansky_PS_D_SO 01_Floor Plan Roof Framing.pdf`
- `04_RD DH_Chalupiansky_PS_D_SO 01_pôdorys strechy.pdf` → `04_RD DH_Chalupiansky_PS_D_SO 01_Floor Plan Roof.pdf`
- `05_RD DH_Chalupiansky_PS_D_SO 01_rez A rez B.pdf` → `05_RD DH_Chalupiansky_PS_D_SO 01_Section A Section B.pdf`

### 034IK26B - Boča_Vyhnálik → 034IK26B - Boča_Vyhnálik

Dirs: `Truss Design Variant A`, `Truss Design Variant B`, `Supporting Documents`

Files in Truss Design Variant A:
- `034IK26A.material.pdf` → `034IK26A.material.pdf` (unchanged)
- `Pôdorys+3D.pdf` → `Floor Plan + 3D.pdf`

Files in Truss Design Variant B:
- `034IK26B.material.pdf` → `034IK26B.material.pdf` (unchanged)
- `Pôdorys+3D.pdf` → `Floor Plan + 3D.pdf`

Files in Supporting Documents:
- `pôdorys.jpg` → `Floor Plan.jpg`
- `rez.jpg` → `Section.jpg`
- `strecha.jpg` → `Roof.jpg`

- [x] 3.1 Process project 022 — create dirs, copy files with translated names, write translation-notes.txt in all directories (including root level of the project).
- [x] 3.2 Process project 027 — create dirs, copy files with translated names, write translation-notes.txt in all directories.
- [x] 3.3 Process project 034 — create dirs, copy files with translated names, write translation-notes.txt in all directories.
- [x] 3.4 Verify batch — confirm 3 more project folders exist (total 8), spot-check 2 files with `diff`.

**Done when**: 8 project folders total in `hidden/Trusses AI/`, each with correct variant directories and translated filenames.
**Verify by**: `ls "hidden/Trusses AI/" | wc -l` returns 8.

## 4. Deeply Nested Projects — 028, 029

These projects have deeper directory structures requiring careful nested directory creation.

### 028IK26A - BigMat Skalica_REDIP → 028IK26A - BigMat Skalica_REDIP

Dir structure:
```
028IK26A - BigMat Skalica_REDIP/
├── Truss Design Variant A/
│   ├── 028IK26A.material.pdf (unchanged)
│   └── Floor Plan + 3D.pdf
└── Supporting Documents/
    ├── Construction Section/
    │   ├── RD MM_E1.pdf (unchanged)
    │   ├── RD MM_E2.pdf (unchanged)
    │   ├── RD MM_E3.pdf (unchanged)
    │   ├── RD MM_E4.pdf (unchanged)
    │   ├── RD MM_E5.pdf (unchanged)
    │   ├── RD MM_S1.pdf (unchanged)
    │   └── TS - RODINNÝ DOM   MM JAKUBOV.pdf → Technical Report - Family House MM Jakubov.pdf
    └── RD MORAVCIK MM/
        ├── Electrical Installations/
        │   ├── RD MM-BLESKOZVOD (1).pdf → RD MM-Lightning Conductor (1).pdf
        │   ├── RD MM-OBALKA (1).pdf → RD MM-Envelope (1).pdf
        │   ├── RD MM-PODORYS 1NP (2).pdf → RD MM-Floor Plan 1st Floor (2).pdf
        │   ├── RD MM-ROZVÁDZAČ RH (1).pdf → RD MM-Distribution Board RH (1).pdf
        │   └── RD MM-TS (1).pdf → RD MM-Technical Report (1).pdf
        ├── Energy Performance Assessment/
        │   └── 25074.docx (unchanged)
        ├── Fire Protection Project/
        │   ├── PO.01 Situácia_RD MM.pdf → PO.01 Site Plan_RD MM.pdf
        │   ├── PO.02 PÔDORYS 1.NP_RD MM.pdf → PO.02 Floor Plan 1st Floor_RD MM.pdf
        │   ├── Tit_RD MM.pdf → Title Page_RD MM.pdf
        │   └── TS_RD MM.pdf → Technical Report_RD MM.pdf
        ├── Heating System/
        │   ├── 1np-uk (3).pdf → 1st Floor Layout (3).pdf
        │   ├── 25074.docx (unchanged)
        │   └── Schema-uk (8).pdf → Schema Layout (8).pdf
        └── Plumbing/
            ├── RD MM JAKUBOV ZTI PODORYS .pdf → RD MM Jakubov Plumbing Floor Plan.pdf
            ├── RD MM JAKUBOV ZTI SITUÁCIA.pdf → RD MM Jakubov Plumbing Site Plan.pdf
            └── TS ZTI RD MM.pdf → Technical Report Plumbing RD MM.pdf
```

### 029IK26A - Bigmat Skalica_Zeleňáková → 029IK26A - Bigmat Skalica_Zeleňáková

Dir structure:
```
029IK26A - Bigmat Skalica_Zeleňáková/
├── Truss Design Variant A/
│   ├── 029IK26A.material.pdf (unchanged)
│   └── Floor Plan + 3D.pdf
└── Supporting Documents/
    ├── Architecture/
    │   ├── 01_Pôdorys základov.pdf → 01_Floor Plan Foundations.pdf
    │   ├── 02_Pôdorys 1.NP.pdf → 02_Floor Plan 1st Floor.pdf
    │   ├── 03_Pôdorys 2.NP.pdf → 03_Floor Plan 2nd Floor.pdf
    │   ├── 04_Pôdorys strechy.pdf → 04_Floor Plan Roof.pdf
    │   ├── 05_Rezy AA, BB.pdf → 05_Sections AA, BB.pdf
    │   ├── 06_Pohľady.pdf → 06_Elevations.pdf
    │   ├── Koordinačná situácia.pdf → Coordination Site Plan.pdf
    │   ├── SS_RD Studienka.pdf → Summary Report_RD Studienka.pdf
    │   ├── Štítok ARCH.pdf → Label ARCH.pdf
    │   ├── Štítok hl.pdf → Label Main.pdf
    │   └── TS_RD Zeleňáková.pdf → Technical Report_RD Zeleňáková.pdf
    └── Structural Assessment/
        └── Statický posudok - RD Zeleňáková (1).pdf → Structural Assessment - RD Zeleňáková (1).pdf
```

- [x] 4.1 Process project 028 — create full nested directory structure, copy all files with translated names, write translation-notes.txt in every directory (7 directories total including project root).
- [x] 4.2 Process project 029 — create full nested directory structure, copy all files with translated names, write translation-notes.txt in every directory (4 directories total).
- [x] 4.3 Verify batch — confirm 10 project folders total. Spot-check `diff` on `028IK26A.material.pdf` and `Statický posudok - RD Zeleňáková (1).pdf`.

**Done when**: Projects 028 and 029 fully nested structures exist with all files translated and notes in every directory.
**Verify by**: `find "hidden/Trusses AI/028IK26A - BigMat Skalica_REDIP/" -type f -name "translation-notes.txt" | wc -l` returns 7 (one per directory).

## 5. Mid-Complexity Projects — 032, 033, 035, 039, 040

### 032IK26A - Nagy → 032IK26A - Nagy

Dir structure:
```
032IK26A - Nagy/
├── Final Design/
│   └── Proposal/
│       ├── 032IK26A.material.pdf (unchanged)
│       └── Floor Plan + 3D.pdf
├── Truss Design Variant A/
│   ├── 032IK26A.material.pdf (unchanged)
│   └── Floor Plan + 3D.pdf
└── Supporting Documents/
    └── viber_image_2026-02-02_11-31-29-620.jpg (unchanged)
```

### 033JO26A - SIPKON_Mikloš → 033JO26A - SIPKON_Mikloš

Dir structure:
```
033JO26A - SIPKON_Mikloš/
├── Truss Design Variant A/
│   ├── 033JO26A.material.pdf (unchanged)
│   └── 033JO26A_Pôdorys + 3D.pdf → 033JO26A_Floor Plan + 3D.pdf
└── Supporting Documents/
    ├── 033JO26A.txt (unchanged, contents NOT translated)
    ├── 04 Pďdorys.pdf → 04 Floor Plan.pdf
    ├── 05 rez.pdf → 05 Section.pdf
    └── 08 pohĖady.pdf → 08 Elevations.pdf
```

### 035IK26A - Kartik_Tapfer → 035IK26A - Kartik_Tapfer

Dir structure:
```
035IK26A - Kartik_Tapfer/
├── Truss Design Variant A/
│   ├── 035IK26A.material.pdf (unchanged)
│   └── Floor Plan + 3D.pdf
└── Supporting Documents/
    ├── pôdorys strechy.jpg → Floor Plan Roof.jpg
    ├── pohlady 1.pdf → Elevations 1.pdf
    ├── pohlady 2.pdf → Elevations 2.pdf
    ├── pohlady 3.pdf → Elevations 3.pdf
    ├── Strecha.jpg → Roof.jpg
    ├── tapfer_PSP_03_PODORYS 1.NP.pdf → tapfer_PSP_03_Floor Plan 1st Floor.pdf
    ├── tapfer_PSP_04_REZ CC-DD.pdf → tapfer_PSP_04_Section CC-DD.pdf
    ├── tapfer_PSP_05_REZ AA- BB.pdf → tapfer_PSP_05_Section AA-BB.pdf
    ├── tapfer_PSP_06_REZ EE.pdf → tapfer_PSP_06_Section EE.pdf
    ├── tapfer_PSP_07_KROV.pdf → tapfer_PSP_07_Roof Framing.pdf
    ├── tapfer_PSP_08_STRECHA.pdf → tapfer_PSP_08_Roof.pdf
    └── tapfer_PSP_09_POHLADY.pdf → tapfer_PSP_09_Elevations.pdf
```

### 039JO26A - SIPKON_Lutostav → 039JO26A - SIPKON_Lutostav

Dir structure:
```
039JO26A - SIPKON_Lutostav/
├── Truss Design Variant A/
│   ├── 039JO26A.material.pdf (unchanged)
│   └── Floor Plan + 3D.pdf
└── Supporting Documents/
    ├── 04pôdorys.pdf → 04 Floor Plan.pdf
    ├── 05 prieƒny rez.pdf → 05 Transverse Section.pdf
    └── SK26_0015 - 01 Pôdorys 1.NP - 03.02.2026.pdf → SK26_0015 - 01 Floor Plan 1st Floor - 03.02.2026.pdf
```

### 040IK26A - Kišš → 040IK26A - Kišš

Dir structure:
```
040IK26A - Kišš/
├── Truss Design Variant A/
│   ├── 040IK26A.material.pdf (unchanged)
│   └── Floor Plan + 3D.pdf
└── Supporting Documents/
    └── Rd Nitra_ZMENA_2026_02_02.pdf → RD Nitra_Change_2026_02_02.pdf
```

- [x] 5.1 Process project 032 — create dirs including Final Design/Proposal nested structure, copy files, write translation-notes.txt in all 5 directories.
- [x] 5.2 Process project 033 — create dirs, copy files with translated names, write translation-notes.txt.
- [x] 5.3 Process project 035 — create dirs, copy all 12 support files with translated names, write translation-notes.txt.
- [x] 5.4 Process project 039 — create dirs, copy files with translated names, write translation-notes.txt.
- [x] 5.5 Process project 040 — create dirs, copy files with translated names, write translation-notes.txt.
- [x] 5.6 Verify batch — confirm 15 project folders total. Spot-check 3 files with `diff`.

**Done when**: 15 project folders in `hidden/Trusses AI/`, each with translated files and notes.
**Verify by**: `ls "hidden/Trusses AI/" | wc -l` returns 15.

## 6. Mid-Complexity Projects — 041, 043, 044, 046, 047

### 041JO26A - EKO-MONT_Polyfunkcia Janíkovce → 041JO26A - EKO-MONT_Mixed-use Building Janíkovce

Dir structure:
```
041JO26A - EKO-MONT_Mixed-use Building Janíkovce/
├── Truss Design Variant A/
│   ├── 041JO26A.material.pdf (unchanged)
│   └── Floor Plan + 3D.pdf
└── Supporting Documents/
    ├── 07b krov.pdf → 07b Roof Framing.pdf
    ├── 07 strecha.pdf → 07 Roof.pdf
    ├── 08 rez.pdf → 08 Section.pdf
    ├── 09 pohlad.pdf → 09 View.pdf
    ├── 10 pohlad.pdf → 10 View.pdf
    ├── 11 pohlady.pdf → 11 Elevations.pdf
    ├── 5 ustúpené podlažie.pdf → 5 Set-back Floor.pdf
    ├── Beze jména.dwg → Untitled.dwg
    ├── JV pohlad.pdf → JV View.pdf
    ├── Polyfunkčný objekt.xlsx → Mixed-use Building.xlsx (contents NOT translated)
    └── správa.pdf → Report.pdf
```

### 043IK26A - BigMat Skalica_Vŕba → 043IK26A - BigMat Skalica_Vŕba

Dir structure:
```
043IK26A - BigMat Skalica_Vŕba/
├── Truss Design Variant A/
│   ├── 043IK26A.material.pdf (unchanged)
│   └── Floor Plan + 3D.pdf
└── Supporting Documents/
    └── RD_Vrba_PS_stavebná časť.pdf → RD_Vrba_PS_Construction Section.pdf
```

### 044AC26A - Stavmat_CALCUS → 044AC26A - Stavmat_CALCUS

Dir structure:
```
044AC26A - Stavmat_CALCUS/
├── Truss Design Variant A/
│   ├── 044AC26A.material.pdf (unchanged)
│   └── Floor Plan + 3D.pdf
└── Supporting Documents/
    ├── Beze jména.dwg → Untitled.dwg
    ├── Nyrovce bytovka SITUACIA 21-02-2025.pdf → Nyrovce Apartment Building Site Plan 21-02-2025.pdf
    ├── PôDORYS 1.NP.pdf → Floor Plan 1st Floor.pdf
    ├── PôDORYS 2.NP.pdf → Floor Plan 2nd Floor.pdf
    ├── PôDORYS 3.NP.pdf → Floor Plan 3rd Floor.pdf
    ├── PôDORYS STRECHY.pdf → Floor Plan Roof.pdf
    ├── PôDORYS STROPU.pdf → Floor Plan Ceiling.pdf
    ├── POHLADY.pdf → Elevations.pdf
    ├── REZ A-A, REZ B-B.pdf → Section A-A, Section B-B.pdf
    └── ZÁKLADY.pdf → Foundations.pdf
```

### 046JO26A - Plešivka_Kochan → 046JO26A - Plešivka_Kochan

Dir structure:
```
046JO26A - Plešivka_Kochan/
├── Truss Design Variant A/
│   ├── 046JO26A.material.pdf (unchanged)
│   └── Floor Plan + 3D.pdf
└── Supporting Documents/
    ├── B.D1.pdf (unchanged)
    ├── D2.01 - pôdorys.pdf → D2.01 - Floor Plan.pdf
    ├── D2.02.pdf (unchanged)
    ├── D2.03 - strecha.pdf → D2.03 - Roof.pdf
    ├── D2.04 - rez.pdf → D2.04 - Section.pdf
    ├── D2.05.1.pdf (unchanged)
    ├── D2.05.2.pdf (unchanged)
    ├── D2.05.3.pdf (unchanged)
    ├── D2.06.pdf (unchanged)
    ├── D2.07.pdf (unchanged)
    ├── DOSKY.pdf → Boards.pdf
    ├── Príloha E01_092025.pdf → Appendix E01_092025.pdf
    ├── Príloha E01.pdf → Appendix E01.pdf
    ├── Príloha E02.pdf → Appendix E02.pdf
    ├── Príloha E03.pdf → Appendix E03.pdf
    ├── SIT.001.pdf → Site Plan 001.pdf
    ├── SIT.002.pdf → Site Plan 002.pdf
    ├── SIT.002+PRIPOJKY.pdf → Site Plan 002+Connections.pdf
    └── SNURKY.pdf → Rebar Details.pdf
```

### 047IK26A - Hiltonko_Valo → 047IK26A - Hiltonko_Valo

Dir structure:
```
047IK26A - Hiltonko_Valo/
├── Truss Design Variant A/
│   ├── 047IK26A.material.pdf (unchanged)
│   └── Floor Plan + 3D.pdf
└── Supporting Documents/
    ├── C1 KOORDINAČNÁ SITUÁCIA.pdf → C1 Coordination Site Plan.pdf
    ├── E2 PÔDORYS ZÁKLADOV.pdf → E2 Floor Plan Foundations.pdf
    ├── E3 1. NADZEMNÉ PODLAŽIE.pdf → E3 1st Floor.pdf
    ├── E4 PÔDOYRS  STRECHY.pdf → E4 Floor Plan Roof.pdf
    ├── E5 REZ A-A´.pdf → E5 Section A-A'.pdf
    └── E6 POHĽADY.pdf → E6 Elevations.pdf
```

- [x] 6.1 Process project 041 — create dirs, copy 12 support files with translated names, write translation-notes.txt.
- [ ] 6.2 Process project 043 — create dirs, copy files, write translation-notes.txt.
- [ ] 6.3 Process project 044 — create dirs, copy 10 support files with translated names (includes Czech `Beze jména` → `Untitled`), write translation-notes.txt.
- [ ] 6.4 Process project 046 — create dirs, copy 18 support files with translated names, write translation-notes.txt.
- [ ] 6.5 Process project 047 — create dirs, copy 6 support files with translated names, write translation-notes.txt.
- [ ] 6.6 Verify batch — confirm 20 project folders total. Spot-check `diff` on 3 files.

**Done when**: 20 project folders in `hidden/Trusses AI/`.
**Verify by**: `ls "hidden/Trusses AI/" | wc -l` returns 20.

## 7. Two-Variant Projects + Simple Projects — 053, 054, 056, 057, 060, 062

### 053IK26B - Plecho_RD Výčapovce → 053IK26B - Plecho_Family House Výčapovce

Dir structure:
```
053IK26B - Plecho_Family House Výčapovce/
├── Truss Design Variant A/
│   ├── 053IK26A.material.pdf (unchanged)
│   └── Floor Plan + 3D.pdf
├── Truss Design Variant B/
│   ├── 053IK26B.material.pdf (unchanged)
│   └── Floor Plan + 3D.pdf
└── Supporting Documents/
    └── translation-notes.txt (directory is empty — note this in the file)
```

### 054IK26A - IP-strechy_Čechvala → 054IK26A - IP Roofs_Čechvala

Dir structure:
```
054IK26A - IP Roofs_Čechvala/
├── Truss Design Variant A/
│   ├── 054IK26A.material.pdf (unchanged)
│   └── Floor Plan + 3D.pdf
└── Supporting Documents/
    ├── Čechvala - pôdorys prízemia.jpg → Čechvala - Floor Plan Ground Floor.jpg
    ├── Čechvala - pôdorys strechy.jpg → Čechvala - Floor Plan Roof.jpg
    └── Čechvala - rez.jpg → Čechvala - Section.jpg
```

### 056JO26A - Maťko_Ježovský → 056JO26A - Maťko_Ježovský

Dir structure:
```
056JO26A - Maťko_Ježovský/
├── Truss Design Variant A/
│   ├── 056JO26A.material.pdf (unchanged)
│   └── Floor Plan + 3D.pdf
└── Supporting Documents/
    └── podorys_1_1.PNG → Floor Plan_1_1.PNG
```

### 057IK26A - Sollár → 057IK26A - Sollár

Dir structure:
```
057IK26A - Sollár/
├── Truss Design Variant A/
│   ├── 057IK26A.material.pdf (unchanged)
│   └── Floor Plan + 3D.pdf
├── Truss Design Variant B/
│   ├── 057IK26A.material.pdf (unchanged)
│   └── Floor Plan + 3D.pdf
└── Supporting Documents/
    └── viber_image_2026-02-25_10-27-57-218.jpg (unchanged)
```

### 060JO26B - SIPKON_Belančík → 060JO26B - SIPKON_Belančík

Dir structure:
```
060JO26B - SIPKON_Belančík/
├── Truss Design Variant A/
│   ├── 060JO26A.material.pdf (unchanged)
│   └── Floor Plan + 3D.pdf
├── Truss Design Variant B/
│   ├── 060JO26B.material.pdf (unchanged)
│   └── Floor Plan + 3D.pdf
└── Supporting Documents/
    ├── ARCHITEKTURA 2025 BELANCIK MCH 03 PODORYS 1NP.pdf → Architecture 2025 Belančík MCH 03 Floor Plan 1st Floor.pdf
    ├── Thumbs.db (unchanged — system file)
    └── viber_image_2026-02-26_11-21-14-528.jpg (unchanged)
```

### 062IK26A - Máče → 062IK26A - Máče

Dir structure:
```
062IK26A - Máče/
├── Truss Design Variant A/
│   ├── 062IK26A.material.pdf (unchanged)
│   └── Floor Plan + 3D.pdf
└── Supporting Documents/
    └── viber_image_2026-02-26_10-49-44-560.jpg (unchanged)
```

- [ ] 7.1 Process project 053 — create dirs including empty Supporting Documents with translation-notes.txt noting the directory is empty in source.
- [ ] 7.2 Process project 054 — create dirs, copy files, write translation-notes.txt.
- [ ] 7.3 Process project 056 — create dirs, copy files, write translation-notes.txt.
- [ ] 7.4 Process project 057 — create dirs (2 variants), copy files, write translation-notes.txt.
- [ ] 7.5 Process project 060 — create dirs (2 variants), copy files (including Thumbs.db), write translation-notes.txt.
- [ ] 7.6 Process project 062 — create dirs, copy files, write translation-notes.txt.
- [ ] 7.7 Verify batch — confirm 26 project folders total. Spot-check 3 files with `diff`.

**Done when**: 26 project folders in `hidden/Trusses AI/`.
**Verify by**: `ls "hidden/Trusses AI/" | wc -l` returns 26.

## 8. Project with German Filenames — 058

### 058JO26A - SIPKON_Petruš → 058JO26A - SIPKON_Petruš

This project contains both Slovak and German filenames. All must be translated to English.

Dir structure:
```
058JO26A - SIPKON_Petruš/
├── Truss Design Variant A/
│   ├── 058JO26A.material.pdf (unchanged)
│   └── Floor Plan + 3D.pdf
└── Supporting Documents/
    ├── 3D Ans 24.09.25.pdf → 3D View 24.09.25.pdf
    ├── Ans N+W 24.09.25.pdf → View N+W 24.09.25.pdf
    ├── Ans S+O 24.09.25.pdf → View S+O 24.09.25.pdf
    ├── EG 24.09.25.pdf → Ground Floor 24.09.25.pdf
    ├── Entwässerung 24.09.25.pdf → Drainage 24.09.25.pdf
    ├── OG 24.09.25.pdf → Upper Floor 24.09.25.pdf
    ├── Schnitt 24.09.25.pdf → Section 24.09.25.pdf
    ├── SK260020 - 01 Pôdorys 1.NP - 24.02.2026.pdf → SK260020 - 01 Floor Plan 1st Floor - 24.02.2026.pdf
    ├── SK260020 - 02 Pôdorys 2.NP - 24.02.2026.pdf → SK260020 - 02 Floor Plan 2nd Floor - 24.02.2026.pdf
    ├── zaťaženie snehom.png → Snow Load.png
    └── zaťaženie vetrom.png → Wind Load.png
```

- [ ] 8.1 Process project 058 — create dirs, copy all 11 support files with translated names (7 German → English, 4 Slovak → English), write translation-notes.txt.
- [ ] 8.2 Verify batch — confirm 27 project folders total. Spot-check `diff` on `Ground Floor 24.09.25.pdf` and `Wind Load.png`.

**Done when**: Project 058 exists with all German and Slovak filenames translated to English.
**Verify by**: `ls "hidden/Trusses AI/058JO26A - SIPKON_Petruš/Supporting Documents/" | grep -c "Ground Floor"` returns 1, and no German words remain: `ls "hidden/Trusses AI/058JO26A - SIPKON_Petruš/Supporting Documents/" | grep -iE "Ans|EG|OG|Schnitt|Entw"` returns empty.

## 9. Most Complex Project — 064

### 064IK26A - LŠ_Greguš → 064IK26A - LŠ_Greguš

This is the largest project with 6 subdirectories under Supporting Documents. Process each subdirectory as a unit.

Dir structure:
```
064IK26A - LŠ_Greguš/
├── Truss Design Variant A/
│   ├── 064IK26A.material.pdf (unchanged)
│   └── Floor Plan + 3D.pdf
└── Supporting Documents/
    ├── PDF ARCH/
    │   ├── A. ZOZNAM DOKUMENTÁCIE.pdf → A. Document List.pdf
    │   ├── B. SÚHRNNÁ SPRÁVA.pdf → B. Summary Report.pdf
    │   ├── C. SIT.001__situacia širšich vzťahov.pdf → C. Site Plan 001__Site Plan Wider Context.pdf
    │   ├── C. SIT.002__situacia.pdf → C. Site Plan 002__Site Plan.pdf
    │   ├── D1.01__podorys 1.pp.pdf → D1.01__Floor Plan 1st Basement.pdf
    │   ├── D1.02__podorys 1.np.pdf → D1.02__Floor Plan 1st Floor.pdf
    │   ├── D1.03__zaklady.pdf → D1.03__Foundations.pdf
    │   ├── D1.04__preklady 1.pp.pdf → D1.04__Lintels 1st Basement.pdf
    │   ├── D1.05__žb stropna doska nad 1.pp.pdf → D1.05__RC Floor Slab above 1st Basement.pdf
    │   ├── D1.06__preklady 1.np.pdf → D1.06__Lintels 1st Floor.pdf
    │   ├── D1.07__strecha.pdf → D1.07__Roof.pdf
    │   ├── D1.08__rez objektom.pdf → D1.08__Section Through Building.pdf
    │   ├── D1.09__pohľady.pdf → D1.09__Elevations.pdf
    │   ├── D1.10__OPORNÝ MÚR__podorys.pdf → D1.10__Retaining Wall__Floor Plan.pdf
    │   └── D1.11__OPORNÝ MÚR__rez, pohľady.pdf → D1.11__Retaining Wall__Section, Elevations.pdf
    ├── PDF Electrical/
    │   ├── 66_E-01_Technická správa.pdf → 66_E-01_Technical Report.pdf
    │   ├── 66_E-02 Situácia (tlač 4x, farebne, 5xA4, 1050x297).pdf → 66_E-02 Site Plan (print 4x, color, 5xA4, 1050x297).pdf
    │   ├── 66_E-03 Úprava vedení.pdf → 66_E-03 Cable Routing.pdf
    │   ├── 66_E-04 Pôdorys 1.PP.pdf → 66_E-04 Floor Plan 1st Basement.pdf
    │   ├── 66_E-05 Pôdorys 1.NP.pdf → 66_E-05 Floor Plan 1st Floor.pdf
    │   └── 66_E-06 Bleskozvod.pdf → 66_E-06 Lightning Conductor.pdf
    ├── PDF Energy Performance/
    │   └── EHB Cabaj Gregus.pdf → Energy Performance Certificate Cabaj Greguš.pdf
    ├── PDF Fire Protection/
    │   ├── 227_11_25 RD Greguš-V01.pdf (unchanged)
    │   ├── 227_11_25 RD Greguš-V02.pdf (unchanged)
    │   ├── 227_11_25 RD Greguš-V03.pdf (unchanged)
    │   ├── 227_11_25 RD Greguš-V04.pdf (unchanged)
    │   ├── 227_11_25 RD Greguš-V05.pdf (unchanged)
    │   └── 227_11_25_Technicka sprava.pdf → 227_11_25_Technical Report.pdf
    ├── PDF Structural Engineering/
    │   ├── horná a dolná výstuž.pdf → Upper and Lower Reinforcement.pdf
    │   ├── schody__420x297.pdf → Stairs__420x297.pdf
    │   ├── trám T1__420x297.pdf → Beam T1__420x297.pdf
    │   ├── trám T2__420x297.pdf → Beam T2__420x297.pdf
    │   └── trám T3__420x297.pdf → Beam T3__420x297.pdf
    └── PDF Building Services/
        ├── D4.00__technická správa.pdf → D4.00__Technical Report.pdf
        ├── D4.01__uloženie potrubia.pdf → D4.01__Pipe Routing.pdf
        ├── D4.02__ZTI - podorys 1.PP.pdf → D4.02__Plumbing - Floor Plan 1st Basement.pdf
        ├── D4.03__ZTI - podorys 1.NP.pdf → D4.03__Plumbing - Floor Plan 1st Floor.pdf
        ├── D4.04__ZTI - zariadovacie predmety.pdf → D4.04__Plumbing - Sanitary Fixtures.pdf
        ├── D4.05__PLYN - podorys 1.PP.pdf → D4.05__Gas - Floor Plan 1st Basement.pdf
        ├── D4.06__VYK - podorys 1.PP.pdf → D4.06__Heating - Floor Plan 1st Basement.pdf
        ├── D4.07__VYK - podorys 1.NP.pdf → D4.07__Heating - Floor Plan 1st Floor.pdf
        ├── D4.08__VYK - detaily.pdf → D4.08__Heating - Details.pdf
        ├── D4.09__VYK - schéma zapojenia.pdf → D4.09__Heating - Wiring Diagram.pdf
        └── SIT.001__situacia.pdf → Site Plan 001__Site Plan.pdf
```

- [ ] 9.1 Process project 064 — create full 8-directory structure (Truss Design Variant A + Supporting Documents with 6 subdirs), copy and translate all ~50 files, write translation-notes.txt in every directory (8 total).
- [ ] 9.2 Verify — confirm 28 project folders total. Spot-check `diff` on 3 files across different subdirectories.

**Done when**: Project 064 fully structured with all 6 subdirectories, ~50 translated files, and 8 translation-notes.txt files.
**Verify by**: `find "hidden/Trusses AI/064IK26A - LŠ_Greguš/" -type f -name "translation-notes.txt" | wc -l` returns 8.

## 10. Remaining Projects — 065, 078, 083, 105, 108

### 065IK26A - Bigmat Remot_iTask Int → 065IK26A - Bigmat Remot_iTask Int

Dir structure:
```
065IK26A - Bigmat Remot_iTask Int/
├── Truss Design Variant A/
│   ├── 065IK26A.material.pdf (unchanged)
│   └── Floor Plan + 3D.pdf
└── Supporting Documents/
    ├── 05-Pôdorys 1.NP.pdf → 05-Floor Plan 1st Floor.pdf
    ├── 06-Pôdorys krovu.pdf → 06-Floor Plan Roof Framing.pdf
    ├── 07-Pôdorys strechy.pdf → 07-Floor Plan Roof.pdf
    ├── 08-Rez A-A.pdf → 08-Section A-A.pdf
    ├── 09-Rez B-B´.pdf → 09-Section B-B'.pdf
    ├── 10-Rez C-C´.pdf → 10-Section C-C'.pdf
    ├── 11-Rez D-D´.pdf → 11-Section D-D'.pdf
    └── 12-Pohľady.pdf → 12-Elevations.pdf
```

### 078JO26A - SIPKON_Buocik → 078JO26A - SIPKON_Buocik

Dir structure:
```
078JO26A - SIPKON_Buocik/
├── Truss Design Variant A/
│   ├── 078JO26A.material.pdf (unchanged)
│   └── Floor Plan + 3D.pdf
└── Supporting Documents/
    ├── CP12260085-v1.pdf (unchanged)
    ├── Wolf plan V11260047.pdf (unchanged)
    └── Wolf System Fotovoltika ponuka.pdf → Wolf System Photovoltaics Quote.pdf
```

### 083JO26A - SIPKON_BD Golianovo → 083JO26A - SIPKON_Apartment Building Golianovo

Dir structure:
```
083JO26A - SIPKON_Apartment Building Golianovo/
├── Truss Design Variant A/
│   ├── 083JO26A.material.pdf (unchanged)
│   └── Floor Plan + 3D.pdf
└── Supporting Documents/
    ├── 07 podorys strechy nad 3.NP 350x630 far. .pdf → 07 Floor Plan Roof above 3rd Floor 350x630 color.pdf
    ├── 08 pohlad nas trechu 350x630 far. .pdf → 08 View Toward Roof 350x630 color.pdf
    ├── 09 rezy 297x840 far. .pdf → 09 Sections 297x840 color.pdf
    └── 10 pohlady 297x700 far. .pdf → 10 Elevations 297x700 color.pdf
```

### 105IK26A - Hiltonko_Hippová → 105IK26A - Hiltonko_Hippová

Dir structure:
```
105IK26A - Hiltonko_Hippová/
├── Truss Design Variant A/
│   ├── 105IK26A.material.pdf (unchanged)
│   └── Floor Plan + 3D.pdf
└── Supporting Documents/
    ├── AS00.pdf (unchanged)
    ├── pracovná  strecha.pdf → Working Draft Roof.pdf
    ├── pracovné pohľady.pdf → Working Draft Elevations.pdf
    ├── pracovné základy.pdf → Working Draft Foundations.pdf
    ├── pracovný pôdorys.pdf → Working Draft Floor Plan.pdf
    └── pracovný  rez.pdf → Working Draft Section.pdf
```

### 108JO26A - Marcinko → 108JO26A - Marcinko

Dir structure:
```
108JO26A - Marcinko/
├── Truss Design Variant A/
│   ├── 108JO26A.material.pdf (unchanged)
│   └── Floor Plan + 3D.pdf
└── Supporting Documents/
    ├── 01_preklady_297_594.pdf → 01_Lintels_297_594.pdf
    ├── 02_preklady vystuz_A3.pdf → 02_Lintels Reinforcement_A3.pdf
    ├── 03_strop nad 1NP_297_594.pdf → 03_Ceiling above 1st Floor_297_594.pdf
    ├── 04_krov_297_294.pdf → 04_Roof Framing_297_294.pdf
    ├── RD Marcinko Cabaj - pôdorys prízemia.pdf → RD Marcinko Cabaj - Floor Plan Ground Floor.pdf
    ├── RD Marcinko Cabaj - pôdorys strechy.pdf → RD Marcinko Cabaj - Floor Plan Roof.pdf
    ├── RD Marcinko Cabaj - pôdorys základov.pdf → RD Marcinko Cabaj - Floor Plan Foundations.pdf
    ├── RD Marcinko Cabaj - pohľady.pdf → RD Marcinko Cabaj - Elevations.pdf
    ├── RD Marcinko Cabaj - rez.pdf → RD Marcinko Cabaj - Section.pdf
    ├── RD Marcinko Cabaj - situácia.pdf → RD Marcinko Cabaj - Site Plan.pdf
    ├── RD Marcinko Cabaj - sprievodná a technická správa.pdf → RD Marcinko Cabaj - Cover and Technical Report.pdf
    ├── Rodinný dom - novostavba [zadanie] (1).xlsx → Family House - New Construction [Brief] (1).xlsx (contents NOT translated)
    ├── vykaz krov+strop Marcinko.xls → Quantity Takeoff Roof Framing+Ceiling Marcinko.xls (contents NOT translated)
    └── vykaz vystuze Marcinko.xls → Quantity Takeoff Reinforcement Marcinko.xls (contents NOT translated)
```

- [ ] 10.1 Process project 065 — create dirs, copy 8 support files with translated names, write translation-notes.txt.
- [ ] 10.2 Process project 078 — create dirs, copy files, write translation-notes.txt.
- [ ] 10.3 Process project 083 — create dirs, copy 4 support files with translated names, write translation-notes.txt.
- [ ] 10.4 Process project 105 — create dirs, copy 6 support files with translated names, write translation-notes.txt.
- [ ] 10.5 Process project 108 — create dirs, copy 14 support files with translated names, write translation-notes.txt.
- [ ] 10.6 Verify batch — confirm 33 project folders total. Spot-check 3 files with `diff`.

**Done when**: 33 project folders in `hidden/Trusses AI/`.
**Verify by**: `ls "hidden/Trusses AI/" | wc -l` returns 33.

## 11. Root Translation Notes and Final Verification

- [ ] 11.1 Create root `translation-notes.txt` in `hidden/Trusses AI/` — list all 33 top-level folder translations in the format `Slovak original → English translation`, one per line.
- [ ] 11.2 Verify total project folder count — run `ls "hidden/Trusses AI/" | wc -l` and confirm it returns 33.
- [ ] 11.3 Verify no Slovak/German/Czech names remain — run `find "hidden/Trusses AI/" -depth -print0 | xargs -0 -I{} basename "{}" | grep -cE '[áäčďéíĺľňóôŕšťúýžÁÄČĎÉÍĹĽŇÓÔŔŠŤÚÝŽüöÜÖß]'` and confirm the count is 0 (no diacritical characters in filenames). Note: proper nouns like `Hrušovská`, `Zeleňáková` in folder names may retain diacritics since they are surnames/placenames — these are acceptable.
- [ ] 11.4 Verify translation-notes.txt coverage — run `find "hidden/Trusses AI/" -type d -exec test -f "{}/translation-notes.txt" \; -print` and confirm every directory has a notes file. Expected: all directories should be listed (or use `find "hidden/Trusses AI/" -type d | wc -l` and compare with `find "hidden/Trusses AI/" -type d -exec test -f "{}/translation-notes.txt" \; -print | wc -l`).
- [ ] 11.5 Spot-check file integrity — run `diff` on 5 PDFs across different projects (e.g., projects 001, 028, 058, 064, 108) and confirm byte-identical.
- [ ] 11.6 Verify original directory untouched — run `find "hidden/Väzníky AI/" -type f | wc -l` and compare against a baseline count. Confirm no files were added or removed from the original.

**Done when**: Root translation notes exist, all 33 folders verified present, no untranslated names remain, all spot-checks pass, original directory confirmed untouched.
**Verify by**: All verification commands in tasks 11.2–11.6 pass without errors.
**Stop and hand off if**: Any verification command fails — report the specific failure and which project/directory is affected.

## 12. Human Handoff

These items are outside the autonomous loop and require human decision:

- [ ] 12.1 Decide git strategy for binary files — review `hidden/Trusses AI/` (~246 MB of PDFs, images) and decide whether to: (a) commit directly, (b) use Git LFS, or (c) add to `.gitignore`.
- [ ] 12.2 Spot-check translation accuracy — manually review a sample of translated filenames in `hidden/Trusses AI/` against the originals in `hidden/Väzníky AI/` to confirm correctness.
- [ ] 12.3 Decide on file-content translation — this change explicitly did NOT translate file contents. If PDF/image content translation is desired, create a separate OpenSpec change.
