## 1. Add ezdxf dependency

- [x] 1.1 Add `ezdxf` to `requirements.txt` and verify it imports successfully
  - Add `ezdxf` (latest stable) to `requirements.txt`
  - Run `python -c "import ezdxf; print(ezdxf.__version__)"` to confirm the import works
  - Done when: `ezdxf` appears in `requirements.txt` and `import ezdxf` succeeds without error

## 2. Implement dxf_builder module

- [x] 2.1 Create `agent/src/dxf_builder.py` with `build_dxf(params: DesignParameters) -> bytes`
  - Implement `build_dxf` accepting the existing `DesignParameters` model (import the model from `agent.src.agent`)
  - Parse `floorPlanDimensions` using regex `r"(\d+(?:\.\d+)?)\s*x\s*(\d+(?:\.\d+)?)\s*m?"`; raise `ValueError` on parse failure or `None` input
  - Convert meters to millimeters (multiply by 1000)
  - Create `ezdxf.new("R2000")` document, add `Floor_Plan` and `Roof_Outline` layers
  - Draw floor-plan rectangle as closed LWPOLYLINE on `Floor_Plan` layer with vertices at (0,0), (width,0), (width,depth), (0,depth)
  - Implement Gable roof: ridge line along longer axis center, two rafter lines from eave corners converging at ridge midpoint
  - Implement Hip roof: ridge line (length = building depth - width, centered), four hip lines from ridge endpoints to building corners
  - Implement Mono-pitch roof: LWPOLYLINE matching floor plan, marker LINE on high-side long edge
  - Implement Flat roof: closed LWPOLYLINE matching floor plan rectangle
  - Raise `ValueError` for `roofType=None` or unsupported types; case-insensitive matching for "gable", "hip", "mono-pitch", "flat"
  - Write DXF to `BytesIO` and return bytes
  - Done when: Module exists at `agent/src/dxf_builder.py`, `build_dxf` returns valid bytes for all 4 roof types, raises `ValueError` for invalid input

## 3. Add unit tests

- [x] 3.1 Create `test/test_dxf_builder.py` covering all spec scenarios
  - Test: valid DXF output is re-readable via `ezdxf.read(BytesIO(result))` and DXF version is AC1015
  - Test: floor-plan outline for "10x15m" — assert Floor_Plan layer has one LWPOLYLINE with correct vertices
  - Test: floor-plan outline for "8.5x12.3m" — assert decimal conversion
  - Test: `ValueError` for `floorPlanDimensions=None`
  - Test: `ValueError` for malformed dimensions string
  - Test: Gable roof outline on Roof_Outline layer with expected geometry
  - Test: Hip roof outline on Roof_Outline layer with ridge and hip lines
  - Test: Mono-pitch roof outline with high-side marker
  - Test: Flat roof outline matching floor plan
  - Test: `ValueError` for `roofType=None`
  - Test: `ValueError` for unsupported roof type
  - Done when: All tests pass via `pytest test/test_dxf_builder.py`
