from pathlib import Path
from typing import Protocol


class FileWriterPort(Protocol):
    """Abstracts disk I/O so tests can inject an in-memory implementation."""

    def load_modules(self, base_path): ...
    def write_file(self, path, code: str, *, root): ...

    # NEW — safe default implementation can raise NotImplementedError
    def backup_file(self, original: Path, root: Path) -> Path: ...


class DiffViewerPort(Protocol):
    """How the UI surfaces a diff.  Keeps any editor/tool details out of app code."""

    def view(self, original: Path, improved: Path) -> None: ...
