#!/usr/bin/env python3
"""
MCP Server for Versailles Weather Tools

This server exposes weather forecasting functions for the Palace of Versailles
as MCP tools that can be used by LangGraph agents.
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the scripts directory to the path so we can import the weather module
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root / "scripts"))

from mcp.server.fastmcp import FastMCP
from versailles_weather import get_5day_forecast, get_daily_forecast, get_versailles_weather

# Initialize MCP server
mcp = FastMCP("versailles-weather-server")

@mcp.tool()
def get_versailles_5day_forecast() -> dict:
    """
    Get 5-day weather forecast for Palace of Versailles with 3-hour intervals.

    Returns detailed forecast data including temperature, conditions, humidity,
    wind speed, and cloud coverage for planning visits to Versailles.
    """
    try:
        return get_5day_forecast()
    except Exception as e:
        return {
            "error": str(e),
            "status": "error",
            "message": "Failed to retrieve 5-day forecast"
        }

@mcp.tool()
def get_versailles_daily_forecast() -> dict:
    """
    Get daily weather summaries for Palace of Versailles for the next 5 days.

    Returns aggregated daily data with min/max temperatures and main conditions,
    perfect for planning multi-day visits to Versailles.
    """
    try:
        return get_daily_forecast()
    except Exception as e:
        return {
            "error": str(e),
            "status": "error",
            "message": "Failed to retrieve daily forecast"
        }

@mcp.tool()
def get_weather_for_visit_date(visit_date: str) -> dict:
    """
    Get weather forecast for a specific Versailles visit date.

    Args:
        visit_date: Date in YYYY-MM-DD format (e.g., "2025-01-15")

    Returns detailed weather information for the specific visit date,
    including recommendations for planning your Versailles experience.
    """
    try:
        return get_versailles_weather(visit_date)
    except Exception as e:
        return {
            "error": str(e),
            "status": "error",
            "message": f"Failed to retrieve weather for {visit_date}"
        }

@mcp.tool()
def get_weather_summary_for_planning(visit_date: str) -> str:
    """
    Get a formatted weather summary for Versailles visit planning.

    Args:
        visit_date: Date in YYYY-MM-DD format (e.g., "2025-01-15")

    Returns human-readable weather summary with practical recommendations
    for visiting the Palace of Versailles and its gardens.
    """
    try:
        result = get_versailles_weather(visit_date)

        if result["status"] == "error":
            return f"⚠️ Weather data unavailable: {result.get('error', 'Unknown error')}"

        forecast = result["forecast"]
        days_until = result["days_until_visit"]

        # Format the response for planning
        summary = []
        summary.append(f"🏰 Weather for Versailles visit on {result['visit_date']}:")

        if days_until == 0:
            summary.append("📅 Today's visit")
        elif days_until == 1:
            summary.append("📅 Tomorrow's visit")
        else:
            summary.append(f"📅 {days_until} days from today")

        summary.append(f"🌡️ Temperature: {forecast['min_temp']}°C to {forecast['max_temp']}°C")
        summary.append(f"☁️ Conditions: {forecast['main_condition']}")
        summary.append(f"📊 {forecast['forecasts_count']} detailed forecasts available")


        return "\n".join(summary)

    except Exception as e:
        return f"❌ Error retrieving weather summary: {str(e)}"

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8001)
    args = parser.parse_args()

    print("🏰 Starting Versailles Weather MCP Server...")
    print("Available tools:")
    print("  - get_versailles_5day_forecast: Detailed 5-day forecast")
    print("  - get_versailles_daily_forecast: Daily summaries")
    print("  - get_weather_for_visit_date: Specific date weather")
    print("  - get_weather_summary_for_planning: Formatted planning summary")
    print()

    print(f"🔌 HTTP Server starting on http://localhost:{args.port}")
    print("💡 Use Ctrl+C to stop the server")

    # Set host via settings and use streamable-http transport
    mcp.settings.host = "127.0.0.1"
    mcp.settings.port = args.port
    mcp.run(transport="streamable-http")