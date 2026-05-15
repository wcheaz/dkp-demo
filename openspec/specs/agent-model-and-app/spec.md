## ADDED Requirements

### Requirement: DeepSeekModel class extends OpenAIModel
The system SHALL define a `DeepSeekModel` class that subclasses `pydantic_ai.models.openai.OpenAIModel` and overrides both `request()` and `request_stream()` to call a private `_ensure_thinking_parts()` patching method before delegating to the superclass.

#### Scenario: DeepSeekModel patches missing ThinkingPart
- **WHEN** a `ModelResponse` message in the message history lacks any `ThinkingPart`
- **THEN** the method SHALL append a `ThinkingPart` with `id="reasoning_content"` and `provider_name="deepseek"` to that message's parts list

#### Scenario: DeepSeekModel patches missing TextPart and ToolCallPart
- **WHEN** a `ModelResponse` message lacks both `TextPart` and `ToolCallPart`
- **THEN** the method SHALL prepend a `TextPart(content=".")` to that message's parts list

### Requirement: Model instance configured from environment
The system SHALL create a module-level `model` instance of `DeepSeekModel` using `OPENAI_MODEL` env var (default `"deepseek-chat"`) and `DeepSeekProvider(api_key=OPENAI_API_KEY)`.

#### Scenario: Default model when env var absent
- **WHEN** `OPENAI_MODEL` environment variable is not set
- **THEN** the model SHALL use `"deepseek-chat"` as the model name

#### Scenario: Custom model from env var
- **WHEN** `OPENAI_MODEL` is set to a custom value
- **THEN** the model SHALL use that value as the model name

### Requirement: Environment variables loaded from .env
The system SHALL call `load_dotenv(dotenv_path="../.env")` at module level to load environment variables from the agent package's `.env` file.

#### Scenario: .env file loaded
- **WHEN** the agent module is imported
- **THEN** environment variables from `../.env` SHALL be available via `os.getenv()`

### Requirement: ASGI app exposes AG-UI endpoint
The system SHALL create a Starlette ASGI app via `agent.to_ag_ui(deps=StateDeps(state=YourState()))` that serves the AG-UI protocol.

#### Scenario: AG-UI app creation
- **WHEN** `main.py` is loaded
- **THEN** an ASGI app SHALL exist that delegates agent interactions through the AG-UI protocol

### Requirement: Health check endpoint
The system SHALL register a `/api/health` GET route that returns `{"status": "healthy", "message": "Application is running"}` with HTTP 200.

#### Scenario: Health check responds
- **WHEN** a GET request is sent to `/api/health`
- **THEN** the response SHALL have status 200 and JSON body with `status` and `message` fields

### Requirement: Logfire instrumentation
The system SHALL configure Logfire via `logfire.configure()` and `logfire.instrument_pydantic_ai()` before creating the app.

#### Scenario: Logfire configured
- **WHEN** `main.py` is loaded
- **THEN** Logfire SHALL be configured and PydanticAI instrumentation SHALL be active

### Requirement: Knowledge base directory constant
The system SHALL define `KNOWLEDGE_BASE_DIR` as `Path(__file__).resolve().parent.parent / "knowledge" / "trusses-ai-english"`.

#### Scenario: Constant resolves correctly
- **WHEN** the module is imported from `agent/src/agent.py`
- **THEN** `KNOWLEDGE_BASE_DIR` SHALL point to `agent/knowledge/trusses-ai-english/`
