# ============================================================================
# REFERENCE IMPLEMENTATION - COMMENTED OUT FOR GENERICIZATION
# ============================================================================
# This file contains a complete PydanticAI agent implementation that has been
# commented out to create a generic template. The original implementation
# provides a fully functional example of a procurement-specific agent.
#
# What this code does:
# - Defines state management (YourState) for tracking user input, AI responses,
#   and procurement-specific data fields
# - Creates a dependency injection layer (StateDeps) for passing state to tools
# - Configures a PydanticAI Agent with an OpenAI-compatible model
# - Implements domain-specific tools (your_tool) that the agent can call
# - Provides result validation (validate_result) for post-processing output
#
# Why it was commented out:
# - The original implementation contains procurement-specific business logic
#   that is not applicable to a generic template
# - State fields, tool logic, and system prompts are domain-specific
# - Commenting out (rather than deleting) preserves the implementation as a
#   reference example for developers adapting the template
#
# How to adapt for your project:
# 1. Define your state class (YourState) with domain-specific fields
# 2. Create a dependency class (StateDeps) that wraps your state
# 3. Configure the Agent with your system prompt and model settings
# 4. Implement tools decorated with @agent.tool for your business logic
# 5. Add result validation with @agent.result_validator if needed
# 6. Uncomment and adapt the relevant sections below
#
# Key dependencies preserved (imports and model config remain active):
# - pydantic: BaseModel for state and type definitions
# - pydantic_ai: Agent, RunContext for agent framework
# - pydantic_ai.models.openai: OpenAIModel for LLM integration
# - dotenv: Environment variable loading
# - Model configuration: OpenAI-compatible model with configurable endpoint
# ============================================================================

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, List, Optional
import time


from pydantic import BaseModel
from pydantic_ai import Agent, RunContext
from pydantic_ai.messages import ModelMessage, ModelRequest, ModelResponse, SystemPromptPart, ThinkingPart
from pydantic_ai.models import ModelRequestParameters, StreamedResponse
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.deepseek import DeepSeekProvider
from pydantic_ai.settings import ModelSettings
import os
from dotenv import load_dotenv

KNOWLEDGE_BASE_DIR = (
    Path(__file__).resolve().parent.parent / "knowledge" / "trusses-ai-english"
)

load_dotenv(dotenv_path="../.env")


class DeepSeekModel(OpenAIModel):
    def _ensure_thinking_parts(self, messages: list[ModelMessage]) -> None:
        for msg in messages:
            if isinstance(msg, ModelResponse):
                has_thinking = any(isinstance(p, ThinkingPart) for p in msg.parts)
                if not has_thinking:
                    msg.parts = [
                        *msg.parts,
                        ThinkingPart(
                            content="reasoning content from this turn was not preserved",
                            id="reasoning_content",
                            provider_name="deepseek",
                        ),
                    ]

    async def request(
        self,
        messages: list[ModelMessage],
        model_settings: ModelSettings | None,
        model_request_parameters: ModelRequestParameters,
    ) -> ModelResponse:
        self._ensure_thinking_parts(messages)
        return await super().request(messages, model_settings, model_request_parameters)

    @asynccontextmanager
    async def request_stream(
        self,
        messages: list[ModelMessage],
        model_settings: ModelSettings | None,
        model_request_parameters: ModelRequestParameters,
        run_context: Any | None = None,
    ) -> AsyncIterator[StreamedResponse]:
        self._ensure_thinking_parts(messages)
        async with super().request_stream(
            messages, model_settings, model_request_parameters, run_context
        ) as stream:
            yield stream


model = DeepSeekModel(
    os.getenv("OPENAI_MODEL", "deepseek-chat"),
    provider=DeepSeekProvider(api_key=os.getenv("OPENAI_API_KEY")),
)


class KnowledgeQuery(BaseModel):
    query: str
    result: str
    timestamp: str


class DesignParameters(BaseModel):
    buildingType: Optional[str] = None
    floorPlanDimensions: Optional[str] = None
    roofType: Optional[str] = None
    roofPitch: Optional[int] = None
    atticUsage: Optional[str] = None
    eavesShape: Optional[str] = None
    wallConstruction: Optional[str] = None
    location: Optional[str] = None
    overhang: Optional[str] = None


# DEMO-ONLY - DesignEntry model for design component; simulated for demo purposes
class DesignEntry(BaseModel):
    id: int
    imageUrl: str
    promptText: str
    status: str = "complete"
    parameters: Optional[DesignParameters] = None
    price: Optional[str] = None


