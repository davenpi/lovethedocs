import textwrap
import tempfile
from pathlib import Path

import pytest
from src.gateways.project_file_system import ProjectFileSystem


def _write(p: Path, content: str):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(textwrap.dedent(content))


# ---------- load_modules ------------------------------------------------- #
def test_load_modules_basic_and_relative_paths():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _write(root / "pkg" / "alpha.py", "x = 1\n")
        _write(root / "pkg" / "__init__.py", "# ignored\n")

        fs = ProjectFileSystem(root)
        modules = fs.load_modules()

        assert modules == {Path("pkg/alpha.py"): "x = 1\n"}


def test_load_modules_ignores_virtualenv_dirs():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _write(root / "venv" / "lib" / "ignored.py", "x=99\n")
        _write(root / "beta.py", "y = 2\n")

        fs = ProjectFileSystem(root)
        modules = fs.load_modules()

        assert Path("beta.py") in modules
        assert all("venv" not in p.parts for p in modules)  # path.parts not str


def test_load_modules_preserves_blank_lines_and_unicode():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        code = "\n\na = '✓'\n\n"
        _write(root / "naïve.py", code)

        fs = ProjectFileSystem(root)
        modules = fs.load_modules()

        assert modules[Path("naïve.py")] == code  # exact match


# ---------- stage_file --------------------------------------------------- #
def test_stage_file_relative_explicit_root():
    with tempfile.TemporaryDirectory() as tmp:
        project_root = Path(tmp) / "repo"
        (project_root / "src").mkdir(parents=True)

        rel_path = Path("src/alpha.py")
        code = "print('hello')"

        fs = ProjectFileSystem(project_root)
        fs.stage_file(rel_path, code)

        dest = fs.staged_path(rel_path)
        improved_root = project_root / "_improved"
        assert dest == (improved_root.resolve()) / rel_path
        assert dest.is_file()
        assert dest.read_text(encoding="utf-8") == code


def test_stage_file_absolute_path_raises():
    with tempfile.TemporaryDirectory() as tmp:
        project_root = Path(tmp) / "repo"
        project_root.mkdir()

        abs_path = (project_root / "elsewhere.py").resolve()
        fs = ProjectFileSystem(project_root)

        with pytest.raises(ValueError):
            fs.stage_file(abs_path, "pass")
