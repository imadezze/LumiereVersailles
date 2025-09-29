"""
Configuration settings for the Versailles Weather Agent
"""
import os
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

# Base paths
AGENTS_DIR = Path(__file__).parent.parent
PROMPTS_DIR = AGENTS_DIR / "prompts"

# Model configuration
OPENAI_CONFIG = {
    "model": os.getenv("OPENAI_MODEL", "gpt-4"),
    "api_key": os.getenv("OPENAI_API_KEY"),
    "temperature": float(os.getenv("OPENAI_TEMPERATURE", "0.1")),
    "max_tokens": int(os.getenv("OPENAI_MAX_TOKENS", "1000")),
}

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
    "weather_tool": PROMPTS_DIR / "weather_tool_prompt.md",
    "user_interaction": PROMPTS_DIR / "user_interaction_prompt.md",
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
        "weather_api_key": bool(WEATHER_CONFIG["api_key"]),
        "prompts_exist": all(p.exists() for p in PROMPT_FILES.values()),
    }
    return validation

def get_full_system_prompt() -> str:
    """Get the complete system prompt with all instructions"""
    prompts = []

    # Load main system prompt
    prompts.append(load_prompt("system"))

    # Add weather tool instructions
    prompts.append("\n## Weather Tool Instructions")
    prompts.append(load_prompt("weather_tool"))

    # Add user interaction guidelines
    prompts.append("\n## User Interaction Guidelines")
    prompts.append(load_prompt("user_interaction"))

    return "\n".join(prompts)