from typing import Protocol


class FileWriterPort(Protocol):
    """Abstracts disk I/O so tests can inject an in-memory implementation."""

    def load_modules(self, base_path): ...
    def write_file(self, path, code: str, *, root): ...
