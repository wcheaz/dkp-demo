## Purpose

Defines the `DesignEntry` data model and associated test assets for the design entry system.

## Requirements

### Requirement: DesignEntry type has an id field
The `DesignEntry` interface (TypeScript, `src/lib/types.ts`) and the `DesignEntry` Pydantic model (Python, `agent/src/agent.py`) SHALL include an `id: number` field, a `status` field of type `"processing" | "complete"` with default value `"complete"`, and a `dxfContent` field of type `Optional[str]` with default value `None`.

The `id` SHALL be 1-based and assigned at creation time using the formula `max(existing entries' ids, 0) + 1`.

The `status` field SHALL default to `"complete"` so that all existing code and entries render normally without migration. Entries created by `generate_design` SHALL be created with `status: "processing"` and later resolved to `"complete"`.

The `dxfContent` field SHALL default to `None` so that all existing entries and constructors that do not set it remain functional without migration. Only the `generate_dxf` tool SHALL set this field.

All code paths that create `DesignEntry` objects — `generate_design` handler, `AddDesignButton`, and any other constructor — SHALL assign the next sequential ID. Only `generate_design` SHALL create entries with `status: "processing"`; all other constructors SHALL use the default `"complete"`. No constructor other than `generate_dxf` SHALL set `dxfContent`.

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
- **WHEN** a `DesignEntry` object is created with `{ id: 1, imageUrl: "/next.svg", promptText: "test" }` (omitting `status` and `dxfContent`)
- **THEN** the object SHALL satisfy the `DesignEntry` interface and `status` SHALL be `"complete"` (TypeScript) or not required (Python model default) and `dxfContent` SHALL be `None`.

#### Scenario: DesignEntry can be created with processing status
- **WHEN** a `DesignEntry` object is created with `{ id: 1, imageUrl: "/design-gable.svg", promptText: "test", status: "processing" }`
- **THEN** the object SHALL satisfy the `DesignEntry` interface with `status: "processing"` and `dxfContent` SHALL be `None`.

#### Scenario: DesignEntry accepts dxfContent field
- **WHEN** a `DesignEntry` object is created with `{ id: 1, imageUrl: "/next.svg", promptText: "test", dxfContent: "base64string" }`
- **THEN** the object SHALL satisfy the `DesignEntry` interface with `dxfContent: "base64string"`.

#### Scenario: TypeScript compilation succeeds with dxfContent field
- **WHEN** `npx tsc --noEmit` is run
- **THEN** the command SHALL exit zero, confirming `dxfContent` is properly typed in both the interface and all usage sites.

#### Scenario: Python model accepts dxfContent field
- **WHEN** `cd agent && python -m mypy .` is run
- **THEN** the command SHALL exit zero, confirming `dxfContent` is properly typed in the Pydantic model.

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

### Requirement: DesignEntry dxfContent is plain base64 string
The `dxfContent` field, when set, SHALL contain a plain base64-encoded string with no data URI prefix. When `None`, the field indicates that DXF content has not been generated for this entry.

#### Scenario: dxfContent defaults to None on new entries
- **WHEN** a `DesignEntry` is created by `AddDesignButton` or `generate_design` without explicitly setting `dxfContent`
- **THEN** the entry's `dxfContent` SHALL be `None`

#### Scenario: dxfContent can be set by generate_dxf tool
- **WHEN** the `generate_dxf` tool runs successfully for design ID 1
- **THEN** the entry with `id: 1` SHALL have `dxfContent` set to a non-None base64 string, and all other entries SHALL have `dxfContent` unchanged
