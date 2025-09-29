# Versailles Weather Agent

A sophisticated LangGraph-based agent that provides weather forecasts and visit planning assistance for the Palace of Versailles using OpenAI models.

## Architecture

### Directory Structure

```
agents/
├── core/                    # Core agent logic
│   ├── __init__.py         # Package exports
│   ├── agent.py            # Main VersaillesWeatherAgent class
│   ├── graph.py            # LangGraph workflow definition
│   └── state.py            # Agent state management
├── tools/                   # Tool integrations
│   ├── __init__.py         # Tool exports
│   └── weather_tools.py    # Weather API tool wrappers
├── config/                  # Configuration management
│   └── settings.py         # Settings and prompt loading
├── prompts/                 # External prompt files
│   ├── system_prompt.md    # Main system instructions
│   ├── weather_tool_prompt.md  # Weather tool usage guide
│   └── user_interaction_prompt.md  # User interaction patterns
└── README.md               # This file
```

## Features

### Core Capabilities
- **Weather Forecasting**: Get accurate weather data for Versailles for any date
- **Date Extraction**: Automatically extract and parse dates from natural language
- **Visit Planning**: Provide context-aware advice based on weather conditions
- **Natural Language Interface**: Chat naturally about weather and visit planning

### Technical Features
- **LangGraph Workflow**: Sophisticated multi-step reasoning process
- **OpenAI Integration**: Uses GPT models for natural language understanding
- **External Prompts**: All prompts stored in separate markdown files
- **MCP Server**: Expose agent functionality through MCP protocol
- **Error Handling**: Robust error handling and fallback mechanisms

## Configuration

### Environment Variables

Required environment variables:

```bash
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4  # optional, defaults to gpt-4
OPENAI_TEMPERATURE=0.1  # optional, defaults to 0.1

# Weather API Configuration
OPENWEATHER_API_KEY=your_openweather_api_key

# Agent Configuration (optional)
AGENT_MAX_ITERATIONS=5  # Maximum workflow iterations
AGENT_TIMEOUT=30       # Timeout in seconds
```

### Configuration Validation

The system includes configuration validation:

```python
from agents.config.settings import validate_config

status = validate_config()
# Returns: {"openai_api_key": True, "weather_api_key": True, "prompts_exist": True}
```

## Usage

### Direct Agent Usage

```python
from agents.core.agent import VersaillesWeatherAgent

agent = VersaillesWeatherAgent()
result = agent.process_query("What's the weather at Versailles on January 15, 2025?")
print(result["response"])
```

### LangGraph Workflow

```python
from agents.core.graph import create_compiled_agent
from langchain_core.messages import HumanMessage

agent = create_compiled_agent()

state = {
    "messages": [HumanMessage(content="Weather forecast for tomorrow?")],
    "user_query": "Weather forecast for tomorrow?",
    "iteration_count": 0
}

result = agent.invoke(state)
print(result["response"])
```

### MCP Server

The agent is exposed as an MCP server with multiple tools:

```python
# Available MCP tools:
# - ask_versailles_weather_agent(question: str)
# - get_versailles_weather_simple(visit_date: str)
# - get_visit_planning_advice(visit_date: str, interests: str)
# - chat_with_versailles_agent(message: str)
# - get_agent_status()
```

## LangGraph Workflow

The agent uses a structured workflow:

1. **Parse Input**: Extract date and intent from user query
2. **Weather Tool** (conditional): Call weather API if needed
3. **Response Generation**: Generate natural language response
4. **End**: Return final response

### Workflow Diagram

```
Entry → Parse Input → [Weather Tool?] → Response → End
                            ↓
                       Weather Tool → Response
```

## Prompt Management

All prompts are stored externally in markdown files:

- **system_prompt.md**: Core agent personality and capabilities
- **weather_tool_prompt.md**: Instructions for weather tool usage
- **user_interaction_prompt.md**: Guidelines for user interaction patterns

### Loading Prompts

```python
from agents.config.settings import load_prompt, get_full_system_prompt

# Load individual prompt
system_prompt = load_prompt("system")

# Get complete assembled prompt
full_prompt = get_full_system_prompt()
```

## Testing

Run the comprehensive test suite:

```bash
python tests/test_agent.py
```

Tests cover:
- Configuration validation
- Weather tool functionality
- Basic agent operations
- LangGraph workflow execution
- MCP server integration

## Error Handling

The agent includes robust error handling:

- **Configuration Errors**: Missing API keys or prompt files
- **API Errors**: Weather service unavailable or rate limits
- **Date Parsing Errors**: Invalid or ambiguous date formats
- **Model Errors**: OpenAI API issues or token limits

## Performance Considerations

- **Caching**: Weather data could be cached for recent queries
- **Token Usage**: Prompts are optimized for minimal token consumption
- **Timeout Handling**: Built-in timeouts prevent hanging requests
- **Iteration Limits**: Prevents infinite loops in workflow

## Extending the Agent

### Adding New Tools

1. Create tool in `agents/tools/`
2. Add to tool list in agent initialization
3. Update prompts to include tool usage instructions

### Modifying Workflow

1. Edit `agents/core/graph.py`
2. Add new nodes or modify existing ones
3. Update state management in `agents/core/state.py`

### Customizing Prompts

1. Edit markdown files in `agents/prompts/`
2. Add new prompt files and update `settings.py`
3. Reload configuration in running instances