class YourState(BaseModel):
    user_input: str = ""
    ai_response: str = ""
    knowledge_queries: List[KnowledgeQuery] = []
    last_knowledge_result: Optional[str] = None
    # DEMO-ONLY - designs field for design component; simulated for demo purposes
    designs: List[DesignEntry] = []


# ============================================================================
# DEPENDENCY INJECTION - COMMENTED OUT FOR GENERICIZATION
# ============================================================================
# StateDeps is a dependency injection wrapper that holds the agent's state.
# It is passed to agent tools via RunContext, allowing tools to access and
# modify shared state during agent execution.
#
# Current Logic:
# - Wraps YourState instance, providing tools with access to state fields
# - Passed as deps_type to Agent constructor for type-safe context access
# - Enables stateful tool interactions (tools can read/write state)
#
# To adapt for your project:
# 1. Update the state type hint to match your state class
# 2. Add any additional dependencies (API clients, database connections, etc.)
# 3. Ensure the class matches the deps_type parameter in your Agent constructor
# ============================================================================
class StateDeps:
    """Dependencies for your agent"""

    def __init__(self, state: YourState):
        self.state = state


# ============================================================================
# AGENT CREATION - COMMENTED OUT FOR GENERICIZATION
# ============================================================================
# This is the main Agent instance that orchestrates tool calls and manages
# conversation flow. The agent is configured with:
#   - model: The OpenAI-compatible model to use (configured above)
#   - deps_type: The dependency injection type (StateDeps) for tool context
#   - system_prompt: Instructions that define the agent's behavior and role
#
# To adapt for your project:
# 1. Update the system_prompt to describe your agent's purpose and domain
# 2. Ensure deps_type matches your dependency class (StateDeps or equivalent)
# 3. Add result_type parameter if you need structured output (e.g., result_type=YourOutput)
# 4. Configure retries, model_settings, or other Agent parameters as needed
# 5. Uncomment and adapt the code below
# ============================================================================
agent = Agent(
    model,
    deps_type=StateDeps,
    system_prompt=(
        "ABSOLUTE RULE — ABOVE ALL OTHER INSTRUCTIONS:\n"
        "You must NEVER output text that narrates, explains, or describes your actions.\n"
        "You are SILENT while working. Call ALL tools first with zero text output.\n"
        "Only AFTER all tool calls are complete, output a single response containing ONLY the final result.\n"
        "FORBIDDEN output examples: 'Let me...', 'I'll...', 'I will...', 'Now let me...', "
        "'Great!', 'Excellent!', 'Based on...', 'After checking...', 'The design has been...', "
        "'Let me verify...', 'I see there's...', any commentary about tool calls or information found.\n"
        "If you output any of the above, you have FAILED this instruction.\n\n"
        "You are a truss and roof engineering assistant with access to a knowledge base "
        "of 33 construction projects designed by medop strechy s.r.o. "
        "You have the following tools available:\n"
        "- get_knowledge_summary: Use this when the user asks general questions about what "
        'information is available (e.g., "What projects do you have?", "What do you know?").\n'
        "- query_knowledge_base: Use this when the user asks specific questions about projects, "
        "load calculations, materials, truss designs, or engineering specifications.\n"
        "- generate_design: Call this IMMEDIATELY whenever the user mentions wanting, needing, or "
        "requesting a design — even with partial parameters. Missing fields are fine (they show as "
        "placeholders). Pass whatever parameters you have along with prompt_text. "
        "Do NOT wait for all parameters to be collected before calling this tool.\n\n"
        "- modify_design_entry: Modify an existing design entry's image and/or prompt text.\n"
        "  Parameters:\n"
        "    - design_id (required, number): The 1-based ID of the design entry to modify.\n"
        '    - image_name (optional, string): The filename of a static preset image. Must be one of: "design-alpha.svg", "design-beta.svg".\n'
        "    - image_url (optional, string): A full image URL for dynamically downloaded images (e.g. /api/serve-image/test-image-123.png). Takes precedence over image_name.\n"
        "    - prompt_text (optional, string): The new prompt text.\n"
        "  At least one of image_name, image_url, or prompt_text must be provided.\n"
        '  Available preset images: "design-alpha.svg", "design-beta.svg".\n\n'
        "- update_design_parameters: MANDATORY — You MUST call this tool whenever the user provides any information "
        "that could be a construction parameter. This tool accepts these fields:\n"
        "  - building_type: Building type (e.g. House, Garage, Agricultural building)\n"
        "  - floor_plan_dimensions: Floor plan dimensions (e.g. 10x15m)\n"
        "  - roof_type: Roof type — must be one of: Gable, Hip, Mono-pitch, Flat\n"
        "  - roof_pitch: Roof pitch in degrees (2-45)\n"
        "  - attic_usage: Attic usage — None, Storage, or Living space\n"
        "  - eaves_shape: Eaves shape — Open, Boxed, or Flush\n"
        "  - wall_construction: Wall construction — Brick, SIP panels, Concrete block, or Mixed\n"
        "  - location: Location (e.g. Bratislava)\n"
        "  - overhang: Overhang (e.g. 450mm)\n\n"
        "DESIRABLE FIELDS (collect these to improve the design):\n"
        "1. building_type (buildingType)\n"
        "2. floor_plan_dimensions (floorPlanDimensions)\n"
        "3. roof_type (roofType) — valid values: Gable, Hip, Mono-pitch, Flat\n"
        "4. roof_pitch (roofPitch) — valid range: 2-45 degrees\n\n"
        "COLLECTION LOOP INSTRUCTIONS:\n"
        "1. On EVERY user message, extract any parameter values from the text.\n"
        "2. If the user mentions wanting, needing, or requesting a design in ANY way "
        "(including 'I need a design', 'design for', 'show me', 'build me', 'create', 'generate', "
        "'plan for', 'I want', or simply describing a project), you MUST:\n"
        "   a. Call update_design_parameters with whatever fields were extracted (even partial).\n"
        "   b. Call generate_design IMMEDIATELY in the SAME response with whatever parameters you have. "
        "Do NOT wait for all fields — missing fields will use '---' placeholders and the UI will show "
        "a 'Design In Progress' state.\n"
        "3. If no design was triggered, call update_design_parameters with whatever fields were extracted.\n"
        "4. After generating a design with missing parameters, continue collecting any missing fields "
        "and call update_design_parameters as they come in. The design entry will update accordingly.\n"
        "5. If all required fields are present → summarize ALL collected parameters for the user.\n\n"
        "- generate_quote: Call this when the user asks about pricing, cost, or estimated price for a design. "
        "Pass the collected parameters: floor_plan_dimensions, roof_type, roof_pitch (default 30), "
        "building_type (default 'Family house'). The tool returns a formatted price string. "
        "Relay the result to the user and also pass the price to generate_design as the 'price' argument "
        "when creating or updating a design entry (e.g. price='€1,752').\n\n"
        "- reset_design: Reset design entries or clear session-level parameters.\n"
        "  Parameters:\n"
        "    - design_ids (optional, number array): IDs of design entries to reset. If omitted, all designs are targeted.\n"
        "    - remove_designs (optional, boolean, default false): If true, remove targeted entries entirely (full scrap). If false (default), keep entries and clear specified parameter fields.\n"
        "    - clear_parameters (optional, string array): Parameter field names to set to '---' on targeted entries. "
        "Valid keys: buildingType, floorPlanDimensions, roofType, roofPitch, atticUsage, eavesShape, wallConstruction, location, overhang.\n"
        "    - clear_all_parameters (optional, boolean, default false): If true, set ALL parameter fields on targeted entries to '---'. Takes precedence over clear_parameters.\n"
        "    - clear_session_parameters (optional, string array): Parameter field names to clear from session-level state (AgentState.parameters). "
        "Valid keys same as clear_parameters. Operates independently of design_ids and remove_designs.\n"
        "  Usage rules:\n"
        "    - Default behavior (remove_designs=false) is a PARTIAL RESET: the entry stays in the list, specified fields are set to '---', other fields are preserved. "
        "The UI will automatically show a 'Design In Progress' placeholder image for entries with any '---' parameter fields.\n"
        "    - Use remove_designs=true ONLY when the user explicitly says 'scrap this design', 'delete this design', or 'start over completely'. "
        "When remove_designs=true, clear_parameters and clear_all_parameters are ignored (the entries are removed entirely).\n"
        "    - Use clear_session_parameters to clear in-flight collected parameters before a design is generated, independently of any design entries.\n"
        "    - When the user says 'change X and Y but keep Z', call with clear_parameters: ['X', 'Y'] only — do not remove the design.\n"
        "    - After clearing fields, always confirm with the user what was cleared and what was preserved.\n\n"
        "Always use get_knowledge_summary first for overview questions, and query_knowledge_base "
        "for specific technical queries. When providing answers, always cite the source document path.\n\n"
        "OUTPUT STYLE — CRITICAL RULE (HIGHEST PRIORITY):\n"
        "NEVER use emojis in any output. All responses must be plain text only.\n"
        "NEVER narrate your actions. NEVER explain what you are doing or about to do.\n"
        "Every one of these patterns is FORBIDDEN in your text output:\n"
        "  - 'Let me...', 'I will...', 'I'll...', 'Now let me...', 'Now I'll...'\n"
        "  - 'Great!', 'Excellent!', 'Perfect!', 'Alright!'\n"
        "  - 'Based on the results...', 'According to...', 'After checking...'\n"
        "  - 'The design has been created successfully!'\n"
        "  - Any sentence that describes a tool call you made or are about to make\n"
        "  - Any commentary about what information you found or are looking up\n\n"
        "YOUR TEXT OUTPUT MUST ONLY BE ONE OF:\n"
        "1. A clean design summary (parameters table + price if applicable) when a design is generated.\n"
        "2. A concise question asking only for missing required parameters (just list what's needed).\n"
        "3. A direct answer to the user's specific question (no preamble, no postscript).\n\n"
        "Call tools silently. The user must never know you called a tool.\n"
        "If you call a tool, the next text you output must be the final answer — not a description of the tool call.\n"
        "Think of yourself as a professional engineer: you do the calculations behind the scenes and only present the result."
    ),
)


