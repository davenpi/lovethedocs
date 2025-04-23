"""
Central place for tweakable settings.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    model_name: str = "gpt-4o-mini"
