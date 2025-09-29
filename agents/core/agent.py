"""
Core agent implementation for Versailles Weather Agent with MCP integration
"""
import re
from datetime import datetime, date
from typing import Dict, Any, Optional, List
from langchain_mistralai import ChatMistralAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate

from ..config.settings import MISTRAL_CONFIG, get_full_system_prompt
from .state import AgentState

# MCP integration
try:
    from langchain_mcp_adapters.client import MultiServerMCPClient
    import asyncio
except ImportError:
    print("Warning: langchain-mcp-adapters not installed. MCP features disabled.")
    MultiServerMCPClient = None


class VersaillesWeatherAgent:
    """
    LangGraph agent for Versailles weather assistance
    """

    def __init__(self):
        """Initialize the agent with Mistral model and MCP tools"""
        self.llm = ChatMistralAI(
            model=MISTRAL_CONFIG["model"],
            api_key=MISTRAL_CONFIG["api_key"],
            temperature=MISTRAL_CONFIG["temperature"],
        )

        # Initialize MCP client for weather tools
        self.mcp_tools = []
        if MultiServerMCPClient:
            try:
                # Connect to local weather MCP server
                from pathlib import Path
                project_root = Path(__file__).parent.parent.parent

                self.mcp_client = MultiServerMCPClient({
                    "versailles_weather": {
                        "url": "http://localhost:8001/mcp",
                        "transport": "streamable_http"
                    }
                })

                # Get tools asynchronously
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                self.mcp_tools = loop.run_until_complete(self.mcp_client.get_tools())
                loop.close()

                print(f"✅ Connected to MCP server with {len(self.mcp_tools)} weather tools")
            except Exception as e:
                print(f"⚠️  Failed to connect to MCP server: {e}")

        # Use MCP tools with LLM
        self.llm_with_tools = self.llm.bind_tools(self.mcp_tools) if self.mcp_tools else self.llm

        # Load system prompt
        self.system_prompt = get_full_system_prompt()

        # Create prompt template
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("human", "{user_input}")
        ])

    def extract_date(self, text: str) -> Optional[str]:
        """
        Extract date from user input and convert to YYYY-MM-DD format
        """
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

        if 'today' in text_lower:
            return today.isoformat()
        elif 'tomorrow' in text_lower:
            tomorrow = date(today.year, today.month, today.day + 1)
            return tomorrow.isoformat()
        elif 'next week' in text_lower:
            next_week = date(today.year, today.month, today.day + 7)
            return next_week.isoformat()

        return None


    def process_user_input(self, user_input: str) -> Dict[str, Any]:
        """
        Process user input - let LLM decide what tools to use
        """
        result = {
            "user_query": user_input,
            "extracted_date": self.extract_date(user_input)
        }
        return result

    def process_query(self, user_input: str) -> Dict[str, Any]:
        """
        Main method to process a user query - let LLM decide tools to use
        """
        try:
            # Create messages for the LLM with tools
            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=user_input)
            ]

            # Let the LLM decide what tools to use and generate response
            response = self.llm_with_tools.invoke(messages)

            # Check if the LLM wants to call tools
            tool_calls = getattr(response, 'tool_calls', [])

            if tool_calls and self.mcp_tools:
                print(f"🛠️  LLM requested {len(tool_calls)} tool calls")

                # Execute tool calls through MCP
                tool_results = []
                for tool_call in tool_calls:
                    try:
                        print(f"🔧 Executing tool: {tool_call['name']} with args: {tool_call['args']}")

                        # Find the matching tool from MCP tools
                        matching_tool = None
                        for tool in self.mcp_tools:
                            if tool.name == tool_call['name']:
                                matching_tool = tool
                                break

                        if matching_tool:
                            # Execute the tool asynchronously (MCP tools are async)
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)
                            result = loop.run_until_complete(matching_tool.ainvoke(tool_call['args']))
                            loop.close()

                            tool_results.append({
                                "tool_call": tool_call,
                                "result": result
                            })
                            print(f"✅ Tool executed successfully via MCP")
                        else:
                            print(f"❌ Tool {tool_call['name']} not found in MCP tools")
                            tool_results.append({
                                "tool_call": tool_call,
                                "error": f"Tool {tool_call['name']} not found"
                            })

                    except Exception as e:
                        print(f"❌ Tool execution failed: {e}")
                        tool_results.append({
                            "tool_call": tool_call,
                            "error": str(e)
                        })

                # Generate final response with tool results
                tool_message = f"\n\nTool results: {tool_results}"
                final_response = response.content + tool_message

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
            return {
                "response": f"I apologize, but I encountered an error: {str(e)}",
                "error": str(e),
                "status": "error"
            }