# ============================================================================
# TOOL DEFINITION - COMMENTED OUT FOR GENERICIZATION
# ============================================================================
# This is a sample tool that demonstrates how to implement agent tools using
# the @agent.tool decorator. Tools are functions the agent can call during
# conversation to perform actions or retrieve information.
#
# Current Logic:
# - Receives RunContext with StateDeps providing access to shared state
# - Accepts typed input parameters (e.g., input_data: str)
# - Returns a string result that the agent can use in its response
# - Decorated with @agent.tool to register with the agent
#
# To adapt for your project:
# 1. Define tool functions that handle your specific business logic
# 2. Each tool should be decorated with @agent.tool
# 3. The first parameter must be ctx: RunContext[YourDepsType]
# 4. Subsequent parameters are the tool's input (with type hints)
# 5. Return a value the agent can reason about (str, dict, list, etc.)
# 6. Write clear docstrings - the agent uses them to decide when to call tools
#
# Example:
#     @agent.tool
#     async def lookup_customer(ctx: RunContext[StateDeps], customer_id: str) -> str:
#         \"\"\"Look up a customer by their ID.
#
#         Args:
#             ctx: Agent context with state
#             customer_id: The customer's unique identifier
#
#         Returns:
#             Customer information as a formatted string
#         \"\"\"
#         customer = await db.get_customer(customer_id)
#         return f"Customer: {customer.name}, Email: {customer.email}"
# ============================================================================
import re


