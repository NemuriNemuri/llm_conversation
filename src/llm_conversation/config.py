import json
from pathlib import Path

import ollama
from pydantic import BaseModel, ConfigDict, Field, field_validator


def get_available_models() -> list[str]:
    return [x.model or "" for x in ollama.list().models if x.model]


class AgentConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., min_length=1, description="Name of the AI agent")
    model: str = Field(..., description="Ollama model to be used")
    system_prompt: str = Field(..., description="Initial system prompt for the agent")
    temperature: float = Field(
        default=0.8,
        ge=0.0,
        le=1.0,
        description="Sampling temperature for the model (0.0-1.0)",
    )
    ctx_size: int = Field(default=2048, ge=0, description="Context size for the model")

    @field_validator("model")
    @classmethod
    def validate_model(cls, value: str) -> str:
        available_models = get_available_models()
        if value not in available_models:
            raise ValueError(f"Model '{value}' is not available")

        return value


class ConversationSettings(BaseModel):
    model_config = ConfigDict(extra="forbid")

    use_markdown: bool = Field(default=False, description="Enable Markdown formatting")
    allow_termination: bool = Field(
        default=False, description="Allow AI agents to terminate the conversation"
    )
    initial_message: str | None = Field(
        default=None, description="Initial message to start the conversation"
    )


class Config(BaseModel):
    model_config = ConfigDict(extra="forbid")

    agent1: AgentConfig = Field(..., description="Configuration for the first AI agent")
    agent2: AgentConfig = Field(
        ..., description="Configuration for the second AI agent"
    )
    settings: ConversationSettings = Field(..., description="Conversation settings")


def load_config(config_path: Path) -> Config:
    """
    Load and validate the configuration file using Pydantic.

    Args:
        config_path (Path): Path to the JSON configuration file

    Returns:
        Config: Validated configuration object

    Raises:
        ValueError: If the configuration is invalid
    """
    try:
        with open(config_path, "r") as f:
            config_dict = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in config file: {e}")

    try:
        return Config.model_validate(config_dict)
    except Exception as e:
        raise ValueError(f"Configuration validation failed: {e}")
