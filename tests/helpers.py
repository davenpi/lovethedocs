"""
Lightweight test doubles shared across the suite.
"""

from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path

from lovethedocs.domain import docstyle
from lovethedocs.domain.models import SourceModule

# Re-use the same style everywhere
STYLE = docstyle.DocStyle.from_string("numpy")


class DummyUseCase:
    """
    Pretends to be DocumentationUpdateUseCase.
    Set `should_fail=True` to force an exception.
    """

    def __init__(self, *, should_fail: bool = False):
        self.should_fail = should_fail
        self.calls: list[SourceModule] = []

    # ----- sync path --------------------------------------------------------
    def run(self, modules, *, style):
        self.calls.extend(modules)
        if self.should_fail:
            raise ValueError("boom")
        return [(m, m.code + "\n# updated") for m in modules]

    # ----- async path -------------------------------------------------------
    async def run_async(self, modules, *, style, concurrency):
        self.calls.extend(modules)
        for m in modules:
            if self.should_fail:
                raise RuntimeError("async-boom")
            yield m, m.code + "\n# updated"


class DummyFS:
    """In-memory stand-in for ProjectFileSystem."""

    def __init__(self, root: Path):
        self.root = root
        self.staged: dict[Path, str] = {}

    def load_modules(self):
        # pretend every project has a single module
        path = Path("foo.py")
        return {path: "print('hi')"}

    def stage_file(self, path: Path, code: str):
        self.staged[path] = code


@contextmanager
def silent_progress():
    """No-op replacement for rich progress bars."""

    class _P:
        def add_task(self, *_, **__):
            return None

        def advance(self, *_):
            pass

    yield _P()
