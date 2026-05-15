## ADDED Requirements

### Requirement: KnowledgeQuery model
The system SHALL define a `KnowledgeQuery` Pydantic `BaseModel` with fields: `query: str`, `result: str`, `timestamp: str`.

#### Scenario: KnowledgeQuery instantiation
- **WHEN** a `KnowledgeQuery` is created with `query="test"`, `result="answer"`, `timestamp="2026-01-01T00:00:00Z"`
- **THEN** all three fields SHALL be accessible and correctly typed

### Requirement: DesignParameters model
The system SHALL define a `DesignParameters` Pydantic `BaseModel` with all optional string/int fields: `buildingType`, `floorPlanDimensions`, `roofType`, `roofPitch` (int), `atticUsage`, `eavesShape`, `wallConstruction`, `location`, `overhang` — each defaulting to `None`.

#### Scenario: DesignParameters with no values
- **WHEN** a `DesignParameters` is instantiated with no arguments
- **THEN** every field SHALL be `None`

#### Scenario: DesignParameters with partial values
- **WHEN** a `DesignParameters` is instantiated with `buildingType="House"` and `roofPitch=30`
- **THEN** `buildingType` SHALL be `"House"`, `roofPitch` SHALL be `30`, and all other fields SHALL be `None`

### Requirement: DesignEntry model
The system SHALL define a `DesignEntry` Pydantic `BaseModel` with fields: `id: int`, `imageUrl: str`, `promptText: str`, `status: str = "complete"`, `parameters: Optional[DesignParameters] = None`, `price: Optional[str] = None`.

#### Scenario: DesignEntry default status
- **WHEN** a `DesignEntry` is created with `id=1`, `imageUrl="test.png"`, `promptText="a design"`
- **THEN** `status` SHALL default to `"complete"` and `parameters` and `price` SHALL be `None`

### Requirement: YourState model
The system SHALL define a `YourState` Pydantic `BaseModel` with fields: `user_input: str = ""`, `ai_response: str = ""`, `knowledge_queries: List[KnowledgeQuery] = []`, `last_knowledge_result: Optional[str] = None`, `designs: List[DesignEntry] = []`.

#### Scenario: YourState default values
- **WHEN** a `YourState` is instantiated with no arguments
- **THEN** `user_input` SHALL be `""`, `knowledge_queries` SHALL be `[]`, and `designs` SHALL be `[]`

### Requirement: StateDeps dependency injection class
The system SHALL define a `StateDeps` class with `__init__(self, state: YourState)` storing state as `self.state`.

#### Scenario: StateDeps wraps state
- **WHEN** `StateDeps(state=YourState())` is created
- **THEN** `deps.state` SHALL be a `YourState` instance
