from datetime import datetime
from app.tool.base import BaseTool


_DATETIME_DESCRIPTION = """Get the current date and time. This tool returns the current date and time in ISO format.
Use this tool to get the current date is needed."""


class DateTimeTool(BaseTool):
    name: str = "get_datetime"
    description: str = _DATETIME_DESCRIPTION
    parameters: dict = {
        "type": "object",
        "properties": {},
        "required": [],
    }

    async def execute(self) -> str:
        """Get the current date and time"""
        current_datetime = datetime.now()
        return f"Current date and time: {current_datetime.strftime('%Y-%m-%d %H:%M:%S')} (ISO format: {current_datetime.isoformat()})"
