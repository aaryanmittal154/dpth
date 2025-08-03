# ComposioTool Integration Guide

## Overview

The `ComposioTool` is a powerful meta-tool that gives your AI agents access to over 3000+ pre-integrated tools through Composio's platform. Instead of manually implementing individual tool integrations, agents can dynamically discover and use any tool they need.

## Key Features

- **Dynamic Tool Discovery**: Agents can search and list available tools based on their needs
- **Automatic Authentication**: Handles OAuth and API key authentication for all integrated services
- **Unified Interface**: Consistent API across all 3000+ tools
- **Real-time Execution**: Execute actions on external services in real-time
- **Smart Categorization**: Tools are organized by category for easy discovery

## Installation

1. Install the Composio SDK:
```bash
pip install composio-core
```

2. Get your Composio API key:
   - Sign up at [https://app.composio.dev](https://app.composio.dev)
   - Navigate to Settings → API Keys
   - Copy your API key

3. Set your API key as an environment variable:
```bash
export COMPOSIO_API_KEY="your-api-key-here"
```

## Usage Examples

### 1. List All Available Tools

The agent can discover what tools are available:

```python
# Agent prompt: "What tools do you have available?"
# The agent will use:
{
    "action": "list_tools"
}
```

### 2. Search for Specific Tools

Find tools by category or keyword:

```python
# Agent prompt: "Show me email-related tools"
# The agent will use:
{
    "action": "list_tools",
    "query": "email"
}
```

### 3. Get Tool Information

Learn about a specific tool's capabilities:

```python
# Agent prompt: "Tell me what I can do with GitHub"
# The agent will use:
{
    "action": "get_tool_info",
    "tool_name": "github"
}
```

### 4. Execute Tool Actions

Perform real actions using any tool:

```python
# Agent prompt: "Create a GitHub issue in composiohq/composio repository"
# The agent will use:
{
    "action": "execute",
    "tool_name": "github",
    "action_name": "create_issue",
    "parameters": {
        "repo": "composiohq/composio",
        "title": "Feature Request: Add new integration",
        "body": "It would be great to have integration with..."
    }
}
```

## Available Tool Categories

- 🔧 **Development**: GitHub, GitLab, Bitbucket, Jira
- 📧 **Email & Communication**: Gmail, Outlook, SendGrid, Mailchimp
- 💬 **Messaging & Collaboration**: Slack, Discord, Teams, Zoom
- 📋 **Productivity**: Notion, Airtable, Asana, Trello, Monday.com
- 🗂️ **Google Workspace**: Drive, Sheets, Docs, Calendar
- 📱 **Social Media**: Twitter, LinkedIn, Facebook, Instagram
- 💳 **Payments & Finance**: Stripe, PayPal, Square
- ☁️ **Cloud Services**: AWS, Azure, GCP, Heroku
- 🤝 **CRM & Sales**: HubSpot, Salesforce, Pipedrive
- And many more...

## Authentication Flow

When using a tool for the first time, the agent will guide you through authentication:

1. The agent attempts to execute an action
2. If not authenticated, it provides an authentication URL
3. Visit the URL to authorize the tool
4. Return to the agent and retry the action

## Best Practices

1. **Start with Discovery**: Let agents explore available tools before executing actions
2. **Use Search Queries**: Help agents find relevant tools using category keywords
3. **Check Authentication**: Ensure tools are authenticated before complex operations
4. **Handle Errors Gracefully**: The tool provides clear error messages for troubleshooting

## Example Agent Workflows

### Email Automation
```
User: "Send an email to john@example.com about our meeting tomorrow"
Agent:
1. Lists email tools
2. Gets Gmail tool info
3. Executes send_email action with appropriate parameters
```

### Project Management
```
User: "Create a new task in my project management tool"
Agent:
1. Searches for project management tools
2. Identifies available tools (Notion, Asana, Trello)
3. Asks which tool to use
4. Creates the task in the selected tool
```

### GitHub Workflow
```
User: "Check my GitHub notifications and create issues for any bugs"
Agent:
1. Gets GitHub tool info
2. Fetches notifications
3. Analyzes notifications for bug reports
4. Creates issues for identified bugs
```

## Troubleshooting

### "Composio is not properly initialized"
- Ensure `composio-core` is installed
- Verify COMPOSIO_API_KEY is set correctly

### "Tool not found"
- Check the exact tool name using list_tools
- Tool names are lowercase (e.g., "github" not "GitHub")

### "Authentication required"
- Follow the provided authentication URL
- Complete the OAuth flow for the service
- Retry the action after authentication

## Security Considerations

- API keys are stored securely by Composio
- OAuth tokens are managed automatically
- Each tool respects its service's rate limits
- Sensitive data is encrypted in transit

## Support

For additional help:
- Composio Documentation: [https://docs.composio.dev](https://docs.composio.dev)
- GitHub Issues: [https://github.com/composiohq/composio](https://github.com/composiohq/composio)
- Community Discord: Available through Composio's website
