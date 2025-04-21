"""
Pure data representations used across the project.
These are placeholders—expand as needed in later phases.
"""

from dataclasses import dataclass


@dataclass
class ModuleEdit:
    path: str  # "src/foo.py"
    updated_code: str  # TODO: make more clear. Is this docstring or signature? Both?
