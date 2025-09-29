"""
Simplified Versailles Agent with direct weather tool integration
"""
import re
import sys
import os
from datetime import datetime, date, timedelta
from typing import Dict, Any, Optional, List
from pathlib import Path

# Add scripts directory to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root / "scripts"))

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import tool

try:
    from versailles_weather import get_versailles_weather, get_current_weather, get_daily_forecast
    WEATHER_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Weather functions not available: {e}")
    WEATHER_AVAILABLE = False

from ..config.settings import get_llm_config, get_full_system_prompt


@tool
def versailles_weather_tool(visit_date: str) -> str:
    """Get weather information for Palace of Versailles for a specific date.

    Args:
        visit_date: Visit date in YYYY-MM-DD format or 'today'

    Returns:
        JSON weather data for LLM to interpret and format appropriately
    """
    try:
        if not WEATHER_AVAILABLE:
            return '{"status": "error", "error": "Weather service not available. Please check your OPENWEATHER_API_KEY in .env file."}'

        # Handle 'today' input
        if visit_date.lower() == 'today':
            visit_date = date.today().isoformat()

        print(f"🌤️ Getting weather for Versailles on {visit_date}")
        result = get_versailles_weather(visit_date)

        # Return the raw JSON data for LLM to interpret
        import json
        return json.dumps(result, ensure_ascii=False)

    except Exception as e:
        error_result = {
            "status": "error",
            "error": f"Error getting weather: {str(e)}",
            "visit_date": visit_date
        }
        import json
        return json.dumps(error_result, ensure_ascii=False)


class SimplifiedVersaillesAgent:
    """
    Simplified Versailles agent with direct tool integration
    """

    def __init__(self):
        """Initialize the agent"""
        # Get LLM configuration
        provider, config = get_llm_config()

        if provider == "mistral":
            from langchain_mistralai import ChatMistralAI
            self.llm = ChatMistralAI(
                model=config["model"],
                api_key=config["api_key"],
                temperature=config["temperature"],
            )
        else:  # openai
            from langchain_openai import ChatOpenAI
            self.llm = ChatOpenAI(
                model=config["model"],
                openai_api_key=config["api_key"],
                temperature=config["temperature"],
            )

        print(f"🤖 Using {provider.upper()} LLM: {config['model']}")

        # Create tools list
        self.tools = [versailles_weather_tool] if WEATHER_AVAILABLE else []

        # Bind tools to LLM
        self.llm_with_tools = self.llm.bind_tools(self.tools)

        # Load comprehensive Versailles guide prompt
        self.system_prompt = get_full_system_prompt()

        print(f"✅ Simplified Versailles agent initialized")
        print(f"🌤️ Weather tools: {'Available' if WEATHER_AVAILABLE else 'Unavailable'}")
        print(f"🛠️ Total tools: {len(self.tools)}")


    def process_query(self, user_input: str) -> Dict[str, Any]:
        """Main method to process a user query"""
        try:
            # Create messages
            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=user_input)
            ]

            # Get response from LLM with tools
            response = self.llm_with_tools.invoke(messages)

            # Check if LLM wants to call tools
            tool_calls = getattr(response, 'tool_calls', [])

            if tool_calls and WEATHER_AVAILABLE:
                print(f"🛠️ LLM requested {len(tool_calls)} tool calls")

                # Execute tool calls and create tool messages
                tool_messages = []
                for tool_call in tool_calls:
                    try:
                        print(f"🔧 Executing: {tool_call['name']} with args: {tool_call['args']}")

                        if tool_call['name'] == 'versailles_weather_tool':
                            result = versailles_weather_tool.invoke(tool_call['args'])

                            # Create a tool message with the result
                            from langchain_core.messages import ToolMessage
                            tool_messages.append(ToolMessage(
                                content=result,
                                tool_call_id=tool_call['id']
                            ))
                            print(f"✅ Weather tool executed successfully")

                    except Exception as e:
                        print(f"❌ Tool execution failed: {e}")
                        from langchain_core.messages import ToolMessage
                        tool_messages.append(ToolMessage(
                            content=f"Error: {str(e)}",
                            tool_call_id=tool_call['id']
                        ))

                # Generate final response with tool results
                final_messages = messages + [response] + tool_messages
                final_response = self.llm.invoke(final_messages)

                return {
                    "response": final_response.content,
                    "messages": final_messages + [final_response],
                    "tools_used": tool_calls,
                    "status": "success"
                }

            return {
                "response": response.content,
                "messages": messages + [response],
                "tools_used": tool_calls,
                "status": "success"
            }

        except Exception as e:
            print(f"❌ Agent error: {e}")
            return {
                "response": f"Je m'excuse, mais je rencontre une erreur technique: {str(e)}",
                "error": str(e),
                "status": "error"
            }