"""
Composio Tool Integration

This tool provides dynamic access to 3000+ tools through Composio's platform.
Agents can discover and use tools on-demand without hardcoding integrations.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional
from app.tool.base import BaseTool, ToolResult
from app.logger import logger
from app.exceptions import ToolError


# Tool description that explains Composio's capabilities
_COMPOSIO_DESCRIPTION = """Access and execute tools from Composio's platform of 3000+ integrations.

This meta-tool allows you to:
1. List all available tools/apps in Composio
2. Search for specific tools by name or category
3. Execute any tool action with proper authentication
4. Prefer using Exa search for web searches

Usage:
- To list available tools: {"action": "list_tools", "query": "optional search term"}
- To get tool details: {"action": "get_tool_info", "tool_name": "github"}
- To execute a tool: {"action": "execute", "tool_name": "github", "action_name": "create_issue", "parameters": {...}}

Examples:
- List all tools: {"action": "list_tools"}
- Search for email tools: {"action": "list_tools", "query": "email"}
- Get GitHub tool info: {"action": "get_tool_info", "tool_name": "github"}
- Create GitHub issue: {"action": "execute", "tool_name": "github", "action_name": "create_issue", "parameters": {"repo": "owner/repo", "title": "Bug", "body": "Description"}}
"""  # noqa: E501

# Path where we persist connection IDs so the user doesn't have to re-authenticate
_CONNECTION_STORE_PATH = Path(os.path.expanduser("~/.composio_connections.json"))

# Connection IDs can be supplied via environment variables so you don't have to
# hard-code them here.  Add the following to your shell or **.env** file:
#   COMPOSIO_GMAIL_CONNECTION_ID=ca_...
#   COMPOSIO_GMAIL_AUTH_CONFIG_ID=ac_...
# The code picks them up automatically at runtime.
_HARDCODED_CONNECTION_IDS: Dict[str, str] = {
    k.replace("COMPOSIO_", "").replace("_CONNECTION_ID", "").lower(): v
    for k, v in os.environ.items()
    if k.endswith("_CONNECTION_ID") and k.startswith("COMPOSIO_")
}
_HARDCODED_AUTH_CONFIG_IDS: Dict[str, str] = {
    k.replace("COMPOSIO_", "").replace("_AUTH_CONFIG_ID", "").lower(): v
    for k, v in os.environ.items()
    if k.endswith("_AUTH_CONFIG_ID") and k.startswith("COMPOSIO_")
}


def _load_saved_connections() -> Dict[str, str]:
    """Load cached Composio connection IDs from disk."""
    if _CONNECTION_STORE_PATH.exists():
        try:
            with _CONNECTION_STORE_PATH.open("r", encoding="utf-8") as fh:
                return json.load(fh)
        except Exception as exc:  # pragma: no cover – defensive fallback
            logger.warning(f"Failed to read {_CONNECTION_STORE_PATH}: {exc}")
    return {}


def _save_connection(app_slug: str, connection_id: str) -> None:
    """Persist a new connection id so future runs can reuse it.

    We simply keep a {app_slug: connection_id} mapping in a JSON file in the
    user's home directory. This avoids prompting the user for OAuth every
    execution.
    """
    try:
        cache = _load_saved_connections()
        if cache.get(app_slug) == connection_id:
            return  # already stored
        cache[app_slug] = connection_id
        _CONNECTION_STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
        with _CONNECTION_STORE_PATH.open("w", encoding="utf-8") as fh:
            json.dump(cache, fh)
        logger.info(
            "🔒 Stored persistent Composio connection for %s at %s",
            app_slug,
            _CONNECTION_STORE_PATH,
        )
    except Exception as exc:  # pragma: no cover – best-effort
        logger.warning(f"Could not persist connection cache: {exc}")


class ComposioTool(BaseTool):
    """
    A meta-tool that provides dynamic access to Composio's tool ecosystem.
    Agents can discover and use any of the 3000+ available tools without prior configuration.
    """

    name: str = "composio_tool"
    description: str = _COMPOSIO_DESCRIPTION
    parameters: dict = {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": ["list_tools", "get_tool_info", "execute"],
                "description": "The action to perform: list available tools, get info about a specific tool, or execute a tool action",
            },
            "query": {
                "type": "string",
                "description": "Optional search query when listing tools (e.g., 'email', 'github', 'calendar')",
            },
            "tool_name": {
                "type": "string",
                "description": "The name of the tool to get info about or execute (e.g., 'github', 'gmail', 'slack')",
            },
            "action_name": {
                "type": "string",
                "description": "The specific action to execute for the tool (e.g., 'create_issue', 'send_email')",
            },
            "parameters": {
                "type": "object",
                "description": "Parameters required for the tool action execution",
            },
        },
        "required": ["action"],
    }

    _toolset: Optional[Any] = None
    _available_tools_cache: Optional[List[Dict]] = None

    def __init__(self):
        super().__init__()
        # Merge cached connections with any hard-coded fallbacks.
        self._saved_connections: Dict[str, str] = {
            **_HARDCODED_CONNECTION_IDS,
            **_load_saved_connections(),
        }
        self._initialize_composio()

    def _initialize_composio(self):
        """Initialize Composio toolset with proper error handling"""
        try:
            # Lazy import to avoid issues if composio is not installed
            from composio import ComposioToolSet

            # Check for API key
            api_key = os.getenv("COMPOSIO_API_KEY")
            if not api_key:
                logger.warning(
                    "COMPOSIO_API_KEY not found in environment. "
                    "Some features may be limited. Get your key at https://app.composio.dev"
                )

            # Initialize toolset
            self._toolset = (
                ComposioToolSet(api_key=api_key) if api_key else ComposioToolSet()
            )
            logger.info("✅ Composio toolset initialized successfully")

        except ImportError:
            logger.error(
                "Composio package not installed. Install with: pip install composio-core"
            )
            self._toolset = None
        except Exception as e:
            logger.error(f"Failed to initialize Composio: {str(e)}")
            self._toolset = None

    async def execute(self, **kwargs) -> ToolResult:
        """Execute the requested Composio action"""
        if not self._toolset:
            return ToolResult(
                error="Composio is not properly initialized. Please install composio-core and set COMPOSIO_API_KEY"
            )

        action = kwargs.get("action")

        try:
            if action == "list_tools":
                return await self._list_tools(kwargs.get("query"))
            elif action == "get_tool_info":
                tool_name = kwargs.get("tool_name")
                if not tool_name:
                    return ToolResult(
                        error="tool_name is required for get_tool_info action"
                    )
                return await self._get_tool_info(tool_name)
            elif action == "execute":
                return await self._execute_tool_action(kwargs)
            else:
                return ToolResult(error=f"Unknown action: {action}")

        except Exception as e:
            logger.exception(f"Error in ComposioTool execution: {str(e)}")
            return ToolResult(error=f"Execution failed: {str(e)}")

    async def _list_tools(self, query: Optional[str] = None) -> ToolResult:
        """List available tools, optionally filtered by query"""
        try:
            # Get all available apps/tools
            from composio import App

            # Get list of all available apps
            all_apps = []
            for app in App.all():
                app_info = {
                    "name": app.slug.lower(),
                    "display_name": app.name,
                    "category": self._categorize_app(app.slug.lower()),
                }

                # Filter by query if provided
                if query:
                    query_lower = query.lower()
                    if (
                        query_lower in app.slug.lower()
                        or query_lower in app.name.lower()
                        or query_lower in app_info["category"].lower()
                    ):
                        all_apps.append(app_info)
                else:
                    all_apps.append(app_info)

            # Sort by name for better readability
            all_apps.sort(key=lambda x: x["name"])

            if not all_apps:
                return ToolResult(output="No tools found matching your query")

            # Format output
            output = f"Found {len(all_apps)} tools"
            if query:
                output += f" matching '{query}'"
            output += ":\n\n"

            # Group by category
            categories = {}
            for app in all_apps:
                cat = app["category"]
                if cat not in categories:
                    categories[cat] = []
                categories[cat].append(app)

            for category, apps in sorted(categories.items()):
                output += f"\n{category}:\n"
                for app in apps:
                    output += f"  - {app['name']} ({app['display_name']})\n"

            output += "\n\nUse get_tool_info to learn more about a specific tool."

            return ToolResult(output=output)

        except Exception as e:
            return ToolResult(error=f"Failed to list tools: {str(e)}")

    async def _get_tool_info(self, tool_name: str) -> ToolResult:
        """Get detailed information about a specific tool"""
        try:
            from composio import App, Action

            # Find the app
            app = None
            for a in App.all():
                if a.slug.lower() == tool_name.lower():
                    app = a
                    break

            if not app:
                return ToolResult(error=f"Tool '{tool_name}' not found")

            # Get available actions for this app
            actions = []
            for action in Action.all():
                if action.slug.startswith(f"{app.slug}_"):
                    action_name = action.slug.replace(f"{app.slug}_", "").lower()
                    actions.append(
                        {
                            "name": action_name,
                            "full_name": action.slug,
                            "description": self._get_action_description(action.slug),
                        }
                    )

            # Format output
            output = f"Tool: {app.name} ({app.slug})\n"
            output += f"Category: {self._categorize_app(app.slug.lower())}\n\n"

            if actions:
                output += f"Available Actions ({len(actions)}):\n"
                for action in actions[:10]:  # Show first 10 actions
                    output += f"  - {action['name']}: {action['description']}\n"

                if len(actions) > 10:
                    output += f"  ... and {len(actions) - 10} more actions\n"
            else:
                output += "No actions found for this tool.\n"

            output += f"\n\nTo execute an action, use: "
            output += (
                '{"action": "execute", "tool_name": "'
                + app.slug.lower()
                + '", "action_name": "<action>", "parameters": {...}}'
            )

            return ToolResult(output=output)

        except Exception as e:
            return ToolResult(error=f"Failed to get tool info: {str(e)}")

    async def _execute_tool_action(self, kwargs: Dict[str, Any]) -> ToolResult:
        """Execute a specific tool action"""
        tool_name = kwargs.get("tool_name")
        action_name = kwargs.get("action_name")
        parameters = kwargs.get("parameters", {})

        if not tool_name or not action_name:
            return ToolResult(
                error="Both tool_name and action_name are required for execute action"
            )

        try:
            from composio import App, Action

            # Find the app
            app = None
            for a in App.all():
                if a.slug.lower() == tool_name.lower():
                    app = a
                    break

            if not app:
                return ToolResult(error=f"Tool '{tool_name}' not found")

            # Find the action
            action_full_name = f"{app.slug}_{action_name.upper()}"
            action = None
            for a in Action.all():
                if a.slug == action_full_name:
                    action = a
                    break

            if not action:
                return ToolResult(
                    error=f"Action '{action_name}' not found for tool '{tool_name}'"
                )

            # Check if user is authenticated for this tool
            entity = self._toolset.get_entity()
            connected_apps = entity.get_connections()
            # Normalize app names to lowercase for reliable comparisons
            connected_app_names = [
                getattr(conn, "appName", "").lower() for conn in connected_apps
            ]

            # Persist any discovered connection ids so we can reuse them later
            for conn in connected_apps:
                try:
                    cid = getattr(
                        conn,
                        "id",
                        getattr(conn, "connectionId", getattr(conn, "uniqueKey", "")),
                    )
                    _save_connection(conn.appName.lower(), cid)
                    self._saved_connections[conn.appName.lower()] = cid
                except Exception:
                    pass  # non-critical

            if app.slug.lower() not in connected_app_names:
                # No live connection – check if we previously saved one
                cached_conn_id = self._saved_connections.get(app.slug.lower())
                if cached_conn_id:
                    # Let Composio know about this cached connection so the execution can proceed silently.
                    try:
                        entity.attach_connection(cached_conn_id)  # type: ignore[attr-defined]
                        connected_apps = entity.get_connections()
                        connected_app_names = [
                            getattr(conn, "appName", "").lower()
                            for conn in connected_apps
                        ]
                        self._saved_connections[app.slug.lower()] = cached_conn_id
                    except Exception as exc:  # pragma: no cover
                        logger.warning(
                            "Failed to attach cached connection %s for %s: %s",
                            cached_conn_id,
                            app.slug,
                            exc,
                        )

                # Re-evaluate after trying to attach
                if app.slug.lower() not in connected_app_names:
                    # Still unauthenticated – ask the user to do the OAuth dance once.
                    auth_url = entity.initiate_connection(app.slug.lower())
                    return ToolResult(
                        output=(
                            f"Authentication required for {app.name}.\n\n"
                            f"Please visit the following URL **once** to authorize access, then rerun the command:\n{auth_url}\n\n"
                            "Future runs will pick up the saved connection automatically."
                        )
                    )

            # Execute the action
            logger.info(f"Executing {action.slug} with parameters: {parameters}")
            result = self._toolset.execute_action(action=action, params=parameters)

            # Detect empty or missing data (often indicates missing permissions)
            if result in (None, "", []) or (isinstance(result, dict) and not result):
                try:
                    # Force (re)authentication to request missing scopes
                    auth_url = entity.initiate_connection(app.slug.lower())  # type: ignore[arg-type]
                    return ToolResult(
                        output=(
                            f"Additional authentication or permissions are required for {app.name}.\n\n"
                            f"Please visit the following URL to authorize access, then rerun the command:\n{auth_url}\n\n"
                            "Future runs will automatically use the upgraded connection."
                        )
                    )
                except Exception:
                    # Fall back to a generic error
                    return ToolResult(
                        error="Action returned no data and could not trigger re-authentication."
                    )

            # Format the result if we actually got something useful
            if isinstance(result, dict):
                if "error" in result:
                    return ToolResult(error=result["error"])
                else:
                    return ToolResult(output=json.dumps(result, indent=2))
            else:
                return ToolResult(output=str(result))

        except Exception as e:
            logger.exception(f"Failed to execute tool action: {str(e)}")
            return ToolResult(error=f"Execution failed: {str(e)}")

    def _categorize_app(self, app_name: str) -> str:
        """Categorize apps for better organization"""
        app_lower = app_name.lower()

        if any(x in app_lower for x in ["github", "gitlab", "bitbucket", "git"]):
            return "🔧 Development"
        elif any(x in app_lower for x in ["gmail", "outlook", "sendgrid", "mailchimp"]):
            return "📧 Email & Communication"
        elif any(x in app_lower for x in ["slack", "discord", "teams", "zoom"]):
            return "💬 Messaging & Collaboration"
        elif any(
            x in app_lower for x in ["notion", "airtable", "monday", "asana", "trello"]
        ):
            return "📋 Productivity & Project Management"
        elif any(
            x in app_lower for x in ["google", "calendar", "sheets", "docs", "drive"]
        ):
            return "🗂️ Google Workspace"
        elif any(
            x in app_lower for x in ["twitter", "linkedin", "facebook", "instagram"]
        ):
            return "📱 Social Media"
        elif any(x in app_lower for x in ["stripe", "paypal", "square"]):
            return "💳 Payments & Finance"
        elif any(x in app_lower for x in ["aws", "azure", "gcp", "heroku"]):
            return "☁️ Cloud Services"
        elif any(x in app_lower for x in ["jira", "confluence", "atlassian"]):
            return "🏢 Atlassian Suite"
        elif any(x in app_lower for x in ["hubspot", "salesforce", "pipedrive"]):
            return "🤝 CRM & Sales"
        else:
            return "🔌 Other Integrations"

    def _get_action_description(self, action_name: str) -> str:
        """Get a human-readable description for an action"""
        # Convert action name to readable format
        # e.g., GITHUB_CREATE_ISSUE -> create issue
        parts = action_name.split("_")[1:]  # Remove tool prefix
        description = " ".join(parts).lower()
        return description


# Example usage documentation
"""
Example Usage:

1. List all available tools:
   result = await composio_tool.execute(action="list_tools")

2. Search for specific tools:
   result = await composio_tool.execute(action="list_tools", query="email")

3. Get information about a tool:
   result = await composio_tool.execute(action="get_tool_info", tool_name="github")

4. Execute a tool action:
   result = await composio_tool.execute(
       action="execute",
       tool_name="github",
       action_name="create_issue",
       parameters={
           "repo": "owner/repo",
           "title": "New Feature Request",
           "body": "Please add this feature..."
       }
   )
"""
