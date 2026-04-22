## Purpose

Defines the `DesignEntry` data model and associated test assets for the design entry system.

## Requirements

### Requirement: DesignEntry type has an id field
The `DesignEntry` interface (TypeScript, `src/lib/types.ts`) and the `DesignEntry` Pydantic model (Python, `agent/src/agent.py`) SHALL include an `id: number` field.

The `id` SHALL be 1-based and assigned at creation time using the formula `max(existing entries' ids, 0) + 1`.

All code paths that create `DesignEntry` objects — `add_design_entry` handler, `AddDesignButton`, and any other constructor — SHALL assign the next sequential ID.

#### Scenario: First design entry gets id 1
- **WHEN** the first `DesignEntry` is created in an empty state
- **THEN** the entry SHALL have `id: 1`.

#### Scenario: Subsequent entries increment id
- **WHEN** a new `DesignEntry` is created and the last existing entry has `id: 3`
- **THEN** the new entry SHALL have `id: 4`.

#### Scenario: Existing designs without ids are assigned ids on access
- **WHEN** state contains design entries that lack an `id` field (e.g., from a pre-migration state)
- **THEN** the application SHALL assign sequential IDs to those entries before rendering or processing them.

### Requirement: Test SVG files have descriptive names
The test SVG files SHALL be renamed and copied as follows:
- `tmp/next.svg` → renamed to `tmp/design-alpha.svg`, copied to `public/design-alpha.svg`
- `tmp/vercel.svg` → renamed to `tmp/design-beta.svg`, copied to `public/design-beta.svg`

The default image for new design entries SHALL remain `"/next.svg"` (unchanged from current behavior).

#### Scenario: Descriptive SVG files available in public
- **WHEN** the application starts
- **THEN** `public/design-alpha.svg` and `public/design-beta.svg` SHALL exist and be servable by Next.js.

#### Scenario: Original tmp files renamed
- **WHEN** the rename is complete
- **THEN** `tmp/design-alpha.svg` and `tmp/design-beta.svg` SHALL exist. `tmp/next.svg` and `tmp/vercel.svg` SHALL NOT exist.
