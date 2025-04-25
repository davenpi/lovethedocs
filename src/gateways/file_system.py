"""
I/O helpers.
"""

from pathlib import Path

IGNORED_DIRS = {"venv", ".git", "__pycache__", ".pytest_cache", ".vscode"}


def load_modules(path: Path) -> dict[str, str]:
    """
    Load all Python modules in a directory, returning a path-to-code mapping.

    Ignores directories listed in `IGNORED_DIRS` and skips `__init__.py` and
    `__main__.py` files. Returns a dictionary mapping each module's relative path to
    its source code as a string.

    Parameters
    ----------
    path : Path
        The path to the directory containing Python modules to load.

    Returns
    -------
    dict[str, str]
        A dictionary mapping relative file paths to their corresponding source code.
    """
    modules: dict[str, str] = {}
    for file in path.rglob("*.py"):
        if any(part in IGNORED_DIRS for part in file.parts):
            continue
        if file.name in ("__init__.py", "__main__.py"):
            continue

        code = file.read_text()
        relative_path = file.relative_to(path).as_posix()
        modules[relative_path] = code
    return modules


def write_file(path: str | Path, code: str, root: Path | None = None) -> None:
    """
    Write code to disk under an '_improved' directory, preserving directory structure.

    Writes the provided code to a file path that mirrors the original directory
    structure beneath an '_improved' folder. The output is rooted at the given project
    root or the current working directory. Ensures the written file ends with a single
    trailing newline.

    Parameters
    ----------
    path : str or Path
        The source file's relative or absolute path. If absolute, only the portion
        after 'root' is preserved in the output structure.
    code : str
        The code to write to the file.
    root : Path or None, optional
        The project root directory. If None, uses the current working directory.

    Returns
    -------
    None
    """
    path = Path(path)
    base = Path(root or Path.cwd())

    # Resolve relative path based on root or current working directory
    if path.is_absolute():
        path = path.relative_to(base)

    # Always write under <base>/_improved/<original path>
    dest = base / "_improved" / path
    dest.parent.mkdir(parents=True, exist_ok=True)

    # Ensure a single trailing newline; many tools expect it
    dest.write_text(code, encoding="utf-8")
