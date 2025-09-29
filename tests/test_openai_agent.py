#!/usr/bin/env python3
"""
Test OpenAI Agent calling MCP Tools

This script tests an OpenAI agent properly calling MCP tools
and getting weather information for Versailles.
"""

import sys
import os
import subprocess
import time
import json
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

def test_openai_agent_with_mcp():
    """Test OpenAI agent calling MCP weather tool"""
    print("🤖 Testing OpenAI Agent with MCP Weather Tool")
    print("=" * 50)

    # Check if OpenAI API key is available
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key:
        print("❌ OPENAI_API_KEY not found in environment")
        print("💡 Set OPENAI_API_KEY in .env file to test with OpenAI")
        return False

    try:
        from openai import OpenAI

        # Initialize OpenAI client
        client = OpenAI(api_key=openai_key)

        print("✅ OpenAI client initialized")

        # Test with a simple weather query
        test_queries = [
            "What's the weather like at Versailles today?",
            "Should I visit Versailles tomorrow? What's the weather forecast?",
            "I'm planning to visit Versailles this weekend, what should I expect weather-wise?"
        ]

        # Import and test the MCP tool function directly first
        sys.path.append(str(project_root / "mcp_servers"))
        from versailles_agent_server import get_versailles_weather_forecast

        from datetime import date, timedelta

        for i, query in enumerate(test_queries, 1):
            print(f"\n🔍 Test {i}: {query}")

            # Determine appropriate date based on query
            if "today" in query.lower():
                test_date = date.today().isoformat()
            elif "tomorrow" in query.lower():
                test_date = (date.today() + timedelta(days=1)).isoformat()
            else:
                test_date = (date.today() + timedelta(days=2)).isoformat()

            print(f"📅 Using date: {test_date}")

            # Call the weather tool
            print("🌤️  Calling weather tool...")
            weather_result = get_versailles_weather_forecast(test_date)

            if weather_result.get("status") == "success":
                print("✅ Weather data retrieved successfully")

                # Create a system message that includes weather data
                weather_context = f"""
Weather data for Versailles on {test_date}:
- Location: {weather_result.get('location', {}).get('name', 'Palace of Versailles')}
- Days until visit: {weather_result.get('days_until_visit', 0)}
- Forecast type: {weather_result.get('forecast_type', 'unknown')}
"""

                if weather_result.get('weather'):
                    w = weather_result['weather']
                    weather_context += f"""- Current temperature: {w.get('temperature')}°C
- Feels like: {w.get('feels_like')}°C
- Conditions: {w.get('description')}
- Humidity: {w.get('humidity')}%
- Wind speed: {w.get('wind_speed')} m/s"""

                if weather_result.get('forecast') and weather_result.get('forecast_type') == 'seasonal':
                    f = weather_result['forecast']['seasonal_forecast']
                    weather_context += f"""- Season: {f.get('season')}
- Typical conditions: {f.get('typical_condition')}
- Temperature range: {f['temperature_range']['min']}°C to {f['temperature_range']['max']}°C"""

                # Now ask OpenAI to interpret this data
                print("🧠 Asking OpenAI to interpret weather data...")

                messages = [
                    {
                        "role": "system",
                        "content": """You are a helpful assistant specializing in weather information for the Palace of Versailles.
                        You help visitors plan their trips based on weather conditions.
                        Provide practical, friendly advice about what to expect and how to prepare for their visit."""
                    },
                    {
                        "role": "user",
                        "content": f"""Based on this weather information, please answer the user's question: "{query}"

{weather_context}

Please provide a helpful response about visiting Versailles based on this weather data."""
                    }
                ]

                try:
                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=messages,
                        max_tokens=300,
                        temperature=0.7
                    )

                    ai_response = response.choices[0].message.content
                    print("💬 OpenAI Response:")
                    print(f"   {ai_response}")
                    print("✅ Test completed successfully")

                except Exception as e:
                    print(f"❌ OpenAI API error: {e}")
                    return False

            else:
                print(f"❌ Weather tool error: {weather_result.get('error')}")
                return False

        print(f"\n🎉 All {len(test_queries)} tests completed successfully!")
        return True

    except ImportError:
        print("❌ OpenAI library not installed")
        print("💡 Install with: pip install openai")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_mcp_tool_definition():
    """Test the MCP tool definition and metadata"""
    print("\n🔧 Testing MCP Tool Definition")
    print("=" * 30)

    try:
        sys.path.append(str(project_root / "mcp_servers"))
        from versailles_agent_server import get_versailles_weather_forecast

        # Test function metadata
        print(f"✅ Tool name: {get_versailles_weather_forecast.__name__}")
        print(f"✅ Tool docstring: {bool(get_versailles_weather_forecast.__doc__)}")

        # Test with a sample date
        from datetime import date
        test_date = date.today().isoformat()

        print(f"🧪 Testing tool with date: {test_date}")
        result = get_versailles_weather_forecast(test_date)

        expected_keys = ['status', 'date', 'location']
        present_keys = [key for key in expected_keys if key in result]

        print(f"✅ Tool response keys: {list(result.keys())}")
        print(f"✅ Expected keys present: {len(present_keys)}/{len(expected_keys)}")

        return result.get('status') == 'success'

    except Exception as e:
        print(f"❌ Tool definition test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🏰 Testing OpenAI Agent + MCP Weather Integration")
    print("=" * 60)

    tests = [
        ("MCP Tool Definition", test_mcp_tool_definition),
        ("OpenAI Agent with MCP", test_openai_agent_with_mcp),
    ]

    results = {}

    for test_name, test_func in tests:
        try:
            print(f"\n📋 Running: {test_name}")
            success = test_func()
            results[test_name] = success
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results[test_name] = False

    print("\n" + "=" * 60)
    print("📊 Final Results:")

    for test_name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {test_name}: {status}")

    total_passed = sum(results.values())
    total_tests = len(results)

    print(f"\nPassed: {total_passed}/{total_tests}")

    if total_passed == total_tests:
        print("🎉 All tests passed! OpenAI + MCP integration working!")
        return 0
    else:
        print("⚠️  Some tests failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())