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

import functools
import logging
import re
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, List, Optional
import time


from pydantic import BaseModel
from pydantic_ai import Agent, RunContext
from pydantic_ai_skills import SkillsCapability
from pydantic_ai.messages import ModelMessage, ModelResponse, TextPart, ThinkingPart, ToolCallPart
from pydantic_ai.models import ModelRequestParameters, StreamedResponse
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.deepseek import DeepSeekProvider
from pydantic_ai.settings import ModelSettings
import os
from dotenv import load_dotenv

logger = logging.getLogger("agent.timing")

KNOWLEDGE_BASE_DIR = (
    Path(__file__).resolve().parent.parent / "knowledge" / "trusses-ai-english"
)

KNOWLEDGE_BASE_SLOVAK_DIR = (
    Path(__file__).resolve().parent.parent / "knowledge" / "trusses-ai-slovak"
)

SKILLS_DIR = Path(__file__).resolve().parent.parent.parent / ".agents" / "skills"

load_dotenv(dotenv_path="../.env")


class DeepSeekModel(OpenAIModel):
    _step_counter: int = 0

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
                has_content = any(isinstance(p, TextPart) for p in msg.parts)
                has_tool_calls = any(isinstance(p, ToolCallPart) for p in msg.parts)
                if not has_content and not has_tool_calls:
                    msg.parts = [
                        TextPart(content="."),
                        *msg.parts,
                    ]

    async def request(
        self,
        messages: list[ModelMessage],
        model_settings: ModelSettings | None,
        model_request_parameters: ModelRequestParameters,
    ) -> ModelResponse:
        self._step_counter += 1
        step = self._step_counter
        t0 = time.perf_counter()
        logger.info("[model] inference step %d started", step)
        try:
            self._ensure_thinking_parts(messages)
            result = await super().request(messages, model_settings, model_request_parameters)
            elapsed = time.perf_counter() - t0
            tool_calls = [p for p in result.parts if isinstance(p, ToolCallPart)]
            if tool_calls:
                tool_names = [tc.tool_name for tc in tool_calls]
                logger.info(
                    "[model] inference step %d completed in %.2fs -> tool calls: %s",
                    step, elapsed, tool_names,
                )
            else:
                logger.info(
                    "[model] inference step %d completed in %.2fs -> final response",
                    step, elapsed,
                )
            return result
        except Exception:
            elapsed = time.perf_counter() - t0
            logger.info("[model] inference step %d FAILED after %.2fs", step, elapsed)
            raise

    @asynccontextmanager
    async def request_stream(
        self,
        messages: list[ModelMessage],
        model_settings: ModelSettings | None,
        model_request_parameters: ModelRequestParameters,
        run_context: Any | None = None,
    ) -> AsyncIterator[StreamedResponse]:
        self._step_counter += 1
        step = self._step_counter
        t0 = time.perf_counter()
        logger.info("[model] inference step %d started (streamed)", step)
        try:
            self._ensure_thinking_parts(messages)
            async with super().request_stream(
                messages, model_settings, model_request_parameters, run_context
            ) as stream:
                yield stream
            elapsed = time.perf_counter() - t0
            logger.info("[model] inference step %d stream completed in %.2fs", step, elapsed)
        except Exception:
            elapsed = time.perf_counter() - t0
            logger.info("[model] inference step %d FAILED after %.2fs", step, elapsed)
            raise


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
    roofPitch: Optional[float] = None
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
    price: Optional[int] = None
    dxfContent: Optional[str] = None
    ifcContent: Optional[str] = None
    mxfContent: Optional[str] = None


class YourState(BaseModel):
    user_input: str = ""
    ai_response: str = ""
    knowledge_queries: List[KnowledgeQuery] = []
    last_knowledge_result: Optional[str] = None
    # DEMO-ONLY - designs field for design component; simulated for demo purposes
    designs: List[DesignEntry] = []
    locale: str = "sk"


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
_BASE_PROMPT = (
    "You are a truss and roof engineering assistant with access to a knowledge base "
    "of 33 construction projects designed by medop strechy s.r.o.\n\n"
    "ABSOLUTE RULES:\n"
    "- NEVER use emojis or Unicode symbols. Output plain ASCII text only.\n"
    "- NEVER narrate or explain your actions. Call all tools silently, then output only the final result.\n"
    "- FORBIDDEN: 'Let me...', 'I will...', 'Great!', 'Based on...', any commentary about tool calls.\n"
    # ---- KNOWLEDGE BOUNDARY CONSTRAINTS (remove if agent becomes too weak) ----
    "- KNOWLEDGE BOUNDARY: Only answer domain-specific questions (trusses, roofs, construction, "
    "engineering, materials, pricing, project details) using information retrieved from "
    "query_knowledge_base or get_knowledge_summary. If the knowledge base does not contain "
    "relevant information for a domain question, respond that you do not have that information. "
    "NEVER supplement answers with your own training data, general construction knowledge, or "
    "fabricated content. Off-topic or casual conversation (greetings, meta-questions) is exempt.\n"
    # ---- END KNOWLEDGE BOUNDARY CONSTRAINTS ----
    "\n"
    "SKILLS AND PROGRESSIVE DISCLOSURE:\n"
    "- The decision-loop workflow, tool selection rules, parameter extraction patterns, "
    "pricing formula details, and response formatting guidelines are NOT repeated in this prompt; "
    "they live in the skill and its reference files.\n"
    "- Before handling any design-related request, call load_skill('run-generate-design') to "
    "load the slim workflow coordinator.\n"
    "- Once the skill is loaded, call read_skill_resource('run-generate-design', "
    "'references/<resource>.md') to fetch the specific reference file each step requires. "
    "Never guess parameters, pricing, locale mappings, or formatting rules — read the matching "
    "reference file with read_skill_resource first."
)

