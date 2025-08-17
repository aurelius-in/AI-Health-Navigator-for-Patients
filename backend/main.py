#!/usr/bin/env python3
"""
Main entry point for AI Health Navigator Backend.

This module serves as the main entry point for the backend application,
providing a command-line interface and server startup functionality.
"""

import sys
import os
import asyncio
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from ai_health_navigator.cli import cli
from ai_health_navigator.core.logging import get_logger

logger = get_logger(__name__)


def main():
    """Main entry point for the application."""
    try:
        # Set up logging
        logger.info("Starting AI Health Navigator Backend")
        
        # Run the CLI
        cli()
        
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Application failed to start: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
