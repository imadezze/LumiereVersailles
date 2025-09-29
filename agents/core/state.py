"""
State management for Versailles Weather Agent
"""
from typing import TypedDict, List, Optional, Dict, Any
from langchain_core.messages import BaseMessage


class AgentState(TypedDict):
    """State for the Versailles Weather Agent"""

    # Conversation history
    messages: List[BaseMessage]

    # Current user query
    user_query: str

    # Extracted date from user query
    visit_date: Optional[str]

    # Weather data retrieved
    weather_data: Optional[Dict[str, Any]]

    # Agent response
    response: Optional[str]

    # Error information
    error: Optional[str]

    # Iteration count for safety
    iteration_count: int