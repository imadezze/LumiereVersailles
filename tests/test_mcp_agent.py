#!/usr/bin/env python3
"""
Test LangGraph Agent with MCP Weather Integration

This script tests the LangGraph agent properly connecting to MCP server
and letting the LLM decide when to call weather tools.
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

def test_mcp_agent_integration():
    """Test LangGraph agent with MCP weather tools"""
    print("🤖 Testing LangGraph Agent + MCP Integration")
    print("=" * 50)

    # Check environment
    if not os.getenv("MISTRAL_API_KEY"):
        print("❌ MISTRAL_API_KEY not found")
        return False

    if not os.getenv("OPENWEATHER_API_KEY"):
        print("❌ OPENWEATHER_API_KEY not found")
        return False

    try:
        # Import the agent
        from agents.core.agent import VersaillesWeatherAgent

        print("🔧 Initializing agent...")
        agent = VersaillesWeatherAgent()

        # Test queries that should trigger weather tool usage
        test_queries = [
            "What's the weather like at Versailles today?",
            "Should I visit Versailles tomorrow based on the weather?",
            "Hello, how are you?",  # Should not trigger weather tool
            "I'm planning to visit Versailles this weekend, what's the forecast?"
        ]

        for i, query in enumerate(test_queries, 1):
            print(f"\n🔍 Test {i}: '{query}'")

            # Process query with agent
            result = agent.process_query(query)

            if result.get("status") == "success":
                print("✅ Agent responded successfully")
                print(f"📝 Response: {result['response'][:100]}...")

                # Check if tools were used
                tools_used = result.get("tools_used", [])
                if tools_used:
                    print(f"🛠️  Tools used: {len(tools_used)}")
                    for tool in tools_used:
                        print(f"   - {tool.get('name', 'unknown')}")
                else:
                    print("🛠️  No tools used (LLM responded directly)")

            else:
                print(f"❌ Agent error: {result.get('error')}")
                return False

        print("\n🎉 All MCP agent tests completed!")
        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_mcp_server_connection():
    """Test MCP server connection directly"""
    print("\n🔌 Testing MCP Server Connection")
    print("=" * 30)

    try:
        # Test the MCP server function directly
        sys.path.append(str(project_root / "mcp_servers"))
        from versailles_agent_server import get_versailles_weather_forecast

        from datetime import date
        test_date = date.today().isoformat()

        print(f"📅 Testing with date: {test_date}")
        result = get_versailles_weather_forecast(test_date)

        if result.get("status") == "success":
            print("✅ MCP server working correctly")
            print(f"📍 Location: {result.get('location', {}).get('name')}")
            return True
        else:
            print(f"❌ MCP server error: {result.get('error')}")
            return False

    except Exception as e:
        print(f"❌ MCP server test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🏰 Testing LangGraph Agent + MCP Weather Integration")
    print("=" * 60)

    tests = [
        ("MCP Server Connection", test_mcp_server_connection),
        ("MCP Agent Integration", test_mcp_agent_integration),
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
        print("🎉 All tests passed! LangGraph + MCP integration working!")
        print("💡 The LLM now decides when to call weather tools automatically!")
        return 0
    else:
        print("⚠️  Some tests failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())