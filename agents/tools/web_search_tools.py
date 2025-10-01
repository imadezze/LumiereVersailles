"""
Web search tools for the Versailles Agent using LinkUp Search
"""
import os
import re
from typing import Dict, Any, List
from langchain_core.tools import tool

# Try to import LinkUp, handle gracefully if not installed
try:
    from langchain_linkup import LinkupSearchTool
    LINKUP_AVAILABLE = True
except ImportError:
    print("⚠️ LinkUp Search not available. Install with: pip install langchain-linkup")
    LINKUP_AVAILABLE = False


def clean_text(text: str) -> str:
    """Clean up HTML and formatting from text"""
    if not text:
        return ""

    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Remove URLs in markdown format
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    # Clean up
    text = text.strip()

    return text


@tool
def search_web_for_versailles_info(query: str) -> str:
    """
    Search the web for current information about Versailles using LinkUp Search.

    Use this tool to find up-to-date information about:
    - Current events and exhibitions at Versailles
    - Recent news about the palace
    - Updated opening hours or special closures
    - New ticket information or special offers
    - Upcoming shows and performances

    This tool searches the web in real-time and provides an AI-synthesized answer with sources.

    Args:
        query: Natural language search query (e.g., "special events at Versailles this weekend")

    Returns:
        String containing an AI-synthesized answer based on current web information,
        followed by source citations with URLs

    Example:
        >>> search_web_for_versailles_info("special events at Versailles this summer")
        🔍 Web Search Answer:

        The Musical Fountain Shows take place every weekend from April to October 2025...

        📚 Sources:
        1. Musical Fountains 2025 - https://en.chateauversailles.fr/...
        2. Summer Exhibitions - https://en.chateauversailles.fr/...
    """
    if not LINKUP_AVAILABLE:
        return "❌ Web search is not available. Please install langchain-linkup: pip install langchain-linkup"

    # Check for LINKUP_API_KEY
    api_key = os.getenv("LINKUP_API_KEY")
    if not api_key:
        return "❌ Web search is not available. Please set LINKUP_API_KEY in your .env file.\nGet your API key at: https://app.linkup.so/sign-up"

    try:
        # Initialize LinkUp search tool with sourcedAnswer output type
        search_tool = LinkupSearchTool(
            linkup_api_key=api_key,
            depth="deep",  # Use deep search for better quality
            output_type="sourcedAnswer"  # Get AI-synthesized answer with sources
        )

        # Perform search
        print(f"🔍 Searching web with LinkUp for: {query}")

        # Call LinkUp search
        search_response = search_tool.invoke({"query": query})

        print(f"🔍 DEBUG: Response type: {type(search_response)}")

        # Parse the response - LinkUp returns a LinkupSourcedAnswer object
        # Extract answer and sources attributes directly

        if isinstance(search_response, str):
            # If it's already a formatted string, return it
            return f"🔍 Web Search Results:\n\n{search_response}"

        # Extract answer and sources from LinkupSourcedAnswer object
        if hasattr(search_response, 'answer') and hasattr(search_response, 'sources'):
            answer = search_response.answer
            sources = search_response.sources
        elif isinstance(search_response, dict):
            # Fallback for dict format
            answer = search_response.get("answer", "")
            sources = search_response.get("sources", [])
        else:
            # Unknown format
            print(f"❌ Unexpected response format: {type(search_response)}")
            return f"🔍 Web Search Results:\n\n{str(search_response)}"

        if not answer:
            print(f"❌ No answer found for: {query}")
            return f"No web search answer found for: {query}"

        # Format the output with answer and sources
        formatted_output = f"🔍 Web Search Answer:\n\n{answer}\n\n"

        # Add sources if available (name and URL only, no snippets)
        # LIMIT TO FIRST 3 SOURCES to reduce token usage
        if sources and len(sources) > 0:
            formatted_output += "📚 Sources:\n"
            # Only include first 3 sources
            sources_to_show = sources[:3]
            for i, source in enumerate(sources_to_show, 1):
                # Handle both object attributes and dict keys
                name = getattr(source, 'name', None) or source.get("name", "Unknown source") if isinstance(source, dict) else source.name
                url = getattr(source, 'url', None) or source.get("url", "") if isinstance(source, dict) else source.url

                formatted_output += f"\n{i}. **{name}**\n"
                if url:
                    formatted_output += f"   URL: {url}\n"

        print(f"✅ Found answer with {len(sources)} sources (showing first 3 to LLM)")
        print(f"\n📤 FULL OUTPUT PASSING TO LLM ({len(formatted_output)} chars):")
        print("=" * 100)
        print(formatted_output)
        print("=" * 100)
        return formatted_output

    except Exception as e:
        print(f"❌ Error performing web search: {str(e)}")
        return f"❌ Error performing web search: {str(e)}"


def get_all_web_search_tools():
    """Get all available web search tools for the agent"""
    if not LINKUP_AVAILABLE:
        print("⚠️ LinkUp Search not available - web search tools disabled")
        return []

    api_key = os.getenv("LINKUP_API_KEY")
    if not api_key:
        print("⚠️ LINKUP_API_KEY not found - web search tools disabled")
        return []

    return [search_web_for_versailles_info]


def initialize_web_search():
    """Initialize and check web search availability"""
    if not LINKUP_AVAILABLE:
        print("⚠️ Web search not available: langchain-linkup not installed")
        return False

    api_key = os.getenv("LINKUP_API_KEY")
    if not api_key:
        print("⚠️ Web search not available: LINKUP_API_KEY not set")
        return False

    print("✅ Web search initialized (LinkUp)")
    return True