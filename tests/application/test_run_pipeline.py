from pathlib import Path

import pytest

from lovethedocs.application.run_pipeline import run_pipeline


# --------------------------------------------------------------------------- #
#  Test doubles                                                               #
# --------------------------------------------------------------------------- #
class StubUseCase:
    """Simply returns the original code unchanged."""

    def run(self, modules, *, style):
        for mod in modules:
            yield mod, mod.code


class StubFileSystem:
    """
    In-memory replacement for ProjectFileSystem.

    Attributes
    ----------
    root     : project root passed by `run_pipeline`
    loaded   : directory on which `load_modules()` was invoked (or None)
    staged   : {Path -> str} mapping of every call to `stage_file()`
    """

    instances: list["StubFileSystem"] = []

    def __init__(self, root):
        self.root = Path(root)
        self.loaded: Path | None = None
        self.staged: dict[Path, str] = {}
        StubFileSystem.instances.append(self)

    # -- directory branch ---------------------------------------------------
    def load_modules(self):
        self.loaded = self.root
        # pretend each package contains a single foo.py
        return {Path("foo.py"): "def foo():\n    pass\n"}

    # -- writer used by both branches --------------------------------------
    def stage_file(self, rel_path, code):
        self.staged[Path(rel_path)] = code


# --------------------------------------------------------------------------- #
#  Fixtures                                                                   #
# --------------------------------------------------------------------------- #
@pytest.fixture(autouse=True)
def clear_stub_instances():
    """Ensure each test starts with a fresh slate."""
    StubFileSystem.instances.clear()
    yield
    StubFileSystem.instances.clear()


# --------------------------------------------------------------------------- #
#  Tests                                                                      #
# --------------------------------------------------------------------------- #
def test_run_pipeline_happy_path(tmp_path):
    run_pipeline(
        paths=[tmp_path],
        fs_factory=StubFileSystem,
        use_case=StubUseCase(),
    )

    fs = StubFileSystem.instances[0]
    assert fs.loaded == tmp_path  # directory was traversed
    assert Path("foo.py") in fs.staged  # file was staged
    assert fs.staged[Path("foo.py")].startswith("def foo()")


def test_run_pipeline_single_python_file(tmp_path):
    file_path = tmp_path / "solo.py"
    file_path.write_text("def solo():\n    pass\n", encoding="utf-8")

    run_pipeline(
        paths=file_path,
        fs_factory=StubFileSystem,
        use_case=StubUseCase(),
    )

    fs = StubFileSystem.instances[0]
    assert Path("solo.py") in fs.staged
    assert "def solo" in fs.staged[Path("solo.py")]


def test_run_pipeline_mixed_inputs(tmp_path):
    # ---- create a package --------------------------------------------------
    pkg_dir = tmp_path / "mypkg"
    pkg_dir.mkdir()
    (pkg_dir / "__init__.py").write_text("", encoding="utf-8")
    (pkg_dir / "foo.py").write_text("def foo():\n    pass\n", encoding="utf-8")

    # ---- single file -------------------------------------------------------
    bar_file = tmp_path / "bar.py"
    bar_file.write_text("def bar():\n    pass\n", encoding="utf-8")

    run_pipeline(
        paths=[pkg_dir, bar_file],
        fs_factory=StubFileSystem,
        use_case=StubUseCase(),
    )

    # one StubFileSystem per project root
    dirs_loaded = [fs.loaded for fs in StubFileSystem.instances if fs.loaded]
    assert pkg_dir in dirs_loaded  # directory branch hit

    all_staged: dict[Path, str] = {}
    for fs in StubFileSystem.instances:
        all_staged.update(fs.staged)

    assert any(p.name == "foo.py" for p in all_staged)  # from dir walk
    assert any(p.name == "bar.py" for p in all_staged)  # from single file
