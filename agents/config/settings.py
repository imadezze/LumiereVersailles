"""
Configuration settings for the Versailles Weather Agent
"""
import os
from pathlib import Path
from typing import Dict, Any
from datetime import date
from dotenv import load_dotenv

load_dotenv()

# Base paths
AGENTS_DIR = Path(__file__).parent.parent
PROMPTS_DIR = AGENTS_DIR / "prompts"

# LLM Provider configuration
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai").lower()  # "openai" or "mistral"

# Model configuration
OPENAI_CONFIG = {
    "model": os.getenv("OPENAI_MODEL", "gpt-4"),
    "api_key": os.getenv("OPENAI_API_KEY"),
    "temperature": float(os.getenv("OPENAI_TEMPERATURE", "0.1")),
}

# Mistral AI configuration
MISTRAL_CONFIG = {
    "model": os.getenv("MISTRAL_MODEL", "mistral-medium-2508"),
    "api_key": os.getenv("MISTRAL_API_KEY"),
    "temperature": float(os.getenv("MISTRAL_TEMPERATURE", "0.1")),
}

def get_llm_config():
    """Get the appropriate LLM configuration based on environment settings"""
    if LLM_PROVIDER == "mistral":
        return "mistral", MISTRAL_CONFIG
    else:  # default to openai
        return "openai", OPENAI_CONFIG

# Agent configuration
AGENT_CONFIG = {
    "name": "versailles_weather_agent",
    "description": "Weather assistant for Palace of Versailles visits",
    "max_iterations": int(os.getenv("AGENT_MAX_ITERATIONS", "5")),
    "timeout": int(os.getenv("AGENT_TIMEOUT", "30")),
}

# Prompt file paths
PROMPT_FILES = {
    "system": PROMPTS_DIR / "system_prompt.md",
    "system_apitest": PROMPTS_DIR / "system_prompt_apitest.md",
    "weather_tool": PROMPTS_DIR / "weather_tool_prompt.md",
    "travel_tool": PROMPTS_DIR / "travel_tool_prompt.md",
    "rag_tool": PROMPTS_DIR / "rag_tool_prompt.md",
    "web_search_tool": PROMPTS_DIR / "web_search_tool_prompt.md",
    "useful_information": PROMPTS_DIR / "useful_information_prompt.md",
    "user_interaction": PROMPTS_DIR / "user_interaction_prompt.md",
    "itinerary_preparation": PROMPTS_DIR / "itinerary_preparation_prompt.md",
}

# Weather API configuration
WEATHER_CONFIG = {
    "api_key": os.getenv("OPENWEATHER_API_KEY"),
    "base_url": "https://api.openweathermap.org/data/2.5",
    "timeout": int(os.getenv("WEATHER_TIMEOUT", "10")),
}

def load_prompt(prompt_name: str) -> str:
    """Load a prompt from file"""
    if prompt_name not in PROMPT_FILES:
        raise ValueError(f"Unknown prompt: {prompt_name}")

    prompt_file = PROMPT_FILES[prompt_name]
    if not prompt_file.exists():
        raise FileNotFoundError(f"Prompt file not found: {prompt_file}")

    return prompt_file.read_text(encoding="utf-8")

def validate_config() -> Dict[str, bool]:
    """Validate configuration settings"""
    validation = {
        "openai_api_key": bool(OPENAI_CONFIG["api_key"]),
        "mistral_api_key": bool(MISTRAL_CONFIG["api_key"]),
        "weather_api_key": bool(WEATHER_CONFIG["api_key"]),
        "prompts_exist": all(p.exists() for p in PROMPT_FILES.values()),
    }
    return validation

