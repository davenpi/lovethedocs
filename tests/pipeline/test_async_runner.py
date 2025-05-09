"""
Tests for lovethedocs.application.pipeline.async_runner
(updated to use UpdateResult rather than the removed safety shim).
"""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Dict

import pytest

from lovethedocs.application.pipeline import async_runner as uut
from lovethedocs.domain.models import SourceModule
from lovethedocs.domain.models.update_result import UpdateResult
from lovethedocs.domain.docstyle.base import DocStyle

STYLE = DocStyle.from_string("numpy")


# ────────────────────────────────────────────────────────────
# Local stand-ins (no shared helpers)
# ────────────────────────────────────────────────────────────
class _DummyFS:
    """In-memory stand-in that discovers modules lazily."""

    def __init__(self, root: Path):
        self.root = root
        self.staged: Dict[Path, str] = {}

    # interface expected by async_runner
    def load_modules(self) -> Dict[Path, str]:
        return {
            p.relative_to(self.root): p.read_text("utf-8")
            for p in self.root.rglob("*.py")
        }

    def stage_file(self, rel_path: Path, code: str) -> None:
        self.staged[rel_path] = code


def _fs_factory(root: Path) -> _DummyFS:  # noqa: D401
    return _DummyFS(root)


# ────────────────────────────────────────────────────────────
# 1. single-file happy path
# ────────────────────────────────────────────────────────────
def test_run_async_single_file_success(tmp_path, patch_progress, patch_summary):
    file_path = tmp_path / "demo.py"
    file_path.write_text("print('x')")

    class FakeUseCase:
        async def run_async(self, modules, *, style, concurrency):
            # exactly one module here
            mod = modules[0]
            yield UpdateResult(mod, mod.code + "\n# updated")

    [fs] = uut.run_async(
        paths=file_path,
        concurrency=2,
        fs_factory=_fs_factory,
        use_case=FakeUseCase(),
        style=STYLE,
    )

    assert fs.staged == {Path("demo.py"): "print('x')\n# updated"}


# ────────────────────────────────────────────────────────────
# 2. directory with one failure
# ────────────────────────────────────────────────────────────
def test_run_async_directory_partial_failure(tmp_path, patch_progress, patch_summary):
    good = tmp_path / "good.py"
    good.write_text("pass")
    bad = tmp_path / "bad.py"
    bad.write_text("boom")

    class FakeUseCase:
        async def run_async(self, modules, *, style, concurrency):
            for mod in modules:
                if mod.path.name == "bad.py":
                    yield UpdateResult(mod, error=RuntimeError("kaboom"))
                else:
                    yield UpdateResult(mod, mod.code + "\n# ok")

    [fs] = uut.run_async(
        paths=[tmp_path],
        concurrency=1,
        fs_factory=_fs_factory,
        use_case=FakeUseCase(),
        style=STYLE,
    )

    assert Path("bad.py") not in fs.staged
    assert fs.staged[Path("good.py")].endswith("# ok")


# ────────────────────────────────────────────────────────────
# 3. non-Python path is ignored
# ────────────────────────────────────────────────────────────
def test_run_async_ignores_non_python(tmp_path, patch_progress, patch_summary):
    junk = tmp_path / "notes.txt"
    junk.write_text("nothing")

    class FakeUseCase:
        async def run_async(self, modules, *, style, concurrency):
            if False:
                yield  # pragma: no cover

    result = uut.run_async(
        paths=junk,
        concurrency=1,
        fs_factory=_fs_factory,
        use_case=FakeUseCase(),
        style=STYLE,
    )
    assert result == []  # runner skips unsupported path


# ────────────────────────────────────────────────────────────
# 4. semaphore limits concurrent coroutines
# ────────────────────────────────────────────────────────────
@pytest.mark.parametrize("concurrency", [1, 2])
def test_semaphore_respected(
    tmp_path, patch_progress, patch_summary, concurrency
):
    # create 5 modules to force overlap
    for i in range(5):
        (tmp_path / f"m{i}.py").write_text("x")

    active = 0
    max_active = 0

    class FakeUseCase:
        async def run_async(self, modules, *, style, concurrency=concurrency):
            sem = asyncio.Semaphore(concurrency)

            async def _job(mod: SourceModule):
                nonlocal active, max_active
                async with sem:
                    active += 1
                    max_active = max(max_active, active)
                    await asyncio.sleep(0)  # let other tasks start
                    active -= 1
                    return UpdateResult(mod, mod.code)

            tasks = [_job(m) for m in modules]
            for coro in asyncio.as_completed(tasks):
                yield await coro

    uut.run_async(
        paths=[tmp_path],
        concurrency=concurrency,
        fs_factory=_fs_factory,
        use_case=FakeUseCase(),
        style=STYLE,
    )

    assert max_active <= concurrency