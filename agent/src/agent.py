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

from datetime import datetime, timezone
from pathlib import Path

from pydantic import BaseModel
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIModel
import os
from dotenv import load_dotenv
from typing import List, Optional

KNOWLEDGE_BASE_DIR = (
    Path(__file__).resolve().parent.parent / "knowledge" / "trusses-ai-english"
)

load_dotenv(dotenv_path="../.env")

# Model configuration
model = OpenAIModel(
    model=os.getenv("OPENAI_MODEL", "gpt-4"),
    base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
)


class KnowledgeQuery(BaseModel):
    query: str
    result: str
    timestamp: str


class YourState(BaseModel):
    user_input: str = ""
    ai_response: str = ""
    knowledge_queries: List[KnowledgeQuery] = []
    last_knowledge_result: Optional[str] = None


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
        "You are a truss and roof engineering assistant with access to a knowledge base "
        "of 33 construction projects designed by medop strechy s.r.o. "
        "You have two tools available:\n"
        "- get_knowledge_summary: Use this when the user asks general questions about what "
        'information is available (e.g., "What projects do you have?", "What do you know?").\n'
        "- query_knowledge_base: Use this when the user asks specific questions about projects, "
        "load calculations, materials, truss designs, or engineering specifications.\n\n"
        "Always use get_knowledge_summary first for overview questions, and query_knowledge_base "
        "for specific technical queries. When providing answers, always cite the source document path."
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
