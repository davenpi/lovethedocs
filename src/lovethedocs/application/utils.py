"""
Small helpers that aren't worth their own module yet.
"""

from pathlib import Path

from lovethedocs.gateways.project_file_system import ProjectFileSystem


def fs_factory(root: Path) -> ProjectFileSystem:
    """Create a `ProjectFileSystem` instance for the specified root directory."""

    return ProjectFileSystem(root)
