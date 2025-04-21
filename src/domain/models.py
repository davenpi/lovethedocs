"""
Pure data representations used across the project.
These are placeholders—expand as needed in later phases.
"""

from dataclasses import dataclass


@dataclass
class ModuleEdit:
    path: str  # "src/foo.py"
    updated_code: str  # full file contents with new docstrings
