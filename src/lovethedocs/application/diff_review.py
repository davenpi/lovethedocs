"""
Developer UX helpers for manually accepting or rejecting staged edits.

Relies on the new ProjectFileSystem gateway:
    • original files  → <root>/<rel_path>
    • staged updates → <root>/_improved/<rel_path>
    • backups        → <root>/_backups/<rel_path>
"""

from __future__ import annotations

from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from lovethedocs.gateways.project_file_system import ProjectFileSystem
from lovethedocs.ports import DiffViewerPort

console = Console()


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
    Display the diff for a single file and optionally apply the staged changes.

    Shows the diff between the original and staged file using the provided diff viewer.
    If interactive mode is enabled, prompts the user to accept or reject the changes.
    If accepted, backs up and overwrites the original file with the staged version.

    Parameters
    ----------
    fs : ProjectFileSystem
        The project file system gateway for file operations.
    rel_path : Path
        The relative path to the file being reviewed.
    diff_viewer : DiffViewerPort
        The diff viewer used to display file differences.
    interactive : bool, optional
        If True, prompt the user for acceptance; otherwise, do not apply changes
        (default is True).

    Returns
    -------
    bool
        True if the change was accepted and applied, False otherwise.
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
    Review all staged Python files and summarize the results.

    Walks through every staged Python (*.py) file, displaying diffs and prompting for
    acceptance if interactive. Tallies the number of accepted and rejected changes, and
    prints a summary panel at the end.

    Parameters
    ----------
    fs : ProjectFileSystem
        The project file system gateway for file operations.
    diff_viewer : DiffViewerPort
        The diff viewer used to display file differences.
    interactive : bool, optional
        If True, prompt the user for acceptance; otherwise, do not apply changes
        (default is True).

    Returns
    -------
    None
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

    # pretty summary panel
    if rejected == 0:
        summary_text = Text(f"✓ {accepted} accepted - 0 rejected", style="bold green")
    else:
        summary_text = Text(
            f"✓ {accepted} accepted   ✗ {rejected} rejected",
            style="yellow" if accepted else "bold red",
        )

    console.print(Panel.fit(summary_text, title="Review complete"))
