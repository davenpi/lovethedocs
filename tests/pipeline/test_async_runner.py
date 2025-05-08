"""
Tests for lovethedocs.application.pipeline.async_runner
(no external helpers required).
"""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Dict

import pytest

from lovethedocs.application.pipeline import async_runner as uut


# ────────────────────────────────────────────────────────────
# Local stand-ins (no shared helpers)
# ────────────────────────────────────────────────────────────
class _DummyFS:
    """In-memory stand-in that discovers modules lazily."""

    def __init__(self, root: Path):
        self.root = root
        self.staged: Dict[Path, str] = {}

    # ----- interface expected by async_runner -----------------------------
    def load_modules(self) -> Dict[Path, str]:
        modules = {
            p.relative_to(self.root): p.read_text("utf-8")
            for p in self.root.rglob("*.py")
        }
        # still return *something* so runner metrics don’t explode
        return modules or {Path("foo.py"): "print('hi')"}

    def stage_file(self, rel_path: Path, code: str) -> None:
        self.staged[rel_path] = code


def _fs_factory(root: Path) -> _DummyFS:  # noqa: D401
    return _DummyFS(root)


# ────────────────────────────────────────────────────────────
# 1. single-file happy path
# ────────────────────────────────────────────────────────────
def test_run_async_single_file_success(
    tmp_path, patch_progress, patch_summary, monkeypatch
):
    file_path = tmp_path / "demo.py"
    file_path.write_text("print('x')")

    async def stub_safe_update(use_case, mod, *, style, sem):
        # succeed indiscriminately
        return mod, mod.code + "\n# updated", None

    monkeypatch.setattr(uut, "safe_update_async", stub_safe_update)

    [fs] = uut.run_async(
        paths=file_path,
        concurrency=2,
        fs_factory=_fs_factory,
        use_case=object(),  # not used by stub
    )

    assert fs.staged == {Path("demo.py"): "print('x')\n# updated"}


# ────────────────────────────────────────────────────────────
# 2. directory with one failure
# ────────────────────────────────────────────────────────────
def test_run_async_directory_partial_failure(
    tmp_path, patch_progress, patch_summary, monkeypatch
):
    (tmp_path / "good.py").write_text("pass")
    (tmp_path / "bad.py").write_text("boom")

    async def stub_safe_update(use_case, mod, *, style, sem):
        if mod.path.name == "bad.py":
            return mod, None, RuntimeError("kaboom")
        return mod, mod.code + "\n# ok", None

    monkeypatch.setattr(uut, "safe_update_async", stub_safe_update)

    [fs] = uut.run_async(
        paths=[tmp_path],
        concurrency=1,
        fs_factory=_fs_factory,
        use_case=None,
    )

    assert Path("bad.py") not in fs.staged
    print("fs.staged", fs.staged)
    assert fs.staged[Path("good.py")].endswith("# ok")


# ────────────────────────────────────────────────────────────
# 3. non-Python path is ignored
# ────────────────────────────────────────────────────────────
def test_run_async_ignores_non_python(
    tmp_path, patch_progress, patch_summary, monkeypatch
):
    junk = tmp_path / "notes.txt"
    junk.write_text("nothing")

    monkeypatch.setattr(uut, "safe_update_async", lambda *a, **k: None)

    result = uut.run_async(
        paths=junk,
        concurrency=1,
        fs_factory=_fs_factory,
        use_case=None,
    )
    assert result == []  # runner skips unsupported path


# ────────────────────────────────────────────────────────────
# 4. semaphore limits concurrent coroutines
# ────────────────────────────────────────────────────────────
@pytest.mark.parametrize("concurrency", [1, 2])
def test_semaphore_respected(
    tmp_path, patch_progress, patch_summary, monkeypatch, concurrency
):
    # 5 modules to force overlap
    for i in range(5):
        (tmp_path / f"m{i}.py").write_text("x")

    active = 0
    max_active = 0

    async def stub_safe_update(use_case, mod, *, style, sem):
        nonlocal active, max_active
        async with sem:  # honour the runner’s semaphore
            active += 1
            max_active = max(max_active, active)
            # yield control to let other tasks start
            await asyncio.sleep(0)
            active -= 1
            return mod, mod.code, None

    monkeypatch.setattr(uut, "safe_update_async", stub_safe_update)

    uut.run_async(
        paths=[tmp_path],
        concurrency=concurrency,
        fs_factory=_fs_factory,
        use_case=None,
    )

    assert max_active <= concurrency
