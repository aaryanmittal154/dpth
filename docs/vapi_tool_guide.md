# Vapi Tool Integration Guide

## Overview

The VapiTool enables your AI agents to make phone calls and have voice conversations with people using the Vapi AI platform. This powerful integration allows agents to:

- Make outbound phone calls to any phone number
- Create and manage voice assistants with custom prompts
- Configure different voices and language models
- Get call recordings and transcripts
- Handle complex conversational flows

## Prerequisites

Before using the VapiTool, you need to:

1. **Create a Vapi Account**: Sign up at [https://vapi.ai](https://vapi.ai)
2. **Get API Key**: Navigate to your Vapi dashboard and copy your API key
3. **Set Environment Variables**:
   ```bash
   export VAPI_API_KEY="your-api-key-here"
   export VAPI_PHONE_NUMBER_ID="your-phone-number-id"  # Optional
   ```

4. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

### Setting up Phone Numbers

You have two options for phone numbers:

1. **Use Vapi Dashboard**: Purchase a phone number through the Vapi dashboard
2. **Environment Variable**: Set `VAPI_PHONE_NUMBER_ID` with an existing phone number ID
3. **Use Assistant ID**: Create assistants with phone numbers already configured

## Usage Examples

### 1. Simple Phone Call

Make a basic phone call with a simple message:

```python
# Agent can use the tool like this:
result = await vapi_tool.execute(
    action="create_call",
    phone_number="+1234567890",
    message="Hi John, I'm calling to remind you about your appointment tomorrow at 3 PM."
)
```

### 2. Custom Assistant Configuration

Create a call with advanced assistant settings:

```python
result = await vapi_tool.execute(
    action="create_call",
    phone_number="+1234567890",
    assistant_config={
        "name": "Sales Assistant",
        "firstMessage": "Hello! I'm calling from TechCorp about our new product launch.",
        "systemPrompt": "You are a friendly sales representative. Keep responses concise and professional.",
        "model": "gpt-4",
        "voice": "andrew",  # Available voices: andrew, brian, emma, olivia (Azure voices)
        "temperature": 0.7,
        "maxDurationSeconds": 300,  # 5 minute max call
        "endCallPhrases": ["goodbye", "bye", "talk to you later"]
    }
)
```

### 3. Create Reusable Assistant

Create an assistant that can be reused for multiple calls:

```python
# Create the assistant
result = await vapi_tool.execute(
    action="create_assistant",
    assistant_config={
        "name": "Customer Support Bot",
        "firstMessage": "Hello! Thank you for calling support. How can I help you today?",
        "systemPrompt": "You are a helpful customer support agent...",
        "model": "gpt-3.5-turbo",
        "voice": "emma"
    }
)

# Use the assistant ID for calls
assistant_id = result.metadata["assistant_id"]
result = await vapi_tool.execute(
    action="create_call",
    phone_number="+1234567890",
    assistant_id=assistant_id
)
```

### 4. Get Call Information

Retrieve details about a call including recordings and transcripts:

```python
result = await vapi_tool.execute(
    action="get_call",
    call_id="call_xxxxx"
)
# Returns: status, cost, recording URL, transcript, etc.
```

### 5. List Recent Calls

Get a list of recent calls:

```python
result = await vapi_tool.execute(
    action="list_calls",
    limit=10
)
```

## Available Actions

### create_call
Makes an outbound phone call.

**Parameters:**
- `phone_number` (required): The phone number to call (format: +1234567890)
- `message` (optional): Simple message for the assistant to speak
- `assistant_config` (optional): Advanced configuration object
- `assistant_id` (optional): ID of existing assistant to use
- `metadata` (optional): Custom metadata to attach to the call

### get_call
Retrieves information about a specific call.

**Parameters:**
- `call_id` (required): The ID of the call

### list_calls
Lists recent calls.

**Parameters:**
- `limit` (optional): Number of calls to return (default: 10)

### create_assistant
Creates a reusable assistant configuration.

**Parameters:**
- `assistant_config` (required): Configuration object with:
  - `name`: Assistant name
  - `firstMessage`: Opening message
  - `systemPrompt`: System instructions
  - `model`: LLM model (gpt-4, gpt-3.5-turbo, etc.)
  - `voice`: Voice ID (andrew, brian, emma, olivia for Azure voices)
  - `temperature`: LLM temperature (0-2)
  - `maxDurationSeconds`: Max call duration
  - `endCallPhrases`: Phrases that end the call

## Voice Options

### Azure Voices (Default - Built-in)
- `jennifer` - Female, professional
- `michael` - Male, friendly
- `emma` - Female, conversational
- `mark` - Male, authoritative
- `sarah` - Female, warm

### Deepgram Voices
- `luna` - Female
- `zeus` - Male
- `hera` - Female
- `orion` - Male

### Other Voice Providers

**11Labs** - Premium voices (requires API key in Vapi dashboard)
**PlayHT** - High-quality voices
**Deepgram** - Various voices
**RimeAI** - Demographically specific voices
- `melissa` - Female
- `will` - Male
- `ruby` - Female
- `davis` - Male

## Best Practices

1. **Keep First Messages Short**: The opening message should be concise and clear
2. **Use Appropriate Voices**: Match the voice to your use case (professional vs casual)
3. **Set Time Limits**: Always set `maxDurationSeconds` to control costs
4. **Handle Errors**: Check for errors in the ToolResult and handle appropriately
5. **Test First**: Test with your own number before calling customers
6. **Respect Privacy**: Ensure you have consent before making calls
7. **Monitor Costs**: Each call incurs costs based on duration and usage

## Integration with Agents

When using the VapiTool in your agent workflows:

```python
# In your agent prompt
"""
You can make phone calls using the vapi_call tool.

To make a simple call:
Use the tool with action="create_call", provide the phone_number and message.

To check on a call:
Use action="get_call" with the call_id.

Example scenarios:
- "Call John at +1234567890 and remind him about the meeting"
- "Check the status of call_xxxxx"
- "List the last 5 calls we made"
"""
```

## Troubleshooting

### Common Issues

1. **No API Key**: Ensure `VAPI_API_KEY` is set in your environment
2. **No Phone Number**: Either set `VAPI_PHONE_NUMBER_ID` or use an `assistant_id`
3. **Invalid Phone Format**: Use E.164 format: +[country code][number]
4. **Call Fails**: Check your Vapi account has credits and phone number is valid
5. **Import Error**: Run `pip install vapi-server-sdk`

### Error Messages

- `"Vapi not configured"`: Set your API key
- `"No phone number configured"`: Add a phone number ID or use assistant_id
- `"Failed to create call"`: Check API key, credits, and phone number format

## Advanced Features

### Webhooks and Real-time Events

For real-time call events, configure webhooks in your Vapi dashboard to receive:
- Call status updates
- Real-time transcripts
- Function calls from the assistant
- Call completion events

### Custom Functions

You can add custom functions to your assistants through the Vapi dashboard that can:
- Look up customer information
- Check availability
- Process orders
- Transfer calls

## Cost Considerations

- Calls are billed per minute
- Different voices and models have different costs
- International calls may have higher rates
- Set `maxDurationSeconds` to control maximum cost per call

## Security Notes

1. Never expose your API key in client-side code
2. Validate phone numbers before making calls
3. Implement rate limiting for bulk operations
4. Store call recordings securely
5. Comply with local regulations for automated calling

## Support

- Vapi Documentation: https://docs.vapi.ai
- Vapi Dashboard: https://dashboard.vapi.ai
- Vapi Discord: https://discord.gg/vapi

## Example Agent Workflow

Here's a complete example of an agent using the VapiTool:

```python
# Agent receives: "Call our customer John at +1234567890 about his order"

# Agent uses VapiTool:
result = await vapi_tool.execute(
    action="create_call",
    phone_number="+1234567890",
    assistant_config={
        "firstMessage": "Hi John, I'm calling from YourCompany about your recent order.",
        "systemPrompt": """You are calling John about his order. Be friendly and helpful.
        Ask if he has any questions about his order and if everything arrived correctly.
        Keep the call brief unless he has specific questions.""",
        "model": "gpt-3.5-turbo",
        "voice": "michael",
        "maxDurationSeconds": 180,  # 3 minute max
        "endCallPhrases": ["goodbye", "bye", "have a nice day"]
    },
    metadata={
        "customer": "John",
        "purpose": "order_followup"
    }
)

# Agent reports back:
"I've successfully initiated a call to John at +1234567890. The call ID is {call_id}.
I'll be asking about his recent order and if everything arrived correctly.
The call will last a maximum of 3 minutes."
```
