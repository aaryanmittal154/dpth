# 🏆 Deptheon - Winner of Agents in the Loop Hackathon 2025


**The World's Most Capable Autonomous AI Agent**

*Deptheon can autonomously orchestrate complex, multi-hour workflows involving web research, phone calls, emails, code execution, and access to 3000+ tools - all while you sleep.*

</div>

## 🎯 What is Deptheon?

Deptheon is a **fully autonomous AI agent** that won 1st place at the **Agents in the Loop Hackathon 2025** in San Francisco. Unlike traditional chatbots that only handle web-based tasks, Deptheon can:

- 🌐 **Conduct comprehensive web research** using advanced search and scraping
- 📞 **Make live phone calls** and conduct interviews using AI voice technology
- 📧 **Send emails and manage communications** across multiple platforms
- 💻 **Execute code and automate tasks** in sandboxed environments
- 🔗 **Access 3000+ tools and APIs** through Composio integration
- 🔄 **Chain complex workflows** autonomously for hours without human intervention

## 🚀 The Winning Demo

During the hackathon, Deptheon showcased its capabilities with an **autonomous multi-modal workflow** that would typically require hours of manual work:

### What Deptheon Accomplished (Autonomously)

1. **🔍 Web Research**
   - Searched for information about the "Agents in the Loop" hackathon
   - Scraped relevant websites and documentation
   - Found the DevPost page and event details

2. **📞 Live Phone Interview**
   - Automatically dialed +1-415-605-6693
   - Conducted a professional interview using VAPI's AI voice technology
   - Asked structured questions about the hackathon experience
   - Recorded and transcribed the entire conversation

3. **📝 Content Creation & Email**
   - Analyzed the interview transcript
   - Composed a professional LinkedIn post highlighting the achievement
   - Sent the draft via Gmail to the winner for review and posting

### Key Interview Insights Captured

> **Project**: "Deptheon" - A fully autonomous agent with access to hundreds of tools
>
> **Inspiration**: Long-time fascination with agentic AI and perfect hackathon theme fit
>
> **Technical Challenge**: Integrating diverse toolsets smoothly across different platforms
>
> **Innovation**: Full autonomy across planning/execution cycles with real-world actions
>
> **Future Vision**: Scale to more complex workflows and open beta access
>
> **Advice**: "Just go and have fun! The magic happens when curiosity leads the way."

## 🏗️ Architecture Overview

Deptheon is built on a sophisticated **tool-based agent architecture** that enables seamless integration of multiple capabilities:

```
┌─────────────────────────────────────────────────────────────┐
│                       DEPTHEON CORE                        │
├─────────────────────────────────────────────────────────────┤
│  🧠 LLM Engine (OpenAI o3-2025-04-16)                     │
│  🎯 Autonomous Planning & Execution                        │
│  🔄 Multi-step Workflow Orchestration                      │
└─────────────────────────────────────────────────────────────┘
                              │
            ┌─────────────────┼─────────────────┐
            │                 │                 │
    ┌───────▼──────┐ ┌────────▼────────┐ ┌─────▼─────┐
    │   COMPOSIO   │ │      VAPI       │ │  PYTHON   │
    │   3000+      │ │   Voice AI      │ │ EXECUTION │
    │   Tools      │ │   Calling       │ │ SANDBOX   │
    └──────────────┘ └─────────────────┘ └───────────┘
            │                 │                 │
    ┌───────▼──────┐ ┌────────▼────────┐ ┌─────▼─────┐
    │   • Gmail    │ │  • Outbound     │ │ • Web     │
    │   • GitHub   │ │    Calls        │ │   Scraping│
    │   • Slack    │ │  • Interview    │ │ • Data    │
    │   • Notion   │ │    Conduct      │ │   Analysis│
    │   • And      │ │  • Transcript   │ │ • API     │
    │     2996+    │ │    Capture      │ │   Calls   │
    └──────────────┘ └─────────────────┘ └───────────┘
```

## 💡 Key Features

### 🤖 **Fully Autonomous Operation**
- No human intervention required during task execution
- Intelligent planning and adaptive problem-solving
- Self-directed workflow orchestration

### 🛠️ **Extensive Tool Integration**
- **Composio**: Access to 3000+ tools and APIs (Gmail, GitHub, Slack, Notion, etc.)
- **VAPI**: AI-powered voice calling and conversation capabilities
- **Python Execution**: Sandboxed code execution for data processing and automation
- **Web Research**: Advanced search and content extraction

### 🔄 **Agents-in-the-Loop Architecture**
- Continuous planning → execution → learning cycles
- Dynamic tool selection based on task requirements
- Real-time adaptation to changing conditions

### 🛡️ **Production-Ready Design**
- Docker-based sandboxed execution environment
- Comprehensive logging and monitoring
- Error handling and recovery mechanisms
- Configurable safety limits and timeouts

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- Docker (for sandboxed execution)
- OpenAI API key
- Composio API key (optional, for extended tool access)
- VAPI API key (optional, for voice calling)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/deptheon.git
   cd deptheon
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

