"""
Versailles Weather Agent Package

This package contains a LangGraph-based weather agent for the Palace of Versailles
that provides weather forecasts and visit planning assistance.

Main components:
- core: Agent logic and LangGraph workflow
- tools: Weather-related tools and integrations
- config: Configuration management and prompt loading
- prompts: External prompt files for system instructions
"""

from .core import SimplifiedVersaillesAgent

__version__ = "1.0.0"
__all__ = ["SimplifiedVersaillesAgent"]