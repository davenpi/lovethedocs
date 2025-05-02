"""
LoveTheDocs: Enhance Python docs with AI

Make your code more understandable, maintainable, and useful with
AI-generated documentation.
"""

__version__ = "0.1.0"

# Expose the app directly
from lovethedocs.cli.app import app as cli

__all__ = ["cli"]