def get_full_system_prompt() -> str:
    """Get the complete system prompt with all instructions

    Checks for system_prompt_apitest.md first:
    - If exists: API test mode (one-shot, no additional questions)
    - If not: Normal mode with itinerary preparation guidelines
    """
    from datetime import timedelta

    prompts = []

    # Get current date and related dates
    today = date.today()
    tomorrow = today + timedelta(days=1)

    # Calculate next weekend (Saturday-Sunday)
    # weekday() returns 0=Monday, 1=Tuesday, ..., 6=Sunday
    days_until_saturday = (5 - today.weekday()) % 7
    if days_until_saturday == 0:
        # Today is Saturday, so "this weekend" is today and tomorrow
        next_saturday = today
    else:
        # Calculate next Saturday
        next_saturday = today + timedelta(days=days_until_saturday if days_until_saturday > 0 else 7)

    next_sunday = next_saturday + timedelta(days=1)

    current_date_formatted = today.strftime("%B %d, %Y")  # e.g., "September 30, 2025"
    current_day_of_week = today.strftime("%A")  # e.g., "Tuesday"
    tomorrow_date_formatted = tomorrow.strftime("%Y-%m-%d")  # e.g., "2025-10-01"
    next_weekend_dates = f"{next_saturday.strftime('%B %d')} - {next_sunday.strftime('%B %d, %Y')}"  # e.g., "October 4 - October 5, 2025"
    next_weekend_formatted = f"{next_saturday.strftime('%Y-%m-%d')} and {next_sunday.strftime('%Y-%m-%d')}"  # e.g., "2025-10-04 and 2025-10-05"

    # Check if API test mode is enabled
    api_test_mode = PROMPT_FILES["system_apitest"].exists()

    if api_test_mode:
        # API TEST MODE: Load apitest prompt (one-shot, no questions)
        print("🔬 API TEST MODE: Using system_prompt_apitest.md")
        system_prompt = load_prompt("system_apitest")
    else:
        # NORMAL MODE: Load standard prompt
        print("💬 NORMAL MODE: Using system_prompt.md with itinerary preparation")
        system_prompt = load_prompt("system")

    # Inject dynamic dates
    system_prompt = system_prompt.replace("{current_date}", current_date_formatted)
    system_prompt = system_prompt.replace("{current_day_of_week}", current_day_of_week)
    system_prompt = system_prompt.replace("{tomorrow_date}", tomorrow_date_formatted)
    system_prompt = system_prompt.replace("{next_weekend_dates}", next_weekend_dates)
    system_prompt = system_prompt.replace("{next_weekend_formatted}", next_weekend_formatted)
    prompts.append(system_prompt)

    # Add practical information FIRST - authoritative reference data
    try:
        prompts.append("\n## Practical Information & Visit Tips")
        prompts.append("\n**IMPORTANT: This section contains exact, authoritative information. Always check here FIRST for practical questions (hours, tickets, tips) before using tools.**\n")
        prompts.append(load_prompt("useful_information"))
    except FileNotFoundError:
        pass

    # Add tool instructions
    prompts.append("\n## Available Tools")

    # Knowledge base search tool (if available)
    try:
        prompts.append("\n### Knowledge Base Search")
        prompts.append(load_prompt("rag_tool"))
    except FileNotFoundError:
        pass

    # Web search tool (if available)
    try:
        prompts.append("\n### Web Search")
        web_search_prompt = load_prompt("web_search_tool")
        web_search_prompt = web_search_prompt.replace("{current_date}", current_date_formatted)
        web_search_prompt = web_search_prompt.replace("{next_weekend_dates}", next_weekend_dates)
        prompts.append(web_search_prompt)
    except FileNotFoundError:
        pass

    # Weather tool
    prompts.append("\n### Weather Information")
    prompts.append(load_prompt("weather_tool"))

    # Travel time tool (if available)
    try:
        prompts.append("\n### Travel Time Calculation")
        prompts.append(load_prompt("travel_tool"))
    except FileNotFoundError:
        pass

    # Add user interaction guidelines
    prompts.append("\n## User Interaction Guidelines")
    prompts.append(load_prompt("user_interaction"))

    # Add itinerary preparation guidelines (ONLY in normal mode)
    if not api_test_mode:
        try:
            prompts.append("\n## Itinerary Preparation Guidelines")
            prompts.append(load_prompt("itinerary_preparation"))
        except FileNotFoundError:
            pass

    return "\n".join(prompts)