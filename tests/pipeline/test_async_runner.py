# tests/pipeline/test_async_runner.py
from pathlib import Path

import pytest

from lovethedocs.application.pipeline import async_runner
from tests.helpers import DummyFS, DummyUseCase


@pytest.fixture
def fs_factory():
    # Return a fresh DummyFS for every project root
    return lambda root: DummyFS(root)


def test_run_async_single_file(tmp_path, patch_progress, patch_summary, fs_factory):
    file_path = tmp_path / "demo.py"
    file_path.write_text("print('x')")

    uc = DummyUseCase()
    [fs] = async_runner.run_async(
        paths=file_path,
        concurrency=2,
        fs_factory=fs_factory,
        use_case=uc,
    )

    assert Path("demo.py") in fs.staged
    assert fs.staged[Path("demo.py")].endswith("# updated")


def test_run_async_directory(tmp_path, patch_progress, patch_summary, fs_factory):
    pkg = tmp_path / "pkg"
    pkg.mkdir()
    (pkg / "a.py").write_text("pass")

    uc = DummyUseCase()
    [fs] = async_runner.run_async(
        paths=[pkg],
        concurrency=1,
        fs_factory=fs_factory,
        use_case=uc,
    )

    # DummyFS.load_modules always returns exactly one file,
    # so we expect one staged file after the run.
    assert len(fs.staged) == 1
    staged_path = next(iter(fs.staged))
    assert staged_path.suffix == ".py"
    assert fs.staged[staged_path].endswith("# updated")
