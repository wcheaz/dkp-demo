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
