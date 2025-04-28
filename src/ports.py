from typing import Protocol


class AIClientPort(Protocol):
    """Turn a prompt into the model's JSON response."""

    def request(self, source_prompt: str, *, model: str) -> dict: ...


class FileWriterPort(Protocol):
    """Abstracts disk I/O so tests can inject an in-memory implementation."""

    def load_modules(self, base_path): ...
    def write_file(self, path, code: str, *, root): ...
