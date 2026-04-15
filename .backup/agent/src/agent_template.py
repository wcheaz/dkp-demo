# Minimal PydanticAI Agent Template
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


# Your state class - customize this for your domain
class YourState(BaseModel):
    """State for your specific application"""

    user_input: str = ""
    ai_response: str = ""
    # Add your domain-specific state fields here


# Dependencies
class StateDeps:
    """Dependencies for your agent"""

    def __init__(self, state: YourState):
        self.state = state


# Create agent
agent = Agent(
    model, deps_type=StateDeps, system_prompt="You are a helpful AI assistant."
)


# Define your tools here
@agent.tool
async def your_tool(ctx: RunContext[StateDeps], input_data: str) -> str:
    """
    Your tool description

    Args:
        ctx: Agent context with state
        input_data: Input data for your tool

    Returns:
        Your tool output
    """
    # Implement your tool logic here
    return f"Tool output: {input_data}"


# Main agent function - customize this
@agent.result_validator
def validate_result(ctx: RunContext[StateDeps], result: str) -> str:
    """Validate and process agent results"""
    # Add your validation logic here
    return result
