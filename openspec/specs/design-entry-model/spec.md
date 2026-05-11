## Purpose

Defines the `DesignEntry` data model and associated test assets for the design entry system.

## Requirements

### Requirement: DesignEntry type has an id field
The `DesignEntry` interface (TypeScript, `src/lib/types.ts`) and the `DesignEntry` Pydantic model (Python, `agent/src/agent.py`) SHALL include an `id: number` field and a `status` field of type `"processing" | "complete"` with default value `"complete"`.

The `id` SHALL be 1-based and assigned at creation time using the formula `max(existing entries' ids, 0) + 1`.

The `status` field SHALL default to `"complete"` so that all existing code and entries render normally without migration. Entries created by `generate_design` SHALL be created with `status: "processing"` and later resolved to `"complete"`.

All code paths that create `DesignEntry` objects — `generate_design` handler, `AddDesignButton`, and any other constructor — SHALL assign the next sequential ID. Only `generate_design` SHALL create entries with `status: "processing"`; all other constructors SHALL use the default `"complete"`.

#### Scenario: First design entry gets id 1
- **WHEN** the first `DesignEntry` is created in an empty state
- **THEN** the entry SHALL have `id: 1`.

#### Scenario: Subsequent entries increment id
- **WHEN** a new `DesignEntry` is created and the last existing entry has `id: 3`
- **THEN** the new entry SHALL have `id: 4`.

#### Scenario: Existing designs without ids are assigned ids on access
- **WHEN** state contains design entries that lack an `id` field (e.g., from a pre-migration state)
- **THEN** the application SHALL assign sequential IDs to those entries before rendering or processing them.

#### Scenario: DesignEntry type includes status field with complete default
- **WHEN** a `DesignEntry` object is created with `{ id: 1, imageUrl: "/next.svg", promptText: "test" }` (omitting `status`)
- **THEN** the object SHALL satisfy the `DesignEntry` interface and `status` SHALL be `"complete"` (TypeScript) or not required (Python model default).

#### Scenario: DesignEntry can be created with processing status
- **WHEN** a `DesignEntry` object is created with `{ id: 1, imageUrl: "/design-gable.svg", promptText: "test", status: "processing" }`
- **THEN** the object SHALL satisfy the `DesignEntry` interface with `status: "processing"`.

#### Scenario: TypeScript compilation succeeds with status field
- **WHEN** `npx tsc --noEmit` is run
- **THEN** the command SHALL exit zero, confirming `status` is properly typed in both the interface and all usage sites.

#### Scenario: Python model accepts status field
- **WHEN** `cd agent && python -m mypy .` is run
- **THEN** the command SHALL exit zero, confirming `status` is properly typed in the Pydantic model.

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
