#!/usr/bin/env python3
"""
MCP Server for Versailles Weather

This server exposes the Versailles Weather function as an MCP tool
that can be used by other systems and LLMs.
"""

import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add scripts directory to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root / "scripts"))

from mcp.server.fastmcp import FastMCP

# Initialize MCP server
mcp = FastMCP("versailles-weather-server")

@mcp.tool(
    name="get_versailles_weather_forecast",
    description="Get detailed weather forecast for Palace of Versailles for a specific visit date. Provides temperature, conditions, humidity, wind speed, and visit planning context."
)
def get_versailles_weather_forecast(visit_date: str) -> dict:
    """
    Get weather forecast for Versailles for a specific visit date.

    Args:
        visit_date: Date in YYYY-MM-DD format (e.g., "2025-01-15")

    Returns:
        Dictionary containing weather data and visit recommendations with keys:
        - status: "success" or "error"
        - date: Visit date
        - location: Palace information
        - weather: Current weather (if today)
        - forecast: Forecast data
        - forecast_type: Type of forecast (current/5day/seasonal)
        - days_until_visit: Days until the visit
    """
    import sys
    print(f"🚨 MCP TOOL CALLED VIA HTTP! 🚨", file=sys.stderr)
    print(f"🌤️  Tool called: get_versailles_weather_forecast('{visit_date}')", file=sys.stderr)
    print(f"📅 Visit date parameter: {visit_date}", file=sys.stderr)

    try:
        from versailles_weather import get_versailles_weather

        # Get weather data directly
        result = get_versailles_weather(visit_date)
        print(f"✅ Weather data retrieved successfully for {visit_date}", file=sys.stderr)
        return result

    except Exception as e:
        print(f"❌ Error getting weather data: {e}", file=sys.stderr)
        return {
            "error": str(e),
            "status": "error",
            "date": visit_date,
            "message": f"Failed to retrieve weather data for {visit_date}"
        }

if __name__ == "__main__":
    import sys
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8001)
    args = parser.parse_args()

    print("🏰 Starting Versailles Weather MCP Server...")
    print("Available tool:")
    print("  - get_versailles_weather_forecast: Get weather forecast for Versailles")
    print()

    print(f"🔌 HTTP Server starting on http://localhost:{args.port}", file=sys.stderr)
    print("💡 Use Ctrl+C to stop the server", file=sys.stderr)

    # Set host via settings and use streamable-http transport
    mcp.settings.host = "127.0.0.1"
    mcp.settings.port = args.port
    mcp.run(transport="streamable-http")