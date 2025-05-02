from pathlib import Path
from typing import Protocol


class FileSystemPort(Protocol):
    """
    All paths are pathlib.Path **relative to the project root**
    and the instance is created once with that root.
    """

    # ----- read ------------------------------------------------------------ #
    def load_modules(self) -> dict[Path, str]: ...

    # ----- write ----------------------------------------------------------- #
    def stage_file(self, rel_path: Path, code: str) -> None:
        # writes to <root>/_improved/…
        ...

    def apply_stage(self, rel_path: Path) -> None:
        # backup original → <root>/_backups/…
        # copy staged file over original
        ...

    # ----- helpers --------------------------------------------------------- #
    def original_path(self, rel_path: Path) -> Path: ...
    def staged_path(self, rel_path: Path) -> Path: ...
    def backup_path(self, rel_path: Path) -> Path: ...


class DiffViewerPort(Protocol):
    """How the UI surfaces a diff. Keeps any editor/tool details out of app code."""

    def view(self, original: Path, improved: Path) -> None: ...
