# Pamir IFC Bridging Summary

This document summarizes the work delivered by the `pamir-ifc-pricing-bridge`
change. It closes two gaps with MiTek Pamir: (1) the client-side 3D CAD viewer
could not render Pamir-exported IFC files, and (2) the backend-generated IFCs
lacked the hierarchical structure and inline metadata Pamir needs for automated
import and quoting.

## 1. Client-side B-Rep geometry parsing

Implemented in `src/app/cad-viewer-3d/page.tsx` (`parseIfcToDxf`).

- **`IFCFACETEDBREP` / `IFCCLOSEDSHELL`**: the parser resolves the B-Rep
  `ClosedShell`, walks every `IfcFace`, extracts the `IfcFaceOuterBound`
  polyloops, and resolves the referenced `IfcCartesianPoint` coordinates to
  emit DXF `LINE` segments (or `3DFACE`) for each polyloop edge.
- **`IFCARBITRARYCLOSEDPROFILEDEF`**: when a swept area is an arbitrary profile
  rather than a rectangle, its outer curve is resolved into an ordered polygon
  loop. `IFCCOMPOSITECURVE` is traversed segment-by-segment
  (`IFCCOMPOSITECURVESEGMENT` → parent `IFCPOLYLINE`), and direct
  `IFCPOLYLINE` paths are also supported, before the loop is swept into the
  extrusion.
- A fallback remains for the existing swept-solid (`IFCEXTRUDEAREASOLID` +
  rectangle profile) path so previously-supported files keep rendering.

Coverage is validated by `scripts/test-ifc-parser.js`.

## 2. Recursive coordinate transformation

Implemented in `resolvePlacement3D` / `combinePlacements`
(`src/app/cad-viewer-3d/page.tsx`).

- Each `IFCLOCALPLACEMENT` is converted to a local orthonormal frame from its
  `IFCAXIS2PLACEMENT3D` (location + axis/refDir basis).
- The `PlacementRelTo` parent chain is walked recursively up to the storey
  root, accumulating transforms via right-to-left matrix multiplication:
  `M_global = M_parent * M_local`.
- A `visited` set guards against malformed cyclic placement graphs so a repeat
  reference short-circuits instead of recursing forever.
- Vertices are transformed into absolute world coordinates, so deeply nested
  members inside assemblies render in the correct position.

## 3. Backend hierarchical assembly nesting

Implemented in `agent/src/ifc_builder.py`.

- Each truss position is wrapped in an `IfcElementAssembly` (named
  `S<index>`) with `PredefinedType = .TRUSS.` and `AssemblyPlace = .FACTORY.`.
- Its chords/webs are linked via `IfcRelAggregates`, so Pamir treats the
  members as a single coherent structural frame instead of floating beams.
- `IfcBuildingElementProxy` support points are emitted at each wall bearing so
  the support zone is explicit.

Coverage is validated by `test/test_ifc_builder.py` and the
`generated/gable.ifc` assertions (`IfcElementAssembly` and
`IfcBuildingElementProxy` counts).

## 4. Inline metadata and custom property sets

Implemented in `agent/src/ifc_builder.py`.

- **Member metadata**: each `IfcMember` gets `Name = "T<index>"` and
  `Description = "C24 45x120"` (grade + `ThicknessxWidth`), readable by Pamir
  without resolving a property set. `ObjectType` carries the functional role
  (`TOP_CHORD` / `BOTTOM_CHORD` / `WEB` / `PLATE`).
- **Pamir property sets** (attached via `IfcRelDefinesByProperties`):
  - `Pamir Frame` on each `IfcElementAssembly` — `Weight` (from summed timber
    volume × 420 kg/m³), `DesignResult = Success`, `ProductionSet = 1`.
  - `Pamir Support` on every `IfcBuildingElementProxy` — `Type = WoodWall`,
    `Face = Bottom`.
  - `Pamir Member` on every `IfcMember` — `SiteFixed = False` (members are
    factory-fabricated inside the truss, so they are not fixed on site).

## 5. Calibrated pricing model

The pricing formula was recalibrated to Pamir quote metrics in both the backend
(`agent/src/agent.py` `generate_quote`) and the frontend mirror
(`src/components/pricing-breakdown-modal.tsx` `computePricingBreakdown`), so
both code paths agree.

Derived quantities (from floor area `A`):

| Quantity | Formula |
| --- | --- |
| Joints | `round(A * 1.32)` |
| Timber volume (m³) | `A * 0.254` |
| Trusses | `round(A * 0.147)` |
| Support nodes | `trusses * 2` |
| Bracket count | `round(support_nodes * 1.6)` |

Cost coefficients (CZK):

| Component | Formula |
| --- | --- |
| Gusset plates | `joints * 50` |
| Timber (C24) | `timber_volume * 6200` |
| Assembly (labor + overhead) | `(trusses / 20) * 18000` |
| Hangers | `trusses * 120` |
| Metalwork (ABR90 brackets) | `bracket_count * 370` |

The component sum is multiplied by a roof-type factor (`gable` 1.0, `hip` 1.3,
`mono-pitch` 0.9, `flat` 0.8), then converted CZK → EUR at `/ 25`. The skill
references under `.agents/skills/run-generate-design/references/`
(`pricing-formula.md`, `tool-execution-simulation-spec.md`) were updated to the
same coefficients.

## Verification

- Client parser: `node scripts/test-ifc-parser.js`.
- Backend: `pytest test/test_ifc_builder.py`, `pytest test/test_pricing.py`.
- Generated IFC assertions on `generated/gable.ifc` (assemblies, proxies,
  property sets, member formatting).
- Full gates (`pytest`, `npx tsc --noEmit`, `npm run lint`) pass at or within
  the recorded baselines under `.ralph/baselines/pamir-ifc-pricing-bridge-*`.
