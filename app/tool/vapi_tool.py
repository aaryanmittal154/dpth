"""
Vapi Tool for Voice Calling

This tool enables agents to make phone calls and have voice conversations
using the Vapi AI platform. It supports both outbound calling and managing
ongoing conversations.
"""

import os
import json
import asyncio
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
from app.tool.base import BaseTool, ToolResult
from app.logger import logger
from app.exceptions import ToolError


_VAPI_DESCRIPTION = """Make phone calls and have voice conversations using Vapi AI.

This tool allows you to:
1. Create outbound phone calls to any phone number
2. Set up voice assistants with custom prompts and voices
3. Get call status and recordings
4. Manage ongoing calls

Usage:
- To make a call: {"action": "create_call", "phone_number": "+1234567890", "assistant_config": {...}}
- To get call status: {"action": "get_call", "call_id": "call_xxx"}
- To end a call: {"action": "end_call", "call_id": "call_xxx"}
- To list recent calls: {"action": "list_calls", "limit": 10}

Examples:
- Simple call: {"action": "create_call", "phone_number": "+1234567890", "message": "Hi, I'm calling about your appointment tomorrow."}
- Custom assistant: {"action": "create_call", "phone_number": "+1234567890", "assistant_config": {"firstMessage": "Hello!", "voice": "jennifer", "model": "gpt-4"}}
"""


