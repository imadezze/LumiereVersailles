# Lumière Versailles

MCP server providing weather forecast tools for Palace of Versailles visits. This project includes a powerful MCP server for weather analysis and a LangGraph agent for intelligent weather-based visit planning.

## Features

- 🌤️ **Weather Forecasting**: Detailed weather forecasts for Versailles palace visits
- 🏰 **Visit Planning**: AI-powered recommendations based on weather conditions
- 🤖 **LangGraph Agent**: Intelligent agent that decides when to call weather tools
- 📊 **MCP Integration**: Model Context Protocol server for tool interoperability
- 🌐 **HTTP Transport**: Streamable HTTP transport for web deployment

## Project Structure

- `mcp_servers/versailles_agent_server.py` - Main MCP server for weather forecasting
- `agents/core/agent.py` - LangGraph agent with MCP integration
- `scripts/versailles_weather.py` - Core weather functionality
- `tests/test_mcp_agent.py` - Test suite for MCP agent integration

## Running the MCP Server

In order to run your MCP server locally, use the following command:

```bash
python mcp_servers/versailles_agent_server.py
```

The server will automatically start in **streamable HTTP** mode on port 8001.

## Running the Agent Tests

To test the LangGraph agent with MCP integration:

```bash
python tests/test_mcp_agent.py
```

This will test both direct MCP server connection and agent integration.

## Deployment Commands

For deployment platforms, use these commands:

### Using pip:
**Install command:**
```bash
pip install -r requirements.txt
```

**Start command:**
```bash
python mcp_servers/versailles_agent_server.py
```

## Exposing the Server

If you want to expose the server to be visible globally, you can use [ngrok]()

```bash
ngrok http [Port Number]
```

You can then use the resulting public address to integrate your MCP server into an existing platform (e.g. Mistral LeChat).


