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

from langchain_mistralai import ChatMistralAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import tool

try:
    from versailles_weather import get_versailles_weather, get_current_weather, get_daily_forecast
    WEATHER_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Weather functions not available: {e}")
    WEATHER_AVAILABLE = False

from ..config.settings import MISTRAL_CONFIG, get_full_system_prompt


@tool
def versailles_weather_tool(visit_date: str) -> str:
    """Get weather information for Palace of Versailles for a specific date.

    Args:
        visit_date: Visit date in YYYY-MM-DD format or 'today'

    Returns:
        Weather information and visit recommendations for Versailles
    """
    try:
        if not WEATHER_AVAILABLE:
            return "❌ Weather service not available. Please check your OPENWEATHER_API_KEY in .env file."

        # Handle 'today' input
        if visit_date.lower() == 'today':
            visit_date = date.today().isoformat()

        print(f"🌤️ Getting weather for Versailles on {visit_date}")
        result = get_versailles_weather(visit_date)

        if result["status"] == "success":
            if result.get("forecast_type") == "current":
                weather = result["weather"]
                return f"""🌤️ Weather for Versailles today ({result['visit_date']}):
🌡️ Temperature: {weather['temperature']}°C (feels like {weather['feels_like']}°C)
☁️ Conditions: {weather['description']}
💨 Wind: {weather['wind_speed']} m/s
💧 Humidity: {weather['humidity']}%
👁️ Visibility: {weather['visibility']} km

🏰 Visit recommendations:
- Gardens: {"🌧️ Bring an umbrella" if "rain" in weather['description'].lower() else "🌞 Great weather for outdoor visit"}
- Château: Interior visits are comfortable (18-20°C)
"""
            else:
                forecast = result["forecast"]
                return f"""📅 Weather forecast for Versailles on {result['visit_date']} ({result['days_until_visit']} days from now):
🌡️ Temperature: {forecast['min_temp']}°C - {forecast['max_temp']}°C
☁️ Conditions: {forecast['main_condition']}
📊 Based on {forecast['forecasts_count']} detailed forecasts

🏰 Visit recommendations:
- Plan accordingly for {forecast['main_condition'].lower()} conditions
- Check weather closer to your visit date for updates
"""
        else:
            return f"❌ {result.get('error', 'Unable to get weather data')}"

    except Exception as e:
        return f"❌ Error getting weather: {str(e)}"


class SimplifiedVersaillesAgent:
    """
    Simplified Versailles agent with direct tool integration
    """

    def __init__(self):
        """Initialize the agent"""
        self.llm = ChatMistralAI(
            model=MISTRAL_CONFIG["model"],
            api_key=MISTRAL_CONFIG["api_key"],
            temperature=MISTRAL_CONFIG["temperature"],
        )

        # Create tools list
        self.tools = [versailles_weather_tool] if WEATHER_AVAILABLE else []

        # Bind tools to LLM
        self.llm_with_tools = self.llm.bind_tools(self.tools)

        # Load comprehensive Versailles guide prompt
        self.system_prompt = get_full_system_prompt()

        print(f"✅ Simplified Versailles agent initialized")
        print(f"🌤️ Weather tools: {'Available' if WEATHER_AVAILABLE else 'Unavailable'}")
        print(f"🛠️ Total tools: {len(self.tools)}")

    def extract_date(self, text: str) -> Optional[str]:
        """Extract date from user input and convert to YYYY-MM-DD format"""
        # Common date patterns
        patterns = [
            r'\b(\d{4})-(\d{1,2})-(\d{1,2})\b',  # YYYY-MM-DD
            r'\b(\d{1,2})/(\d{1,2})/(\d{4})\b',  # MM/DD/YYYY
            r'\b(\d{1,2})-(\d{1,2})-(\d{4})\b',  # MM-DD-YYYY
        ]

        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                if pattern == patterns[0]:  # YYYY-MM-DD
                    year, month, day = match.groups()
                else:  # MM/DD/YYYY or MM-DD-YYYY
                    month, day, year = match.groups()

                try:
                    # Validate and format date
                    date_obj = datetime(int(year), int(month), int(day)).date()
                    return date_obj.isoformat()
                except ValueError:
                    continue

        # Look for relative dates
        text_lower = text.lower()
        today = date.today()

        if 'aujourd\'hui' in text_lower or 'today' in text_lower:
            return today.isoformat()
        elif 'demain' in text_lower or 'tomorrow' in text_lower:
            tomorrow = today + timedelta(days=1)
            return tomorrow.isoformat()
        elif 'prochaine' in text_lower or 'next week' in text_lower:
            next_week = today + timedelta(days=7)
            return next_week.isoformat()

        return None

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

                # Execute tool calls
                tool_results = []
                for tool_call in tool_calls:
                    try:
                        print(f"🔧 Executing: {tool_call['name']} with args: {tool_call['args']}")

                        if tool_call['name'] == 'versailles_weather_tool':
                            result = versailles_weather_tool.invoke(tool_call['args'])
                            tool_results.append({
                                "tool_call": tool_call,
                                "result": result
                            })
                            print(f"✅ Weather tool executed successfully")
                        else:
                            tool_results.append({
                                "tool_call": tool_call,
                                "error": f"Unknown tool: {tool_call['name']}"
                            })

                    except Exception as e:
                        print(f"❌ Tool execution failed: {e}")
                        tool_results.append({
                            "tool_call": tool_call,
                            "error": str(e)
                        })

                # Generate final response with tool results
                if tool_results and tool_results[0].get("result"):
                    # Use the actual weather data instead of template response
                    final_response = tool_results[0]["result"]
                else:
                    final_response = response.content

                return {
                    "response": final_response,
                    "messages": messages + [response],
                    "tools_used": tool_calls,
                    "tool_results": tool_results,
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