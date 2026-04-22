# ============================================================================
# REFERENCE IMPLEMENTATION - COMMENTED OUT FOR GENERICIZATION
# ============================================================================
# This file contains a reference PydanticAI agent implementation that has been
# commented out to create a generic template. The original implementation
# provides a complete example of how to structure an agent with state, tools,
# and result validation.
#
# To adapt for your project:
# 1. Define your state class with domain-specific fields
# 2. Create dependencies that match your state requirements
# 3. Configure the agent with appropriate system prompt and model
# 4. Implement tools that handle your specific business logic
# 5. Add result validation if needed
# 6. Uncomment and adapt the code below
# ============================================================================

from pydantic import BaseModel
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIModel
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path="../.env")

# Model configuration
model = OpenAIModel(
    model=os.getenv("OPENAI_MODEL", "gpt-4"),
    base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
)


# ============================================================================
# STATE CLASS - COMMENTED OUT FOR GENERICIZATION
# ============================================================================
# YourState defines the shared state that persists across agent tool calls.
# It tracks conversation context (user_input, ai_response) and any
# domain-specific fields needed by your tools.
#
# Current Logic:
# - user_input: Stores the latest user message for tool context
# - ai_response: Stores the latest agent response for tool context
# - Additional fields can be added for domain-specific data tracking
#
# To adapt for your project:
# 1. Define fields that represent your domain's state (e.g., order_id, customer_data)
# 2. Use Optional types for fields that may not always be populated
# 3. Provide default values so the state can be initialized without all fields
# 4. Keep state serializable (BaseModel ensures JSON compatibility)
# ============================================================================
# class YourState(BaseModel):
#     """State for your specific application"""
#
#     user_input: str = ""
#     ai_response: str = ""
#     # Add your domain-specific state fields here


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
# class StateDeps:
#     """Dependencies for your agent"""
#
#     def __init__(self, state: YourState):
#         self.state = state


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
# agent = Agent(
#     model, deps_type=StateDeps, system_prompt="You are a helpful AI assistant."
# )


# ============================================================================
# TOOL IMPLEMENTATION - COMMENTED OUT FOR GENERICIZATION
# ============================================================================
# Tool functions define the actions your agent can take. Each tool is decorated
# with @agent.tool and receives a RunContext containing the agent's dependencies.
# Tools can read and modify state, call external APIs, process data, etc.
#
# Current Logic:
# - your_tool: A sample tool that takes input_data and returns a formatted string
# - Demonstrates the tool signature pattern: async def tool(ctx, args) -> str
# - Shows how to access state through ctx.deps.state
# - Includes docstring for agent self-discovery of available tools
#
# To adapt for your project:
# 1. Define tools that implement your specific business logic
# 2. Each tool must be an async function decorated with @agent.tool
# 3. First parameter is always RunContext[StateDeps] for dependency access
# 4. Additional parameters become the tool's input schema
# 5. Return type should be a string or a Pydantic model for structured output
# 6. Write clear docstrings - the agent uses them to decide when to call tools
# 7. Uncomment and adapt the code below
# ============================================================================
# @agent.tool
# async def your_tool(ctx: RunContext[StateDeps], input_data: str) -> str:
#     """
#     Your tool description
#
#     Args:
#         ctx: Agent context with state
#         input_data: Input data for your tool
#
#     Returns:
#         Your tool output
#     """
#     # Implement your tool logic here
#     return f"Tool output: {input_data}"


# ============================================================================
# RESULT VALIDATION - COMMENTED OUT FOR GENERICIZATION
# ============================================================================
# The result validator is an optional hook that runs after the agent generates
# a response. It allows you to inspect, validate, or transform the agent's
# output before it is returned to the caller.
#
# Current Logic:
# - Receives the agent's RunContext and the raw result string
# - Can enforce output format requirements or content policies
# - Can transform or enrich the result before returning
#
# To adapt for your project:
# 1. Define validation rules for your domain (e.g., required fields, format checks)
# 2. Raise an exception to trigger a retry if validation fails
# 3. Transform the result as needed (e.g., extract structured data)
# 4. Uncomment and adapt the code below
# ============================================================================
# @agent.result_validator
# def validate_result(ctx: RunContext[StateDeps], result: str) -> str:
#     """Validate and process agent results"""
#     # Add your validation logic here
#     return result