4. **Configure the agent**
   ```bash
   # Edit config/config.toml with your preferences
   ```

### Usage

#### Command Line Interface
```bash
# Interactive mode
python main.py

# Direct prompt
python main.py --prompt "Research the latest AI trends and email me a summary"
```

#### Example Tasks

**Market Research Workflow:**
```bash
python main.py --prompt "Conduct market research on AI coding assistants, call 3 companies for interviews, and create a comprehensive report with findings and recommendations"
```

**Content Creation Pipeline:**
```bash
python main.py --prompt "Research trending topics in tech, write a blog post, and schedule it for publication on our social media channels"
```

**Customer Outreach Campaign:**
```bash
python main.py --prompt "Find potential customers in our CRM, call them for feedback interviews, and follow up with personalized emails based on their responses"
```

## 🔧 Configuration

### LLM Configuration (`config/config.toml`)
```toml
[llm]
model = "o3-2025-04-16"                    # OpenAI's latest reasoning model
base_url = "https://api.openai.com/v1"
api_key = "your-openai-api-key"
max_completion_tokens = 8192
temperature = 1.0                          # Fixed for reasoning models
reasoning_summary_level = "detailed"       # Get detailed reasoning traces
```

### Environment Variables
```bash
# Core API Keys
OPENAI_API_KEY=your_openai_key
COMPOSIO_API_KEY=your_composio_key
VAPI_API_KEY=your_vapi_key

# Tool-specific Connection IDs (optional)
COMPOSIO_GMAIL_CONNECTION_ID=ca_xxx
COMPOSIO_GITHUB_CONNECTION_ID=ca_xxx
```

## 🛠️ Core Components

### Agent Architecture

- **`Deptheon`** - Main agent class with autonomous decision-making
- **`ToolCallAgent`** - Base class handling tool orchestration and execution
- **`ToolCollection`** - Dynamic tool management and execution framework

### Available Tools

| Tool | Description | Use Cases |
|------|-------------|-----------|
| **ComposioTool** | Access to 3000+ APIs and services | Email, GitHub, Slack, CRM, databases, etc. |
| **VapiTool** | AI-powered voice calling | Interviews, customer calls, research calls |
| **PythonExecute** | Sandboxed code execution | Data analysis, web scraping, calculations |
| **DateTimeTool** | Time and scheduling utilities | Appointment scheduling, time calculations |
| **Terminate** | Graceful task completion | End workflows when objectives are met |

### Prompting System

Deptheon uses advanced prompting strategies optimized for autonomous operation:

- **System Prompt**: Establishes autonomous behavior and capabilities
- **Next Step Prompt**: Guides intelligent tool selection and workflow planning
- **Context Awareness**: Maintains state across multi-step operations

## 🎯 Use Cases & Applications

### 🔬 **Research & Analysis**
- Market research with competitor analysis
- Academic research with source verification
- Trend analysis and report generation

### 📞 **Customer Engagement**
- Automated customer interviews
- Lead qualification calls
- Feedback collection and analysis

### 📈 **Business Automation**
- End-to-end marketing campaigns
- Customer onboarding workflows
- Sales pipeline management

### 💻 **Development Operations**
- Automated testing and deployment
- Code review and documentation
- Issue tracking and resolution


### What Made Deptheon Stand Out

1. **True Autonomy**: Unlike other submissions that required human oversight, Deptheon operates completely independently
2. **Real-World Actions**: Beyond web tasks, it can make actual phone calls and handle real business operations
3. **Scalable Architecture**: Built to handle complex, multi-hour workflows that can run unsupervised
4. **Production Ready**: Not just a demo - it's a complete framework ready for real-world deployment


### Development Setup
```bash
# Install development dependencies
pip install -r requirements.txt

# Run tests
pytest

# Code formatting
black app/
flake8 app/
```

## 🙋‍♂️ Support & Community

- **Issues**: [GitHub Issues](https://github.com/your-username/deptheon/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-username/deptheon/discussions)
- **Email**: your-email@example.com

## 🚀 What's Next?

We're continuously improving Deptheon with:

- 🔧 Additional tool integrations
- 🧠 Enhanced reasoning capabilities
- 🔒 Advanced security features
- 📊 Analytics and monitoring dashboard
- 🌐 Multi-language support

---

<div align="center">

**Built with ❤️ by the Deptheon Team**

[![Star this repo](https://img.shields.io/github/stars/your-username/deptheon?style=social)](https://github.com/your-username/deptheon)
[![Follow on Twitter](https://img.shields.io/twitter/follow/your-handle?style=social)](https://twitter.com/your-handle)

*"The magic happens when curiosity leads the way."*

</div>
# dpth
