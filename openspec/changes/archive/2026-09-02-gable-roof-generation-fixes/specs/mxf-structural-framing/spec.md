## ADDED Requirements

### Requirement: Generate Full-Span Gable Trusses
For gable roof types, the backend geometry solver SHALL generate a single, unified full-span truss geometry spanning the entire width of the building, with support coordinates located at both outer load-bearing walls.

#### Scenario: Full-span truss generation
- **GIVEN** active DesignParameters specifying a gable roof with width = 10.0m
- **WHEN** the geometry solver is invoked to generate truss members
- **THEN** it SHALL output a single bottom chord of length 10.0m (plus overhangs) and two sloping top chords meeting at a single central ridge at X = 5.0m

### Requirement: Truss Height Transport Split
The geometry solver SHALL detect when the total height of a truss exceeds the transport limit of 3.3m, and in such cases, split the truss definition into two horizontal parts (a base frame and a cap frame) in the exported XML.

#### Scenario: Splitting tall trusses
- **GIVEN** active DesignParameters specifying a gable roof with a height of 3.8m
- **WHEN** the geometry solver generates the truss frames
- **THEN** the output frame definition SHALL contain two Parts:
  - Part 1 (Base): Extends up to a height of 2.8m, ending in a horizontal chord
  - Part 2 (Cap): A triangular cap frame of height 1.0m resting on Part 1

### Requirement: Gable End Truss Placement
The system SHALL place specialized `GableEnd` panel frames at the two outermost ends of the building frame layout instead of standard common trusses.

#### Scenario: Gable ends placed at boundaries
- **GIVEN** a building depth of 15.0m with 14 truss rows
- **WHEN** the building frame list is generated
- **THEN** the first frame (row 0 at Y = inset) and the last frame (row 13 at Y = depth - inset) SHALL be assigned the family "GableEnd" and type "PanelFrame"

### Requirement: Roof Slope Bracing
The system SHALL generate `<EngineeredBrace>` elements located along the roof slope, referencing the top chords of the trusses.

#### Scenario: Sloped purlin and wind brace generation
- **GIVEN** a sloped roof frame definition
- **WHEN** the engineered brace list is generated
- **THEN** the list SHALL contain purlin braces spaced at 1.0m intervals along the top chords and diagonal braces running at 45 degrees relative to the truss span
