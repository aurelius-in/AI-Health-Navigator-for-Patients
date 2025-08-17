"""
AI Health Navigator - Advanced AI-powered health navigation platform.

This package provides intelligent triage, provider matching, and personalized
care recommendations using cutting-edge AI technologies.
"""

__version__ = "1.0.0"
__author__ = "AI Health Navigator Team"
__email__ = "team@aihealthnavigator.com"

from .core.config import settings
from .core.logging import get_logger

__all__ = ["settings", "get_logger"]
