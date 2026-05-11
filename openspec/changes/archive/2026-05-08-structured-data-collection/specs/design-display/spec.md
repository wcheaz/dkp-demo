## MODIFIED Requirements

### Requirement: AgentState carries designs array
`AgentState` in `src/lib/types.ts` SHALL define a `designs` field of type `DesignEntry[]` and a `parameters` field of type `DesignParameters`. `DesignEntry` SHALL be an exported interface with `imageUrl: string` and `promptText: string`. `DesignParameters` SHALL be an exported interface with optional string/number fields for construction parameters. The old `procurement_codes`-related types and `your_data` field SHALL be removed from `AgentState`.

#### Scenario: AgentState type compiles with designs and parameters fields
- **WHEN** TypeScript compilation is run on `src/lib/types.ts`
- **THEN** the file SHALL compile without errors and `AgentState` SHALL have exactly two fields: `designs: DesignEntry[]` and `parameters: DesignParameters`.

#### Scenario: DesignEntry has required fields
- **WHEN** a `DesignEntry` object is created with `{ imageUrl: "tmp/next.svg", promptText: "test prompt" }`
- **THEN** the object SHALL satisfy the `DesignEntry` interface without TypeScript errors.

#### Scenario: AgentState accepts parameters field
- **WHEN** an `AgentState` object is created with `{ designs: [], parameters: { buildingType: "Family house" } }`
- **THEN** the object SHALL satisfy the `AgentState` type without TypeScript errors.

### Requirement: DesignComponent renders a scrollable list of design entries
The `DesignComponent` SHALL accept an `AgentState` containing a `designs` array of `DesignEntry` objects and a `parameters` field of type `DesignParameters`. The component SHALL render a parameter display section above the scrollable design cards container (see `design-params-display` capability). Each `DesignEntry` SHALL have an `imageUrl` (string) and a `promptText` (string). The component SHALL render one card per entry inside a scrollable container. Multiple cards SHALL be visible simultaneously. The scrollable container SHALL use `overflow-y: auto` so the user can scroll through the design history. Each card SHALL contain an `<img>` element with `src` set to the entry's `imageUrl` and a text element displaying the entry's `promptText`.

#### Scenario: Empty state when no designs exist
- **WHEN** the `designs` array on `AgentState` is empty or undefined
- **THEN** the component SHALL display an empty-state message indicating no designs are available, and SHALL render zero design cards. The parameter display section SHALL still render above the empty state.

#### Scenario: Single design entry displayed
- **WHEN** the `designs` array contains one `DesignEntry` with `imageUrl` set to `"tmp/next.svg"` and `promptText` set to `"Draw a flowchart of user login"`
- **THEN** the component SHALL render exactly one card containing an `<img>` element whose `src` attribute equals `"tmp/next.svg"` and a text element containing `"Draw a flowchart of user login"`.

#### Scenario: Multiple design entries displayed in order with scroll
- **WHEN** the `designs` array contains five entries in order: A, B, C, D, E
- **THEN** the component SHALL render five cards in the same order inside a scrollable container, each showing its own image and prompt text. At least two cards SHALL be visible without scrolling.