_LANGUAGE_INSTRUCTIONS: dict[str, str] = {
    "sk": "\n\nIMPORTANT: Respond in Slovak (Slovenčina). All user-facing text must be in Slovak.",
    "en": "\n\nRespond in English.",
}


def get_system_prompt(locale: str = "sk") -> str:
    return _BASE_PROMPT + _LANGUAGE_INSTRUCTIONS.get(locale, _LANGUAGE_INSTRUCTIONS["sk"])


agent = Agent(
    model,
    deps_type=StateDeps,
    capabilities=[
        SkillsCapability(
            directories=[str(SKILLS_DIR)],
            exclude_tools=["run_skill_script", "list_skills"],
            validate=False,
            auto_reload=False,
        )
    ],
    system_prompt=_BASE_PROMPT,
)


@agent.system_prompt
def locale_instruction(ctx: RunContext[StateDeps]) -> str:
    locale = ctx.deps.state.locale if ctx.deps.state.locale else "sk"
    return _LANGUAGE_INSTRUCTIONS.get(locale, _LANGUAGE_INSTRUCTIONS["sk"])


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


def _timed_tool(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        t0 = time.perf_counter()
        try:
            result = await func(*args, **kwargs)
            elapsed = time.perf_counter() - t0
            result_repr = str(result)
            result_len = len(result_repr)
            logger.info("[tool] %s completed in %.4fs (%d chars returned)", func.__name__, elapsed, result_len)
            return result
        except Exception:
            elapsed = time.perf_counter() - t0
            logger.info("[tool] %s FAILED after %.4fs", func.__name__, elapsed)
            raise
    return wrapper


@agent.tool
@_timed_tool
async def generate_quote(
    ctx: RunContext[StateDeps],
    floor_plan_dimensions: str,
    roof_type: str,
    roof_pitch: int = 30,
    building_type: str = "Family house",
) -> str:
    """Generate a deterministic cost estimate for a roof design based on floor plan dimensions and roof type.

    Uses the calibrated Pamir coefficients (C24 timber @ 6200 CZK/m³, ABR90
    angle brackets @ 370 CZK, and updated gusset/assembly/hanger costs).

    Args:
        ctx: Agent context with state
        floor_plan_dimensions: Floor plan dimensions string (e.g. "10x15m")
        roof_type: Roof type — Gable, Hip, Mono-pitch, or Flat
        roof_pitch: Roof pitch in degrees (default 30)
        building_type: Building type (default "Family house")

    Returns:
        A formatted price string "Estimated price: €<EUR> (excl. VAT)".
        Returns an error string if dimensions cannot be parsed.
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
    support_nodes = total_trusses * 2
    bracket_count = round(support_nodes * 1.6)

    gusset_plate_cost = total_joints * 50
    timber_cost = timber_volume * 6200
    assembly_cost = (total_trusses / 20) * 18000
    hanger_cost = total_trusses * 120
    metalwork_cost = bracket_count * 370

    roof_type_factors = {
        "gable": 1.0,
        "hip": 1.3,
        "mono-pitch": 0.9,
        "flat": 0.8,
    }
    factor = roof_type_factors.get(roof_type.strip().lower(), 1.0)

    total_czk = (
        gusset_plate_cost + timber_cost + assembly_cost + hanger_cost + metalwork_cost
    ) * factor
    total_eur = round(total_czk / 25)
    return f"Estimated price: \u20ac{total_eur} (excl. VAT)"


@agent.tool
@_timed_tool
async def query_knowledge_base(ctx: RunContext[StateDeps], query: str) -> str:
    """Query truss and roof engineering knowledge base by reading relevant documents.

    Args:
        ctx: Agent context with state
        query: The user's question or topic to search for

    Returns:
        Relevant document contents with source file references
    """
    summary_path = KNOWLEDGE_BASE_DIR / "summary.md"
    kb_dir = KNOWLEDGE_BASE_DIR
    if ctx.deps.state.locale == "sk":
        kb_dir = KNOWLEDGE_BASE_SLOVAK_DIR
        summary_path = KNOWLEDGE_BASE_SLOVAK_DIR / "summary.md"
    try:
        summary_content = summary_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return "Knowledge base summary not found. Please contact the administrator."

    query_lower = query.lower()
    query_words = query_lower.split()

    subdirs = [
        d
        for d in kb_dir.iterdir()
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
                relative = md_file.relative_to(kb_dir.parent.parent)
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
@_timed_tool
async def get_knowledge_summary(ctx: RunContext[StateDeps]) -> str:
    """Get an overview of what information is available in the knowledge base.

    Args:
        ctx: Agent context with state

    Returns:
        Summary of knowledge base contents organized by subdirectory
    """
    kb_dir = KNOWLEDGE_BASE_DIR
    if ctx.deps.state.locale == "sk":
        kb_dir = KNOWLEDGE_BASE_SLOVAK_DIR
    summary_path = kb_dir / "summary.md"
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