class VapiTool(BaseTool):
    """
    A tool that enables voice calling capabilities through Vapi AI platform.
    Agents can use this to make phone calls and have conversations with people.
    """

    name: str = "vapi_call"
    description: str = _VAPI_DESCRIPTION
    parameters: dict = {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": [
                    "create_call",
                    "get_call",
                    "end_call",
                    "list_calls",
                    "create_assistant",
                ],
                "description": "The action to perform: create a call, get call info, end a call, list calls, or create an assistant",
            },
            "phone_number": {
                "type": "string",
                "description": "The phone number to call (required for create_call). Format: +1234567890",
            },
            "call_id": {
                "type": "string",
                "description": "The ID of an existing call (required for get_call and end_call)",
            },
            "message": {
                "type": "string",
                "description": "Simple message for the assistant to speak (alternative to assistant_config)",
            },
            "assistant_config": {
                "type": "object",
                "description": "Advanced assistant configuration",
                "properties": {
                    "name": {"type": "string", "description": "Assistant name"},
                    "firstMessage": {
                        "type": "string",
                        "description": "First message the assistant speaks",
                    },
                    "systemPrompt": {
                        "type": "string",
                        "description": "System prompt for the assistant",
                    },
                    "model": {
                        "type": "string",
                        "description": "LLM model to use (e.g., 'gpt-4', 'gpt-3.5-turbo')",
                    },
                    "voice": {
                        "type": "string",
                        "description": "Voice to use (e.g., 'andrew', 'brian', 'emma', 'olivia') - Azure voices",
                    },
                    "temperature": {
                        "type": "number",
                        "description": "LLM temperature (0-2)",
                    },
                    "maxDurationSeconds": {
                        "type": "integer",
                        "description": "Maximum call duration in seconds",
                    },
                    "endCallPhrases": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Phrases that end the call",
                    },
                },
            },
            "assistant_id": {
                "type": "string",
                "description": "ID of an existing assistant to use for the call",
            },
            "metadata": {
                "type": "object",
                "description": "Custom metadata to attach to the call",
            },
            "limit": {
                "type": "integer",
                "description": "Number of calls to return (for list_calls)",
                "default": 10,
            },
        },
        "required": ["action"],
    }

    _client: Optional[Any] = None
    _phone_number_id: Optional[str] = None

    def __init__(self):
        super().__init__()
        self._initialize_vapi()

    def _initialize_vapi(self):
        """Initialize Vapi client with API key"""
        try:
            # Check for Vapi API key in environment
            api_key = os.getenv("VAPI_API_KEY")
            if not api_key:
                logger.warning(
                    "VAPI_API_KEY not found in environment. Vapi tool will not be functional."
                )
                return

            # Import Vapi SDK
            try:
                from vapi import Vapi

                self._client = Vapi(token=api_key)
                logger.info("Vapi client initialized successfully")

                # Try to get or create a phone number
                self._setup_phone_number()

            except ImportError:
                logger.error(
                    "vapi-server-sdk not installed. Run: pip install vapi-server-sdk"
                )

        except Exception as e:
            logger.error(f"Failed to initialize Vapi: {str(e)}")

    def _setup_phone_number(self):
        """Setup phone number for outbound calls"""
        try:
            if not self._client:
                return

            # Check for existing phone number ID in environment
            phone_number_id = os.getenv("VAPI_PHONE_NUMBER_ID")
            if phone_number_id:
                self._phone_number_id = phone_number_id
                return

            # Otherwise, try to get the first available phone number
            try:
                phone_numbers = self._client.phone_numbers.list()
                if phone_numbers and len(phone_numbers) > 0:
                    # Get the actual ID (UUID) of the phone number, not the number itself
                    self._phone_number_id = phone_numbers[0].id
                    logger.info(
                        f"Using phone number ID: {self._phone_number_id} (Number: {phone_numbers[0].number})"
                    )
                else:
                    logger.warning(
                        "No phone numbers found. You'll need to add one in Vapi dashboard or provide assistant_id."
                    )
            except Exception as e:
                logger.warning(f"Could not list phone numbers: {str(e)}")

        except Exception as e:
            logger.error(f"Failed to setup phone number: {str(e)}")

    async def execute(self, **kwargs) -> ToolResult:
        """Execute the Vapi tool action"""
        if not self._client:
            return ToolResult(
                error="Vapi not configured. Please set VAPI_API_KEY environment variable."
            )

        action = kwargs.get("action")

        try:
            if action == "create_call":
                return await self._create_call(kwargs)
            elif action == "get_call":
                return await self._get_call(kwargs)
            elif action == "end_call":
                return await self._end_call(kwargs)
            elif action == "list_calls":
                return await self._list_calls(kwargs)
            elif action == "create_assistant":
                return await self._create_assistant(kwargs)
            else:
                return ToolResult(error=f"Unknown action: {action}")

        except Exception as e:
            logger.error(f"Vapi tool error: {str(e)}")
            return ToolResult(error=f"Failed to execute Vapi action: {str(e)}")

    async def _create_call(self, kwargs: Dict[str, Any]) -> ToolResult:
        """Create an outbound phone call"""
        phone_number = kwargs.get("phone_number")
        if not phone_number:
            return ToolResult(error="phone_number is required for create_call")

        # Ensure phone number is in E.164 format
        if not phone_number.startswith("+"):
            # Assume US number if no country code
            phone_number = f"+1{phone_number}"

        try:
            # Build the call configuration
            call_config = {
                "customer": {
                    "number": phone_number,
                }
            }

            # Add metadata if provided
            if kwargs.get("metadata"):
                call_config["metadata"] = kwargs["metadata"]

            # Configure assistant
            if kwargs.get("assistant_id"):
                # Use existing assistant
                call_config["assistant_id"] = kwargs["assistant_id"]
            else:
                # Create inline assistant configuration
                assistant_config = kwargs.get("assistant_config", {})

                # Simple message mode
                if kwargs.get("message") and not assistant_config:
                    assistant_config = {
                        "firstMessage": kwargs["message"],
                        "model": {
                            "provider": "openai",
                            "model": "gpt-3.5-turbo",
                            "messages": [
                                {
                                    "role": "system",
                                    "content": "You are a helpful assistant making a phone call. Be concise and friendly.",
                                }
                            ],
                        },
                        "voice": {"provider": "azure", "voiceId": "andrew"},
                    }
                else:
                    # Advanced configuration mode
                    assistant = {
                        "firstMessage": assistant_config.get(
                            "firstMessage", "Hello, how can I help you today?"
                        ),
                        "model": {
                            "provider": "openai",
                            "model": assistant_config.get("model", "gpt-3.5-turbo"),
                            "messages": [
                                {
                                    "role": "system",
                                    "content": assistant_config.get(
                                        "systemPrompt", "You are a helpful assistant."
                                    ),
                                }
                            ],
                        },
                        "voice": {
                            "provider": "azure",
                            "voiceId": assistant_config.get("voice", "andrew"),
                        },
                    }

                    if "temperature" in assistant_config:
                        assistant["model"]["temperature"] = assistant_config[
                            "temperature"
                        ]
                    if "maxDurationSeconds" in assistant_config:
                        assistant["maxDurationSeconds"] = assistant_config[
                            "maxDurationSeconds"
                        ]
                    if "endCallPhrases" in assistant_config:
                        assistant["endCallPhrases"] = assistant_config["endCallPhrases"]

                    assistant_config = assistant

                call_config["assistant"] = assistant_config

            # Add phone number ID if available
            if self._phone_number_id:
                call_config["phone_number_id"] = self._phone_number_id
            elif not kwargs.get("assistant_id"):
                return ToolResult(
                    error="No phone number configured. Please set VAPI_PHONE_NUMBER_ID or use an assistant_id"
                )

            # Create the call
            logger.info(f"Creating call with config: {call_config}")

            # Try different parameter approaches for the SDK
            try:
                call = self._client.calls.create(**call_config)
            except Exception as e:
                logger.warning(
                    f"First attempt failed with {str(e)}, trying alternative approach"
                )
                # Try with different parameter naming
                if "phone_number_id" in call_config:
                    call_config["phoneNumberId"] = call_config.pop("phone_number_id")
                if "assistant_id" in call_config:
                    call_config["assistantId"] = call_config.pop("assistant_id")
                call = self._client.calls.create(**call_config)

            output = (
                f"Successfully created call!\n"
                f"Call ID: {call.id}\n"
                f"Status: {call.status}\n"
                f"To: {phone_number}\n"
            )

            if hasattr(call, "createdAt"):
                output += f"Created: {call.createdAt}\n"

            return ToolResult(
                output=output,
                metadata={
                    "call_id": call.id,
                    "status": call.status,
                    "phone_number": phone_number,
                },
            )

        except Exception as e:
            return ToolResult(error=f"Failed to create call: {str(e)}")

    async def _get_call(self, kwargs: Dict[str, Any]) -> ToolResult:
        """Get information about a specific call"""
        call_id = kwargs.get("call_id")
        if not call_id:
            return ToolResult(error="call_id is required for get_call")

        try:
            call = self._client.calls.get(call_id)

            output = (
                f"Call Information:\n"
                f"ID: {call.id}\n"
                f"Status: {call.status}\n"
                f"Type: {call.type}\n"
            )

            if hasattr(call, "startedAt"):
                output += f"Started: {call.startedAt}\n"
            if hasattr(call, "endedAt"):
                output += f"Ended: {call.endedAt}\n"
            if hasattr(call, "cost"):
                output += f"Cost: ${call.cost:.2f}\n"
            if hasattr(call, "endedReason"):
                output += f"End Reason: {call.endedReason}\n"

            # Add recording URL if available
            if hasattr(call, "artifact") and hasattr(call.artifact, "recordingUrl"):
                output += f"Recording: {call.artifact.recordingUrl}\n"

            # Add transcript if available
            if hasattr(call, "artifact") and hasattr(call.artifact, "transcript"):
                output += f"\nTranscript:\n{call.artifact.transcript}\n"

            return ToolResult(output=output)

        except Exception as e:
            return ToolResult(error=f"Failed to get call: {str(e)}")

    async def _end_call(self, kwargs: Dict[str, Any]) -> ToolResult:
        """End an ongoing call"""
        call_id = kwargs.get("call_id")
        if not call_id:
            return ToolResult(error="call_id is required for end_call")

        try:
            # Note: Vapi SDK might not have a direct end call method
            # This would typically be done through the webhook or real-time API
            # For now, we'll return information about how to end calls

            return ToolResult(
                output=(
                    f"To end call {call_id}, you can:\n"
                    f"1. Use end call phrases configured in the assistant\n"
                    f"2. Use the real-time API to send an end call command\n"
                    f"3. Let the call timeout based on maxDurationSeconds\n"
                    f"4. The called party can hang up\n"
                ),
                error="Direct call ending not available through this SDK. See output for alternatives.",
            )

        except Exception as e:
            return ToolResult(error=f"Failed to end call: {str(e)}")

    async def _list_calls(self, kwargs: Dict[str, Any]) -> ToolResult:
        """List recent calls"""
        try:
            limit = kwargs.get("limit", 10)
            calls = self._client.calls.list(limit=limit)

            if not calls:
                return ToolResult(output="No calls found.")

            output = f"Recent Calls (showing {len(calls)} of {limit} requested):\n\n"

            for i, call in enumerate(calls, 1):
                output += f"{i}. Call {call.id}\n"
                output += f"   Status: {call.status}\n"
                output += f"   Type: {call.type}\n"

                if hasattr(call, "createdAt"):
                    output += f"   Created: {call.createdAt}\n"
                if hasattr(call, "cost"):
                    output += f"   Cost: ${call.cost:.2f}\n"
                if hasattr(call, "endedReason"):
                    output += f"   End Reason: {call.endedReason}\n"

                output += "\n"

            return ToolResult(output=output)

        except Exception as e:
            return ToolResult(error=f"Failed to list calls: {str(e)}")

    async def _create_assistant(self, kwargs: Dict[str, Any]) -> ToolResult:
        """Create a reusable assistant configuration"""
        assistant_config = kwargs.get("assistant_config", {})

        try:
            assistant_data = {
                "name": assistant_config.get("name", "Voice Assistant"),
                "firstMessage": assistant_config.get(
                    "firstMessage", "Hello, how can I help you?"
                ),
                "model": {
                    "provider": "openai",
                    "model": assistant_config.get("model", "gpt-3.5-turbo"),
                    "messages": [
                        {
                            "role": "system",
                            "content": assistant_config.get(
                                "systemPrompt", "You are a helpful assistant."
                            ),
                        }
                    ],
                },
                "voice": {
                    "provider": "azure",
                    "voiceId": assistant_config.get("voice", "andrew"),
                },
            }

            # Add optional fields
            if "temperature" in assistant_config:
                assistant_data["model"]["temperature"] = assistant_config["temperature"]
            if "maxDurationSeconds" in assistant_config:
                assistant_data["maxDurationSeconds"] = assistant_config[
                    "maxDurationSeconds"
                ]
            if "endCallPhrases" in assistant_config:
                assistant_data["endCallPhrases"] = assistant_config["endCallPhrases"]

            # Create assistant using direct API structure
            try:
                assistant = self._client.assistants.create(
                    name=assistant_data.get("name"),
                    first_message=assistant_data.get("firstMessage"),
                    model=assistant_data.get("model"),
                    voice=assistant_data.get("voice"),
                    max_duration_seconds=assistant_data.get("maxDurationSeconds"),
                    end_call_phrases=assistant_data.get("endCallPhrases"),
                )
            except Exception as e:
                # Fallback to alternative parameter names if needed
                logger.warning(
                    f"First attempt failed: {str(e)}, trying alternative format"
                )
                assistant_request = {
                    "name": assistant_data.get("name"),
                    "firstMessage": assistant_data.get("firstMessage"),
                    "model": assistant_data.get("model"),
                    "voice": assistant_data.get("voice"),
                }
                if "maxDurationSeconds" in assistant_data:
                    assistant_request["maxDurationSeconds"] = assistant_data[
                        "maxDurationSeconds"
                    ]
                if "endCallPhrases" in assistant_data:
                    assistant_request["endCallPhrases"] = assistant_data[
                        "endCallPhrases"
                    ]

                assistant = self._client.assistants.create(assistant_request)

            output = (
                f"Successfully created assistant!\n"
                f"Assistant ID: {assistant.id}\n"
                f"Name: {assistant.name}\n"
                f"Model: {assistant_data['model']['model']}\n"
                f"Voice: {assistant_data['voice']['voiceId']}\n"
                f"\nUse this assistant_id when creating calls."
            )

            return ToolResult(
                output=output,
                metadata={"assistant_id": assistant.id, "name": assistant.name},
            )

        except Exception as e:
            return ToolResult(error=f"Failed to create assistant: {str(e)}")
