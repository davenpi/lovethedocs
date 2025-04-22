"""
I/O helpers.  No business rules here.
"""

from pathlib import Path

IGNORED_DIRS = {"venv", ".git", "__pycache__", ".pytest_cache", ".vscode"}


def load_modules(path: Path) -> dict[str, str]:
    """
    Load all python modules in a given path, return dict with path-code pairs.


    For example::

        path = Path("src/infra")
        load_modules(path)
        ⇒ {
            "src/infra/file_system.py": "source code...",
            "src/infra/openai_client.py": "source code...",
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
        relative_path = file.relative_to(path).as_posix()  # e.g. "pkg/utils/math.py"
        modules[relative_path] = code
    return modules


def write_files(edits: dict[str, str], base: Path) -> None:
    """
    Writes each edited file into `base/_improved/<relative path>.py`,
    creating any required sub-directories first.

    Example:
        edits = {
            "infra/openai_client.py": "...",
            "samp/mod3.py": "...",
        }
        ⇒ files are written to
           <base>/_improved/infra/openai_client.py
           <base>/_improved/samp/mod3.py
    """
    target = base / "_improved"
    target.mkdir(exist_ok=True)
    target_root = base / "_improved"
    for rel_path_str, code in edits.items():
        wrapped_code = f'"""\n{code.rstrip()}\n"""'
        rel_path = Path(rel_path_str)
        dest_path = target_root / rel_path
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        dest_path.write_text(wrapped_code)
