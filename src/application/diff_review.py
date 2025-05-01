"""
Developer UX helpers for manually accepting or rejecting staged edits.

Relies on the new ProjectFileSystem gateway:
    • original files  → <root>/<rel_path>
    • staged updates → <root>/_improved/<rel_path>
    • backups        → <root>/_backups/<rel_path>
"""

from __future__ import annotations

from pathlib import Path

from src.gateways.project_file_system import ProjectFileSystem
from src.ports import DiffViewerPort


# --------------------------------------------------------------------------- #
# core review logic                                                           #
# --------------------------------------------------------------------------- #
def _review_single(
    fs: ProjectFileSystem,
    rel_path: Path,
    *,
    diff_viewer: DiffViewerPort,
    interactive: bool = True,
) -> bool:
    """
    Show the diff; if accepted, back up + overwrite the original file.

    Returns True when the change was applied.
    """
    original = fs.original_path(rel_path)
    staged = fs.staged_path(rel_path)

    diff_viewer.view(original, staged)

    if not interactive:
        return False

    choice = input(f"Accept changes to {rel_path}? [y/n] ").strip().lower()
    if choice == "y":
        fs.apply_stage(rel_path)
        return True

    return False


# --------------------------------------------------------------------------- #
# public helper                                                               #
# --------------------------------------------------------------------------- #
def batch_review(
    fs: ProjectFileSystem,
    *,
    diff_viewer: DiffViewerPort,
    interactive: bool = True,
) -> None:
    """
    Walk every staged *.py* file and pipe it through `_review_single`,
    tallying the results.
    """
    staged_files = list(fs.staged_root.glob("**/*.py"))
    if not staged_files:
        print("No staged files to review.")
        return

    accepted = rejected = 0
    for staged in staged_files:
        rel_path = staged.relative_to(fs.staged_root)
        print(f"\nReviewing {rel_path}...")
        ok = _review_single(
            fs,
            rel_path,
            diff_viewer=diff_viewer,
            interactive=interactive,
        )
        accepted += int(ok)
        rejected += int(not ok)

    print(f"\nReview complete: {accepted} accepted, {rejected} rejected")
