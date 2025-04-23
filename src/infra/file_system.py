"""
I/O helpers.
"""

from pathlib import Path

IGNORED_DIRS = {"venv", ".git", "__pycache__", ".pytest_cache", ".vscode"}


def load_modules(path: Path) -> dict[str, str]:
    """
    Load all python modules in a given path, return dict with path-code pairs.

    Also ignores directories that are in the `IGNORED_DIRS` set, and skips
    `__init__.py` and `__main__.py` files.

    For example::

        path = Path("src/")
        load_modules(path)
        ⇒ {
            "src/hello.py": "source code...",
            "src/main.py": "source code...",
            ...
        }

    Parameters
    ----------
    path : Path
        The path to the directory containing the Python modules.

    Returns
    -------
    dict[str, str]
        A dictionary where the keys are the relative paths of the Python modules
        and the values are their corresponding code as strings.
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


# TODO: Clean this up and improve documentation.
def write_file(path: str | Path, code: str, root: Path | None = None) -> None:
    """
    Write *code* to disk, mirroring the original directory structure
    under an ``_improved`` folder.

    Parameters
    ----------
    path : str | Path
        The source file's **relative** path (e.g., ``"pkg/foo.py"``) or an
        absolute path.  If absolute, only its tail after *root* is preserved.
    code : str
        The code to write.
    root : Path | None, default None
        The project root that was handed to ``load_modules``.  If omitted,
        ``Path.cwd()`` is used, so running the pipeline from anywhere still
        writes files under ``./_improved``.

    Returns
    -------
    None
    """
    path = Path(path)
    base = Path(root) if root else Path.cwd()

    # Always write under <base>/_improved/<original path>
    dest = base / Path("_improved") / path
    dest.parent.mkdir(parents=True, exist_ok=True)

    # Ensure a single trailing newline; many tools expect it
    dest.write_text(code.rstrip() + "\n", encoding="utf-8")
