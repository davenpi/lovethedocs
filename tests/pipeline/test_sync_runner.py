from pathlib import Path

from lovethedocs.application.pipeline import sync_runner as uut
from lovethedocs.domain.docstyle.base import DocStyle
from lovethedocs.domain.models.update_result import UpdateResult

STYLE = DocStyle.from_string("numpy")


# ────────────────────────────────────
# Helpers / fakes
# ────────────────────────────────────
class FakeFS:
    """Captures staged files and lets us stub `load_modules`."""

    def __init__(self, root: Path, modules=None):
        self.root = root
        self._modules = modules or {}
        self.staged: dict[Path, str] = {}

    def load_modules(self):
        return self._modules  # mapping[Path, str]

    def stage_file(self, rel_path: Path, new_code: str):
        self.staged[rel_path] = new_code


# ────────────────────────────────────
# 1. single-file happy path
# ────────────────────────────────────
def test_run_sync_single_file_success(tmp_path, patch_progress, patch_summary):
    file_path = tmp_path / "hello.py"
    file_path.write_text("print('hi')", encoding="utf-8")

    fake_fs = FakeFS(tmp_path)

    def fs_factory(root):  # noqa: D401
        return fake_fs

    class FakeUseCase:
        def run(self, modules, *, style):
            mod = modules[0]
            yield UpdateResult(mod, "print('updated')")

    fses = uut.run_sync(
        paths=file_path, fs_factory=fs_factory, use_case=FakeUseCase(), style=STYLE
    )

    assert fses == [fake_fs]
    assert fake_fs.staged == {Path("hello.py"): "print('updated')"}


# ────────────────────────────────────
# 2. directory with mixed success / failure
# ────────────────────────────────────
def test_run_sync_directory_partial_failure(tmp_path, patch_progress, patch_summary):
    a = tmp_path / "a.py"
    a.write_text("a=1")
    b = tmp_path / "b.py"
    b.write_text("b=2")

    modules_map = {Path("a.py"): "a=1", Path("b.py"): "b=2"}
    fake_fs = FakeFS(tmp_path, modules=modules_map)
    fs_factory = lambda root: fake_fs

    class FakeUseCase:
        def run(self, modules, *, style):
            for mod in modules:
                if mod.path.name == "a.py":
                    yield UpdateResult(mod, "a=42")
                else:
                    yield UpdateResult(mod, error=RuntimeError("boom"))

    fses = uut.run_sync(
        paths=[tmp_path], fs_factory=fs_factory, use_case=FakeUseCase(), style=STYLE
    )

    assert fses == [fake_fs]
    assert fake_fs.staged == {Path("a.py"): "a=42"}  # only the good one


# ────────────────────────────────────
# 3. unsupported path is ignored
# ────────────────────────────────────
def test_run_sync_ignores_non_python_files(tmp_path, patch_progress, patch_summary):
    notes = tmp_path / "notes.txt"
    notes.write_text("deep philosophy")

    fake_fs = FakeFS(tmp_path)
    fs_factory = lambda root: fake_fs

    class FakeUseCase:
        def run(self, modules, *, style):
            if False:  # pragma: no cover
                yield  # never reached

    fses = uut.run_sync(
        paths=notes, fs_factory=fs_factory, use_case=FakeUseCase(), style=STYLE
    )
    assert fses == []  # nothing processed, nothing returned
