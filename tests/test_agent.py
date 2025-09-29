#!/usr/bin/env python3
"""
Test script for the Versailles Weather System

This script tests the basic functionality of the weather tools
and MCP server integration.
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))
sys.path.append(str(project_root / "scripts"))

def test_environment():
    """Test environment variables and configuration"""
    print("🔧 Testing environment configuration...")

    required_vars = ["OPENWEATHER_API_KEY"]
    optional_vars = ["OPENAI_API_KEY", "OPENAI_MODEL"]

    missing_required = []
    missing_optional = []

    for var in required_vars:
        if not os.getenv(var):
            missing_required.append(var)
        else:
            print(f"✅ {var}: Set")

    for var in optional_vars:
        if not os.getenv(var):
            missing_optional.append(var)
        else:
            print(f"✅ {var}: Set")

    if missing_required:
        print(f"❌ Missing required environment variables: {missing_required}")
        return False

    if missing_optional:
        print(f"⚠️  Missing optional environment variables: {missing_optional}")

    return True

def test_weather_tools():
    """Test weather tool functionality"""
    print("\n🌤️  Testing weather tools...")

    try:
        from versailles_weather import get_versailles_weather

        # Test weather tool with today's date
        from datetime import date
        test_date = date.today().isoformat()
        result = get_versailles_weather(test_date)

        print(f"Weather tool result: {result.get('status', 'unknown')}")
        if result.get("status") == "success":
            print(f"  - Date: {result.get('date')}")
            print(f"  - Forecast type: {result.get('forecast_type')}")
            print(f"  - Days until visit: {result.get('days_until_visit')}")
            if result.get('weather'):
                weather = result['weather']
                print(f"  - Current temp: {weather.get('temperature')}°C")
                print(f"  - Conditions: {weather.get('description')}")
        else:
            print(f"  - Error: {result.get('error')}")

        return result.get("status") == "success"

    except Exception as e:
        print(f"❌ Weather tools test failed: {e}")
        return False

def test_date_extraction():
    """Test date extraction functionality"""
    print("\n📅 Testing date extraction...")

    try:
        import re
        from datetime import datetime, date

        def extract_date(text):
            """Simple date extraction function"""
            patterns = [
                r'\b(\d{4})-(\d{1,2})-(\d{1,2})\b',  # YYYY-MM-DD
                r'\b(\d{1,2})/(\d{1,2})/(\d{4})\b',  # MM/DD/YYYY
            ]

            for pattern in patterns:
                match = re.search(pattern, text)
                if match:
                    if pattern == patterns[0]:  # YYYY-MM-DD
                        year, month, day = match.groups()
                    else:  # MM/DD/YYYY
                        month, day, year = match.groups()

                    try:
                        date_obj = datetime(int(year), int(month), int(day)).date()
                        return date_obj.isoformat()
                    except ValueError:
                        continue

            # Handle relative dates
            text_lower = text.lower()
            today = date.today()
            if 'today' in text_lower:
                return today.isoformat()
            elif 'tomorrow' in text_lower:
                from datetime import timedelta
                tomorrow = today + timedelta(days=1)
                return tomorrow.isoformat()

            return None

        # Test date extraction
        test_inputs = [
            "What's the weather on 2025-01-15?",
            "I'm visiting tomorrow",
            "How's the weather today?",
            "Weather on 12/25/2024?"
        ]

        for test_input in test_inputs:
            extracted_date = extract_date(test_input)
            print(f"  Input: '{test_input}' -> Date: {extracted_date}")

        return True

    except Exception as e:
        print(f"❌ Date extraction test failed: {e}")
        return False

def test_mcp_server():
    """Test MCP server tools"""
    print("\n🔌 Testing MCP server tools...")

    try:
        # Import the MCP server functions
        sys.path.append(str(project_root / "mcp_servers"))
        from versailles_agent_server import get_versailles_weather_forecast

        # Test weather forecast tool with today's date
        from datetime import date
        test_date = date.today().isoformat()
        result = get_versailles_weather_forecast(test_date)

        print(f"MCP weather forecast result: {result.get('status')}")
        if result.get("status") == "success":
            print(f"  - Date: {result.get('date')}")
            print(f"  - Location: {result.get('location', {}).get('name')}")
            print(f"  - Forecast type: {result.get('forecast_type')}")
            return True
        else:
            print(f"  - Error: {result.get('error')}")
            return False

    except Exception as e:
        print(f"❌ MCP server test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🏰 Starting Versailles Weather System Tests")
    print("=" * 50)

    tests = [
        ("Environment", test_environment),
        ("Weather Tools", test_weather_tools),
        ("Date Extraction", test_date_extraction),
        ("MCP Server", test_mcp_server),
    ]

    results = {}

    for test_name, test_func in tests:
        try:
            success = test_func()
            results[test_name] = success
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results[test_name] = False

    print("\n" + "=" * 50)
    print("📋 Test Summary:")

    for test_name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {test_name}: {status}")

    total_passed = sum(results.values())
    total_tests = len(results)

    print(f"\nPassed: {total_passed}/{total_tests}")

    if total_passed == total_tests:
        print("🎉 All tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        print("\n💡 Make sure you have:")
        print("   - Set OPENWEATHER_API_KEY in .env file")
        print("   - Installed required dependencies: pip install -r requirements.txt")
        return 1

if __name__ == "__main__":
    sys.exit(main())