## ADDED Requirements

### Requirement: CSV title and description header
The script SHALL write a title row and a description row at the top of the CSV file, followed by a blank separator row before column headers.

#### Scenario: Title and description present in output
- **WHEN** the script generates the CSV
- **THEN** row 1 contains the title text, row 2 contains the description text, row 3 is blank, and row 4 contains column headers

#### Scenario: Title is descriptive
- **WHEN** the script generates the CSV
- **THEN** the title row contains "Top 5 Most Populous Countries — Hello World Greetings" or equivalent descriptive title

### Requirement: Country data columns
The script SHALL produce CSV columns: Country, Population, and Hello World (Greeting).

#### Scenario: Column headers match spec
- **WHEN** the CSV is generated
- **THEN** column headers are exactly "Country", "Population", "Hello World"

### Requirement: Top 5 most populous countries
The script SHALL include data rows for exactly these 5 countries in descending population order: India, China, United States, Indonesia, Pakistan.

#### Scenario: Correct countries in correct order
- **WHEN** the CSV is generated
- **THEN** data rows appear in order: India, China, United States, Indonesia, Pakistan

#### Scenario: Exactly 5 data rows
- **WHEN** the CSV is generated
- **THEN** there are exactly 5 data rows after the header row

### Requirement: Bolded country names
The script SHALL wrap each country name in double asterisks (`**name**`) to indicate bold formatting.

#### Scenario: Country names are bolded
- **WHEN** the CSV is generated
- **THEN** each country cell value is formatted as `**India**`, `**China**`, etc.

### Requirement: Localized Hello World greeting
The script SHALL include a "Hello World" greeting in the primary language of each country.

#### Scenario: Greeting language matches country
- **WHEN** the CSV is generated
- **THEN** greetings are:
  - India: "नमस्ते दुनिया" (Hindi)
  - China: "你好世界" (Mandarin Chinese)
  - United States: "Hello World" (English)
  - Indonesia: "Halo Dunia" (Indonesian)
  - Pakistan: "ہیلو دنیا" (Urdu)

### Requirement: Idempotent file generation
The script SHALL overwrite the output file on each run, producing identical output regardless of how many times it is executed.

#### Scenario: Repeated runs produce identical output
- **WHEN** the script is run twice in succession
- **THEN** the content of the output file after both runs is byte-for-byte identical

### Requirement: UTF-8 encoding
The script SHALL write the CSV file using UTF-8 encoding to support non-ASCII characters in greetings.

#### Scenario: Non-ASCII characters preserved
- **WHEN** the CSV is generated
- **THEN** the file is valid UTF-8 and all greeting characters (Hindi, Chinese, Urdu) are correctly preserved

### Requirement: Output file location
The script SHALL write the CSV file to the project's working directory as `top5_populous_countries.csv`.

#### Scenario: File created in expected location
- **WHEN** the script runs
- **THEN** a file named `top5_populous_countries.csv` exists in the working directory

### Requirement: Reset and cleanup
The script (or an associated reset task) SHALL provide the ability to delete the generated CSV file and reset task completion status so the entire workflow can be re-run from scratch.

#### Scenario: Reset removes generated file
- **WHEN** the reset operation is executed
- **THEN** the file `top5_populous_countries.csv` is deleted if it exists

#### Scenario: Reset clears task checkboxes
- **WHEN** the reset operation is executed
- **THEN** all task checkboxes in `tasks.md` are unchecked (changed from `[x]` to `[ ]`)
