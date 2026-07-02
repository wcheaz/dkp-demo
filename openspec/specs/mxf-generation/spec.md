## Purpose

Python module for generating valid MiTek Exchange XML (`.mxf` Layout format) byte streams containing wall definitions and placements derived from active design parameters, ensuring compatibility with MiTek Pamir imports.

## Requirements

### Requirement: Generate Layout MXF File

The backend SHALL generate a valid MiTek Exchange XML (`.mxf` Layout format) byte stream containing wall definitions and placements derived from active design parameters, ensuring compatibility with MiTek Pamir imports.

#### Scenario: Successful MXF generation for a rectangular building layout
- **GIVEN** active [DesignParameters](file:///home/ncheaz/git/dkp-demo/agent/src/agent.py#L170-L180) specifying width = 10.0m, depth = 6.0m, wall height = 2.7m, and wall thickness = 0.2m
- **WHEN** [build_mxf](file:///home/ncheaz/git/dkp-demo/agent/src/mxf_builder.py) is invoked
- **THEN** the generated XML SHALL contain:
  - An `<Mxf>` root element with attributes `version="MXF Version 5.11"`, `originator="Antigravity Layout Builder"`, and namespace declarations `xmlns:xsd` and `xmlns:xsi`
  - A `<BuildingList>` containing a `<Building>` with a `<BuildingWallList>` of exactly 4 walls (`W0` to `W3`)
  - A `<Position>` vector for each wall where `origin` and `xAxis` reflect wall lengths of 10.0m (W0, W2) and 6.0m (W1, W3)
  - A `zAxis` coordinate vector for each wall pointing **inwards** (e.g. `zAxis` direction `(0, 1, 0)` for `W0`, `(-1, 0, 0)` for `W1`, `(0, -1, 0)` for `W2`, `(1, 0, 0)` for `W3`)
  - A `<WallList>` containing the four wall definitions, each containing a `<SkinList>` with a front face skin polygon starting at X=0 and ending at X=length, and a back face skin polygon starting at X=0.2 and ending at X=length-0.2
  - A `<WallPlateList>` defining a wall plate with offset="0.05", height="0.05", and width="0.1"

#### Scenario: MXF generation rejects invalid dimensions
- **GIVEN** active [DesignParameters](file:///home/ncheaz/git/dkp-demo/agent/src/agent.py#L170-L180) with missing floor plan dimensions
- **WHEN** [build_mxf](file:///home/ncheaz/git/dkp-demo/agent/src/mxf_builder.py) is invoked
- **THEN** the system SHALL raise a ValueError
