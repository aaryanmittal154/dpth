from datetime import datetime
from typing import Dict, List, Optional

from pydantic import Field, model_validator

from app.agent.toolcall import ToolCallAgent
from app.config import config
from app.logger import logger
from app.prompt.deptheon import NEXT_STEP_PROMPT, SYSTEM_PROMPT
from app.tool import (
    Terminate,
    ToolCollection,
    DateTimeTool,
    ComposioTool,
    VapiTool,
)
from app.tool.python_execute import PythonExecute


class Deptheon(ToolCallAgent):
    """A versatile general-purpose agent with support for various tools."""

    name: str = "Deptheon"
    description: str = (
        "A versatile agent that can solve various tasks using multiple tools"
    )

    system_prompt: str = SYSTEM_PROMPT.format(
        directory=config.workspace_root,
        datetime=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    )
    next_step_prompt: str = NEXT_STEP_PROMPT

    max_observe: int = 10000
    max_steps: int = 50

    # Add general-purpose tools to the tool collection
    available_tools: ToolCollection = Field(
        default_factory=lambda: ToolCollection(
            PythonExecute(),
            DateTimeTool(),
            ComposioTool(),
            VapiTool(),
            Terminate(),
        )
    )

    special_tool_names: list[str] = Field(default_factory=lambda: [Terminate().name])

    _initialized: bool = False

    @classmethod
    async def create(cls) -> "Deptheon":
        """Create and initialize a Deptheon instance."""
        instance = cls()
        return instance

    async def cleanup(self) -> None:
        """Clean up agent resources."""
        await super().cleanup()

    def handle_special_tools(self, tool_name: str, tool_params: dict) -> bool:
        """Handle special tools. Return True if handled."""
        if tool_name == "terminate":
            logger.info("Terminating due to tool call.")
            return True
        return False
