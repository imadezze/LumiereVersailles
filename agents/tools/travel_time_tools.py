"""
Travel time tools for calculating routes to Palace of Versailles
"""
import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional
from langchain_core.tools import tool

# Add scripts directory to path to import travel_time module
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root / "scripts"))

try:
    from travel_time import get_distance_time
    TRAVEL_TIME_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Travel time functions not available: {e}")
    TRAVEL_TIME_AVAILABLE = False

# Palace of Versailles coordinates
VERSAILLES_COORDINATES = (48.8048, 2.1204)
VERSAILLES_ADDRESS = "Palace of Versailles, Place d'Armes, 78000 Versailles, France"

@tool
def get_travel_to_versailles_tool(
    origin_address: str,
    compare_modes: bool = True
) -> str:
    """
    Calculate travel time and distance from a starting point to Palace of Versailles.

    This tool helps visitors plan their journey to the Palace of Versailles by providing
    travel information for different transportation modes.

    Args:
        origin_address: Starting location (address, landmark, or "current location")
        compare_modes: Whether to compare different transportation modes (default: True)

    Returns:
        JSON string with travel information for LLM to interpret and format appropriately
    """
    try:
        if not TRAVEL_TIME_AVAILABLE:
            return json.dumps({
                "status": "error",
                "error": "Travel time service not available. Please check your GOOGLE_API_KEY in .env file.",
                "origin": origin_address
            })

        print(f"🗺️ Calculating travel routes from {origin_address} to Palace of Versailles")

        if compare_modes:
            # Get travel times for all available modes
            modes = ["transit", "driving", "walking", "bicycling"]
            results = {}
            successful_modes = []

            for mode in modes:
                try:
                    result = get_distance_time(
                        origin_address=origin_address,
                        destination_address=VERSAILLES_ADDRESS,
                        mode=mode
                    )
                    results[mode] = result
                    successful_modes.append(mode)
                    print(f"✅ Got {mode} route: {result['duration_min']} min")
                except Exception as e:
                    print(f"❌ Failed to get {mode} route: {e}")
                    # Only include error details for debugging, not in final response
                    results[mode] = {
                        "status": "error",
                        "error": "Route not available",
                        "mode": mode
                    }

            # If no modes were successful, return an error
            if not successful_modes:
                return json.dumps({
                    "status": "error",
                    "error": "Unable to calculate routes from this location",
                    "origin": origin_address,
                    "destination": "Palace of Versailles"
                }, ensure_ascii=False)

            return json.dumps({
                "status": "success",
                "origin": origin_address,
                "destination": "Palace of Versailles",
                "routes": results,
                "comparison": True,
                "successful_modes": successful_modes
            }, ensure_ascii=False)

        else:
            # Default to transit mode only
            result = get_distance_time(
                origin_address=origin_address,
                destination_address=VERSAILLES_ADDRESS,
                mode="transit"
            )

            return json.dumps({
                "status": "success",
                "origin": origin_address,
                "destination": "Palace of Versailles",
                "route": result,
                "comparison": False
            }, ensure_ascii=False)

    except Exception as e:
        error_result = {
            "status": "error",
            "error": f"Error calculating travel route: {str(e)}",
            "origin": origin_address,
            "destination": "Palace of Versailles"
        }
        return json.dumps(error_result, ensure_ascii=False)


def get_all_travel_tools():
    """Get all available travel time tools for the agent"""
    if TRAVEL_TIME_AVAILABLE:
        return [get_travel_to_versailles_tool]
    return []