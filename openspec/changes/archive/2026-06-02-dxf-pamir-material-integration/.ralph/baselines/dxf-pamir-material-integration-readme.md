# Pre-flight Quality Gate Baseline

**Date:** 2026-06-02
**Test file:** `test/test_dxf_builder.py`
**Result:** 12 failed, 40 passed, EXIT=1

## Failed Tests (12)

All failures are related to the disabled `Title_Block` layer:

### TestTitleBlock (3 failures)
1. `TestTitleBlock::test_rectangle_lines` — expects 4 LINE entities on `Title_Block` layer (found 0)
2. `TestTitleBlock::test_mtext_content_populated` — expects 5 MTEXT entities on `Title_Block` layer (found 0)
3. `TestTitleBlock::test_none_fields_use_defaults` — expects "Building" in MTEXT content on `Title_Block` layer (found none)

### TestRoundTripAllRoofTypes (4 failures)
4. `TestRoundTripAllRoofTypes::test_all_five_layers_present[Gable]` — asserts `_ALL_FIVE_LAYERS` subset includes `Title_Block`
5. `TestRoundTripAllRoofTypes::test_all_five_layers_present[Hip]` — same assertion
6. `TestRoundTripAllRoofTypes::test_all_five_layers_present[Mono-pitch]` — same assertion
7. `TestRoundTripAllRoofTypes::test_all_five_layers_present[Flat]` — same assertion

### TestGenerateExampleFiles (5 failures)
8. `TestGenerateExampleFiles::test_write_example_dxf[gable]` — asserts `_ALL_FIVE_LAYERS` subset includes `Title_Block`
9. `TestGenerateExampleFiles::test_write_example_dxf[hip]` — same assertion
10. `TestGenerateExampleFiles::test_write_example_dxf[mono-pitch]` — same assertion
11. `TestGenerateExampleFiles::test_write_example_dxf[flat]` — same assertion
12. `TestGenerateExampleFiles::test_write_example_dxf[decimal]` — same assertion

## Root Cause

The `Title_Block` layer generation is disabled in `agent/src/dxf_builder.py`. The tests still assert on `_ALL_FIVE_LAYERS` which includes `Title_Block`, and the `TestTitleBlock` class expects entities that are never produced.

No other test failures exist — all 40 passing tests cover Floor Plan, Roof Outline, Trusses, Dimensions, Layer Colors, and DXF validity correctly.
