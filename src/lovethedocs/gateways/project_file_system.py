import shutil
from pathlib import Path
from typing import Dict

from lovethedocs.ports import FileSystemPort

IGNORED_DIRS = [
    ".bzr",
    ".direnv",
    ".eggs",
    ".git",
    ".git-rewrite",
    ".hg",
    ".ipynb_checkpoints",
    ".mypy_cache",
    ".nox",
    ".pants.d",
    ".pyenv",
    ".pytest_cache",
    ".pytype",
    ".ruff_cache",
    ".svn",
    ".tox",
    ".venv",
    ".vscode",
    "__pycache__",
    "__pypackages__",
    "_build",
    "buck-out",
    "build",
    "dist",
    "node_modules",
    "site-packages",
    "venv",
    ".lovethedocs",
]


class ProjectFileSystem(FileSystemPort):
    def __init__(self, project_root: Path):
        self.root = project_root.resolve()
        self.ltd_root = self.root / ".lovethedocs"
        self.staged_root = self.ltd_root / "improved"
        self.backup_root = self.ltd_root / "backups"

    # ---------- internal guard ------------------------------------------- #
    def _ensure_relative(self, rel_path: Path) -> None:
        if rel_path.is_absolute():
            raise ValueError(
                f"FileSystemPort expects a path *relative* to the project "
                f"root, got absolute path: {rel_path}"
            )

    # ---------------------- read ------------------------------------------ #
    def load_modules(self) -> Dict[Path, str]:
        modules: Dict[Path, str] = {}
        for file in self.root.rglob("*.py"):
            if any(part in IGNORED_DIRS for part in file.parts):
                continue
            if file.name in {"__init__.py", "__main__.py"}:
                continue
            rel = file.relative_to(self.root)
            modules[rel] = file.read_text(encoding="utf-8")
        return modules

    # ---------------------- write ----------------------------------------- #
    def stage_file(self, rel_path: Path, code: str) -> None:
        self._ensure_relative(rel_path)
        dest = self.staged_path(rel_path)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(code, encoding="utf-8")

    def apply_stage(self, rel_path: Path) -> None:
        self._ensure_relative(rel_path)
        orig = self.original_path(rel_path)
        staged = self.staged_path(rel_path)

        if not staged.exists():
            raise FileNotFoundError(staged)

        self.backup_path(rel_path).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(orig, self.backup_path(rel_path))
        shutil.copy2(staged, orig)
        self.delete_staged(rel_path)

    # ---------------------- helpers --------------------------------------- #
    def original_path(self, rel_path: Path) -> Path:
        return self.root / rel_path

    def staged_path(self, rel_path: Path) -> Path:
        return self.staged_root / rel_path

    def backup_path(self, rel_path: Path) -> Path:
        return self.backup_root / rel_path

    # ---------- clean up ---------------------------------------------- #
    def delete_staged(self, rel_path: Path) -> None:
        """Remove the staged file and prune empty dirs up to _improved/."""
        self._ensure_relative(rel_path)

        staged = self.staged_path(rel_path)
        if not staged.exists():
            return

        staged.unlink()  # remove the file

        cur = staged.parent
        while cur != self.staged_root and not any(cur.iterdir()):
            cur.rmdir()
            cur = cur.parent  # walk upward

        if not any(self.staged_root.iterdir()):
            self.staged_root.rmdir()
