#!/usr/bin/env python3
"""
Main entry point for lovethedocs.

This allows the package to be run directly with:
python -m lovethedocs
"""

from lovethedocs.cli.app import app

if __name__ == "__main__":
    app()
