import textwrap
import tempfile
from pathlib import Path

from src.infra.file_system import load_modules


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