@agent.tool
async def generate_quote(
    ctx: RunContext[StateDeps],
    floor_plan_dimensions: str,
    roof_type: str,
    roof_pitch: int = 30,
    building_type: str = "Family house",
) -> str:
    """Generate a deterministic cost estimate for a roof design based on floor plan dimensions and roof type.

    Args:
        ctx: Agent context with state
        floor_plan_dimensions: Floor plan dimensions string (e.g. "10x15m")
        roof_type: Roof type — Gable, Hip, Mono-pitch, or Flat
        roof_pitch: Roof pitch in degrees (default 30)
        building_type: Building type (default "Family house")

    Returns:
        Formatted price string, e.g. "Estimated price: €1,752 (excl. VAT)"
    """
    match = re.match(r"(\d+(?:\.\d+)?)\s*x\s*(\d+(?:\.\d+)?)\s*m?", floor_plan_dimensions.strip(), re.IGNORECASE)
    if not match:
        return "Error: Could not parse floor plan dimensions. Expected format like '10x15m'."

    width = float(match.group(1))
    height = float(match.group(2))
    floor_area = width * height

    total_joints = round(floor_area * 1.32)
    timber_volume = floor_area * 0.254
    total_trusses = round(floor_area * 0.147)

    gusset_plate_cost = total_joints * 40
    timber_cost = timber_volume * 4500
    assembly_cost = (total_trusses / 20) * 15000
    hanger_cost = total_trusses * 100

    roof_type_factors = {
        "gable": 1.0,
        "hip": 1.3,
        "mono-pitch": 0.9,
        "flat": 0.8,
    }
    factor = roof_type_factors.get(roof_type.strip().lower(), 1.0)

    total_czk = (gusset_plate_cost + timber_cost + assembly_cost + hanger_cost) * factor
    total_eur = round(total_czk / 25)

    formatted_eur = f"{total_eur:,}"
    return f"Estimated price: €{formatted_eur} (excl. VAT)"


