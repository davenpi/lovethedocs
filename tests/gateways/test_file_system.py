import tempfile
import textwrap
from pathlib import Path

import pytest

from lovethedocs.gateways.project_file_system import ProjectFileSystem


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
        improved_root = project_root / ".lovethedocs" / "staged"
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


# ---------- delete_staged ------------------------------------------------ #
def test_delete_staged_prunes_empty_dirs():
    """Staging a single nested file and then deleting it should
    remove the file *and* clean up the empty directory tree,
    ultimately deleting the top‑level _improved/ directory.
    """
    with tempfile.TemporaryDirectory() as tmp:
        project_root = Path(tmp) / "repo"
        rel_path = Path("src/nested/alpha.py")
        code = "print('hi')\n"

        fs = ProjectFileSystem(project_root)
        fs.stage_file(rel_path, code)

        staged_file = fs.staged_path(rel_path)
        # Sanity check – file and _improved dir exist
        assert staged_file.is_file()
        assert fs.staged_root.exists()

        # Act
        fs.delete_staged(rel_path)

        # The staged file and the entire _improved tree should be gone
        assert not staged_file.exists()
        assert not fs.staged_root.exists()


# ---------- apply_stage idempotence ------------------------------------- #
def test_apply_stage_is_idempotent():
    """Applying a staged change twice should leave the workspace in a
    consistent state: the first call copies code and makes a backup,
    the second call raises FileNotFoundError while leaving everything
    else untouched.
    """
    with tempfile.TemporaryDirectory() as tmp:
        project_root = Path(tmp) / "repo"
        project_root.mkdir(parents=True, exist_ok=True)

        rel_path = Path("alpha.py")
        original_code = "x = 1\n"
        updated_code = "x = 2\n"

        # Write original file
        (project_root / rel_path).write_text(original_code)

        fs = ProjectFileSystem(project_root)

        # Stage an update and apply it once
        fs.stage_file(rel_path, updated_code)
        fs.apply_stage(rel_path)

        # Verify update and backup
        assert (project_root / rel_path).read_text() == updated_code
        assert fs.backup_path(rel_path).read_text() == original_code

        # Second apply should raise but not corrupt state
        with pytest.raises(FileNotFoundError):
            fs.apply_stage(rel_path)

        # Final consistency checks
        assert (project_root / rel_path).read_text() == updated_code
        assert fs.backup_path(rel_path).is_file()
