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


# Define your tools here
# Commented out for genericization - this is a reference implementation
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


# Main agent function - customize this
# Commented out for genericization - this is a reference implementation
# @agent.result_validator
# def validate_result(ctx: RunContext[StateDeps], result: str) -> str:
#     """Validate and process agent results"""
#     # Add your validation logic here
#     return result
