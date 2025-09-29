"""
Weather tools for the Versailles Weather Agent
"""
import sys
from pathlib import Path
from typing import Dict, Any
from langchain_core.tools import tool

# Add scripts directory to path to import weather module
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root / "scripts"))

from versailles_weather import get_versailles_weather

@tool
def get_versailles_weather_tool(visit_date: str) -> Dict[str, Any]:
    """
    Get weather forecast for Palace of Versailles for a specific visit date.

    This tool provides detailed weather information to help plan visits to
    the Palace of Versailles and its gardens.

    Args:
        visit_date: The date of the visit in YYYY-MM-DD format (e.g., "2025-01-15")

    Returns:
        Dictionary containing:
        - date: The visit date
        - location: Versailles information
        - weather: Current weather conditions (if visiting today)
        - forecast: Relevant forecast data for the date
        - forecast_type: Type of forecast (current, 5day, daily, or seasonal)
        - days_until_visit: Number of days until the visit
        - status: Success/error status

    Example:
        >>> get_versailles_weather_tool("2025-01-15")
        {
            "date": "2025-01-15",
            "location": {"name": "Palace of Versailles", ...},
            "forecast": {...},
            "forecast_type": "5day",
            "days_until_visit": 3,
            "status": "success"
        }
    """
    try:
        result = get_versailles_weather(visit_date)
        return result
    except Exception as e:
        return {
            "error": str(e),
            "status": "error",
            "date": visit_date,
            "message": f"Failed to retrieve weather data for {visit_date}"
        }

def get_all_weather_tools():
    """Get all available weather tools for the agent"""
    return [get_versailles_weather_tool]