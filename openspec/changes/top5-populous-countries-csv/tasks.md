## 1. Pre-flight

- [ ] **Pre-flight: record quality gate baselines**
  - Scope: no code edits; writes only under `.ralph/baselines/`
  - Change: Capture current state of all gates later tasks require.
  - Done when:
    - `.ralph/baselines/top5-populous-countries-csv-typecheck.txt` exists with full output and ends with `EXIT=<integer>` line
    - `.ralph/baselines/top5-populous-countries-csv-lint.txt` exists with full output and ends with `EXIT=<integer>` line
    - `.ralph/baselines/top5-populous-countries-csv-readme.md` lists passing/failing gates, exit codes, and exact failing identifiers
  - Stop and hand off if: any gate is nondeterministic across two runs, or any captured baseline file is missing the `EXIT=<integer>` final line after retrying the capture command.

## 2. Core Implementation

- [ ] **Create CSV generation script with embedded country data**
  - Scope: `test/generate_top5_countries.py` (new file)
  - Change: A Python script that generates `top5_populous_countries.csv` with a title row, description row, blank separator, column headers (Country, Population, Hello World), and 5 data rows for India, China, United States, Indonesia, Pakistan. Country names are bolded with `**name**`. Greetings are in each country's primary language (Hindi, Mandarin, English, Indonesian, Urdu). File is written with UTF-8 encoding in overwrite mode.
  - Done when:
    - `test/generate_top5_countries.py` exists and is syntactically valid (`python -c "import ast; ast.parse(open('test/generate_top5_countries.py').read())"` exits 0)
    - `python test/generate_top5_countries.py` exits 0
    - `top5_populous_countries.csv` exists in the working directory
    - `rg "^Top 5" top5_populous_countries.csv` returns a match (title row present)
    - `rg "Country,Population,Hello World" top5_populous_countries.csv` returns a match (column headers present)
    - `rg "\*\*India\*\*" top5_populous_countries.csv` returns a match (bolded country name)
    - `rg "नमस्ते" top5_populous_countries.csv` returns a match (Hindi greeting)
  - Stop and hand off if: Python 3.12+ is not available or UTF-8 encoding is not supported.

## 3. Verification

- [ ] **Verify idempotency and output correctness**
  - Scope: `test/generate_top5_countries.py`, `top5_populous_countries.csv`
  - Change: Confirmed that the script produces identical output on repeated runs and all 5 country rows are present with correct data.
  - Done when:
    - Running `python test/generate_top5_countries.py` twice produces byte-identical files (`md5sum top5_populous_countries.csv` matches after both runs)
    - `top5_populous_countries.csv` contains exactly 5 data rows (excluding title, description, blank, and header rows)
    - `rg "\*\*China\*\*" top5_populous_countries.csv` returns a match
    - `rg "\*\*United States\*\*" top5_populous_countries.csv` returns a match
    - `rg "\*\*Indonesia\*\*" top5_populous_countries.csv` returns a match
    - `rg "\*\*Pakistan\*\*" top5_populous_countries.csv` returns a match
    - `rg "你好世界" top5_populous_countries.csv` returns a match (Chinese greeting)
    - `rg "Halo Dunia" top5_populous_countries.csv` returns a match (Indonesian greeting)
  - Stop and hand off if: output differs between runs despite no code changes.

## 4. Reset and Reentrancy

- [ ] **Create reset script to clean output and reset task status**
  - Scope: `test/reset_top5_countries.py` (new file), `openspec/changes/top5-populous-countries-csv/tasks.md`
  - Change: A Python script that deletes `top5_populous_countries.csv` if it exists and unchecks all task checkboxes in `tasks.md` (replaces `[x]` with `[ ]`), enabling the entire workflow to be re-run from scratch.
  - Done when:
    - `test/reset_top5_countries.py` exists and is syntactically valid
    - Running `python test/reset_top5_countries.py` deletes `top5_populous_countries.csv` (file no longer exists)
    - After running the reset, `tasks.md` contains zero `[x]` checkboxes (`rg "\[x\]" openspec/changes/top5-populous-countries-csv/tasks.md` returns no matches)
    - After running the reset, `tasks.md` still contains all original `[ ]` checkboxes (`rg "\[ \]" openspec/changes/top5-populous-countries-csv/tasks.md` returns matches)
    - Running the reset script when no CSV exists exits 0 without error (idempotent)
  - Stop and hand off if: task checkbox format in `tasks.md` does not match expected `[x]`/`[ ]` pattern.
