"""
Central place for tweakable settings.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    """
    Immutable configuration settings for the application.

    Stores tweakable parameters such as the model name and documentation style.
    Instances are immutable due to `frozen=True`.
    """

    model: str = "gpt-4.1"
    doc_style: str = "numpy"
