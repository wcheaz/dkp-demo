## 1. Verify existing Phase 2 foundation

- [x] 1.1 Verify floor-plan and roof-outline geometry is complete. Run existing tests (if any) against `dxf_builder.py` and confirm `build_dxf("10x15m", "Gable")` produces valid DXF with `Floor_Plan` and `Roof_Outline` layers. Fix any regressions before proceeding.
  - Done when: `ezdxf.read(BytesIO(build_dxf(params)))` succeeds for all four roof types (gable, hip, mono-pitch, flat).
  - Verify by: Running `pytest test/ -k dxf` (or equivalent test command).

## 2. Truss layout geometry

- [x] 2.1 Add truss count calculation and cross-section drawing functions to `dxf_builder.py`. Add constants `LAYER_TRUSSES = "Trusses"`, a `_compute_truss_count(width_m, depth_m) -> int` function returning `max(2, round(width_m * depth_m * 0.147))`, and a `_draw_trusses(msp, w, d, roof_key, roof_pitch)` function that draws evenly-spaced cross-section LINE entities on the `Trusses` layer. Cross-section shape depends on roof type: isosceles triangle (gable/hip), right triangle (mono-pitch), horizontal line (flat). Ridge height = `(w/2) * tan(pitch * pi/180)` with defaults of 30° (gable/hip), 10° (mono-pitch). Edge inset = 5% of shorter dimension.
  - Done when: `build_dxf` output for a 10x15m gable building with pitch=30 contains a `Trusses` layer with LINE entities forming triangular cross-sections at the expected Y-coordinates, with 22 trusses, first inset by 500mm.
  - Verify by: Running `pytest test/ -k dxf` after writing tests, or manually inspecting DXF in a CAD viewer.

## 3. Dimensions and annotations

- [x] 3.1 Add dimension and text annotation functions to `dxf_builder.py`. Add constants `LAYER_DIMENSIONS = "Dimensions"`, a `_parse_overhang(raw: Optional[str]) -> Optional[float]` function, and a `_draw_dimensions(msp, w, d, w_m, d_m, roof_key, ridge_height_mm, overhang_mm)` function. Add horizontal `msp.add_linear_dim()` for width (below floor plan, offset = 10% of depth), vertical for depth (left of floor plan, offset = 10% of width), vertical for ridge height (right of first truss, gable/hip only), and horizontal for overhang (if parseable). Add TEXT entities for "Width: <W>m", "Depth: <D>m", "Ridge Height: <H>m". Text height = 250mm.
  - Done when: `build_dxf` output for a 10x15m gable building contains a `Dimensions` layer with at least 3 DIMENSION entities and 3 TEXT entities. Flat roof produces no ridge height dimension.
  - Verify by: Running tests, or inspecting DXF output for dimension entity presence and values.

## 4. Title block

- [x] 4.1 Add title block drawing function to `dxf_builder.py`. Add constant `LAYER_TITLE_BLOCK = "Title_Block"` and a `_draw_title_block(msp, w, d, params)` function that draws a 40000x15000mm rectangle (4 LINEs) in the lower-right area with MTEXT entities for buildingType (fallback "Building"), location (fallback "Location not specified"), current UTC date as YYYY-MM-DD, "Plan: <W>x<D>m", and "Roof: <type>". Text height = 800mm.
  - Done when: `build_dxf` output contains a `Title_Block` layer with 4 LINE entities forming the border rectangle and 5 MTEXT entities with correct content. Handles None values for buildingType and location without error.
  - Verify by: Running tests that check layer entity count and MTEXT content.

## 5. Integration and verification

- [x] 5.1 Wire the three new drawing functions into `build_dxf`. After the existing `_draw_floor_plan` and `_ROOF_DRAWERS` calls, add layer creation for `Trusses`, `Dimensions`, `Title_Block`, then call `_draw_trusses`, `_draw_dimensions`, and `_draw_title_block` in sequence. Ensure `build_dxf` returns valid DXF for all four roof types with all five layers present.
  - Done when: `build_dxf` called with `floorPlanDimensions="10x15m"`, `roofType="Gable"`, `roofPitch=30` produces DXF bytes that pass `ezdxf.read()` and contain exactly 5 layers: `Floor_Plan`, `Roof_Outline`, `Trusses`, `Dimensions`, `Title_Block`.
  - Verify by: `pytest test/ -k dxf` — all tests pass, including a round-trip validation test for each roof type.

- [ ] 5.2 Write unit tests in `test/` for the new geometry. Tests MUST cover: (a) truss count calculation for various building sizes including minimum, (b) truss cross-section entity presence and coordinate sanity for each roof type, (c) dimension entity presence and measurement values, (d) title block rectangle and MTEXT content with both populated and None fields, (e) round-trip `ezdxf.read()` validation for all four roof types with all five layers. Each test creates a `DesignParameters` model, calls `build_dxf`, re-reads with `ezdxf.read()`, and asserts on layers and entities.
  - Done when: `pytest test/ -k dxf` passes with 100% of new tests green.
  - Verify by: `pytest test/ -k dxf --tb=short`
