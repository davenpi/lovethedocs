import textwrap
import tempfile
from pathlib import Path

import pytest
from src.gateways.file_system import load_modules, write_file


def _write(p: Path, content: str):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(textwrap.dedent(content))


def test_load_modules_basic_and_relative_paths():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _write(root / "pkg" / "alpha.py", "x = 1\n")
        _write(root / "pkg" / "__init__.py", "# should be ignored\n")

        modules = load_modules(root)

        # Only alpha.py should be present and path must be relative
        assert modules == {"pkg/alpha.py": "x = 1\n"}


def test_load_modules_ignores_virtualenv_dirs():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _write(root / "venv" / "lib" / "ignored.py", "x=99\n")
        _write(root / "beta.py", "y = 2\n")

        modules = load_modules(root)

        assert "beta.py" in modules
        assert all("venv/" not in p for p in modules)


def test_load_modules_preserves_blank_lines_and_unicode():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        # Module has leading + trailing blank lines and a Unicode filename
        code = "\n\na = '✓'\n\n"
        _write(root / "naïve.py", code)

        modules = load_modules(root)

        assert modules["naïve.py"] == code  # exact match, no .strip()


def test_write_file_relative_explicit_root():
    with tempfile.TemporaryDirectory() as tmp:
        project_root = Path(tmp) / "repo"
        (project_root / "src").mkdir(parents=True)

        source = Path("src/alpha.py")  # relative path
        code = "print('hello')"  # no trailing newline

        write_file(source, code, root=project_root)

        dest = project_root / "_improved" / source
        assert dest.is_file(), "destination file should exist"
        assert (
            dest.read_text(encoding="utf-8") == code + "\n"
        ), "file should end with exactly one newline"


def test_write_file_absolute_under_root():
    with tempfile.TemporaryDirectory() as tmp:
        project_root = Path(tmp) / "repo"
        source_file = project_root / "pkg" / "beta.py"
        source_file.parent.mkdir(parents=True, exist_ok=True)

        code = "x = 1\n\n"  # two trailing newlines
        source_file.write_text(code)

        write_file(source_file, code, root=project_root)

        dest = project_root / "_improved" / "pkg" / "beta.py"
        assert (
            dest.read_text() == "x = 1\n"
        ), "write_file should collapse multiple newlines to one"


def test_write_file_absolute_outside_root_raises():
    with tempfile.TemporaryDirectory() as tmp:
        project_root = Path(tmp) / "repo"
        project_root.mkdir()

        outside_file = Path(tmp) / "elsewhere.py"

        with pytest.raises(ValueError):
            write_file(outside_file, "pass", root=project_root)
