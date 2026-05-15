## Why

Generate a reusable, idempotent CSV report listing the top 5 most populous countries with a localized "Hello World" greeting in each country's primary language. The CSV includes a title block and description at the top, followed by formatted country data. This serves as a self-contained demonstration of structured data generation with localization awareness.

## What Changes

- New script that generates a CSV file with:
  - A title row and description row at the top of the file
  - Bolded country names (using Markdown-style `**` wrapping)
  - Columns: Country, Population, "Hello World" (in the country's primary language)
  - Data for the top 5 most populous countries: China, India, United States, Indonesia, Pakistan
- The script is idempotent and reentrant — running it multiple times produces the same output, overwriting any previous file
- A final cleanup/reset task ensures the spec can be re-run from scratch

## Capabilities

### New Capabilities

- `top5-countries-csv-gen`: Generates a titled, described CSV with the top 5 most populous countries, bolded country names, population figures, and a localized "Hello World" column. Includes idempotent reset capability.

### Modified Capabilities

_(none)_

## Impact

- Adds a new standalone script (likely in `test/` directory per project conventions)
- No existing APIs, dependencies, or systems are modified
- Output is a single `.csv` file written to the project's working directory
