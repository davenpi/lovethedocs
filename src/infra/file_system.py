"""
I/O helpers.  No business rules here.
"""

from pathlib import Path

IGNORED_DIRS = {"venv", ".git", "__pycache__", ".pytest_cache", ".vscode"}


def concatenate_modules(path: Path) -> str:
    """
    Legacy helper: returns one big string with BEGIN/END markers.
    Will be replaced by an AST-based extractor in a later phase.
    """

    code_blocks: list[str] = []
    # Walk the project tree recursively, but ignore virtual‑envs and misc build dirs.
    for file in path.rglob("*.py"):
        # Skip files that live inside ignored directories
        if any(part in IGNORED_DIRS for part in file.parts):
            continue
        if file.name in ("__init__.py", "__main__.py"):
            continue

        code = file.read_text().strip()
        relative_path = file.relative_to(path).as_posix()  # e.g. "pkg/utils/math.py"
        code_blocks.append(f"BEGIN {relative_path}\n{code}\nEND {relative_path}\n")
    return "\n".join(code_blocks).strip()


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
    # for name, code in edits.items():
    #     (target / name).write_text(code)
    target_root = base / "_improved"
    for rel_path_str, code in edits.items():
        wrapped_code = f'"""\n{code.rstrip()}\n"""'
        rel_path = Path(rel_path_str)
        dest_path = target_root / rel_path
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        dest_path.write_text(wrapped_code)
