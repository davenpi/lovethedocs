from pathlib import Path

from lovethedocs.gateways.project_file_system import ProjectFileSystem


def fs_factory(root: Path) -> ProjectFileSystem:
    """
    Create a `ProjectFileSystem` instance for the specified root directory.

    Parameters
    ----------
    root : Path
        The root directory for the project file system.

    Returns
    -------
    ProjectFileSystem
        An instance of `ProjectFileSystem` rooted at the given directory.
    """

    return ProjectFileSystem(root)
