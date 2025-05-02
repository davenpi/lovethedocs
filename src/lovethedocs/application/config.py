"""
Central place for tweakable settings.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    """
    Immutable configuration settings for the application.

    This dataclass holds tweakable parameters such as the model name used throughout the
    application. Instances are immutable due to the `frozen=True` parameter.
    """

    model: str = "gpt-4.1"
    doc_style: str = "numpy"