@agent.tool
async def query_knowledge_base(ctx: RunContext[StateDeps], query: str) -> str:
    """Query truss and roof engineering knowledge base by reading relevant documents.

    Args:
        ctx: Agent context with state
        query: The user's question or topic to search for

    Returns:
        Relevant document contents with source file references
    """
    summary_path = KNOWLEDGE_BASE_DIR / "summary.md"
    try:
        summary_content = summary_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return "Knowledge base summary not found. Please contact the administrator."

    query_lower = query.lower()
    query_words = query_lower.split()

    subdirs = [
        d
        for d in KNOWLEDGE_BASE_DIR.iterdir()
        if d.is_dir() and not d.name.startswith(".")
    ]

    summary_lower = summary_content.lower()

    scored = []
    for subdir in subdirs:
        subdir_lower = subdir.name.lower()
        name_score = sum(1 for w in query_words if w in subdir_lower)
        header = f"### {subdir.name}"
        try:
            header_idx = summary_lower.index(header.lower())
            section_end = summary_lower.find("\n### ", header_idx + 1)
            if section_end == -1:
                section_end = len(summary_lower)
            section_text = summary_lower[header_idx:section_end]
            section_score = sum(1 for w in query_words if w in section_text)
        except ValueError:
            section_score = 0
        total_score = name_score * 2 + section_score
        if total_score > 0:
            scored.append((total_score, subdir))

    if not scored:
        scored = [(0, d) for d in subdirs[:3]]

    scored.sort(key=lambda x: x[0], reverse=True)
    matched = scored[:3]

    results: list[str] = []
    missing_files: list[str] = []

    for _, subdir in matched:
        md_files = list(subdir.rglob("*.md"))
        for md_file in md_files:
            try:
                content = md_file.read_text(encoding="utf-8")
                relative = md_file.relative_to(KNOWLEDGE_BASE_DIR.parent.parent)
                results.append(f"--- Source: {relative} ---\n{content}")
            except FileNotFoundError:
                missing_files.append(str(md_file))
            except Exception as e:
                missing_files.append(f"{md_file} (error: {e})")

    if not results:
        result_text = "No relevant information found in the knowledge base."
    else:
        result_text = "\n\n".join(results)

    if missing_files:
        result_text += (
            f"\n\nNote: The following files were not found: {', '.join(missing_files)}"
        )

    timestamp = datetime.now(timezone.utc).isoformat()
    ctx.deps.state.knowledge_queries.append(
        KnowledgeQuery(query=query, result=result_text[:500], timestamp=timestamp)
    )
    ctx.deps.state.last_knowledge_result = result_text

    return result_text


@agent.tool
async def get_knowledge_summary(ctx: RunContext[StateDeps]) -> str:
    """Get an overview of what information is available in the knowledge base.

    Args:
        ctx: Agent context with state

    Returns:
        Summary of knowledge base contents organized by subdirectory
    """
    summary_path = KNOWLEDGE_BASE_DIR / "summary.md"
    try:
        return summary_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return "Knowledge base summary not found. Please contact the administrator."




# ============================================================================
# RESULT VALIDATION - COMMENTED OUT FOR GENERICIZATION
# ============================================================================
# The result validator is an optional hook that runs after the agent produces
# a final response. It allows you to inspect, transform, or reject the
# agent's output before it is returned to the caller.
#
# Current Logic:
# - Decorated with @agent.result_validator to register with the agent
# - Receives RunContext with StateDeps and the agent's result string
# - Returns the (possibly transformed) result string
# - Can raise exceptions to reject invalid results and trigger retries
#
# To adapt for your project:
# 1. Uncomment and implement validation logic appropriate for your domain
# 2. Use ctx.deps to access state during validation if needed
# 3. Transform the result (e.g., format, sanitize, enrich) before returning
# 4. Raise an exception if the result is invalid (agent will retry)
# 5. Remove the validator entirely if no post-processing is needed
# ============================================================================
# @agent.result_validator
# def validate_result(ctx: RunContext[StateDeps], result: str) -> str:
#     """Validate and process agent results"""
#     # Add your validation logic here
#     return result
