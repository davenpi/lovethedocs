# src/application/diff_review.py
from __future__ import annotations

from pathlib import Path
from typing import Union

from src.ports import DiffViewerPort, FileWriterPort


# --------------------------------------------------------------------------- #
# helpers                                                                     #
# --------------------------------------------------------------------------- #
def get_improved_roots(raw_path: Union[str, Path]) -> tuple[Path, Path, bool, Path]:
    """
    Decide where the *_improved* artefacts live for either a single file
    or a directory run.

    Returns
    -------
    base_dir         - the directory that contains the original sources
    improved_root    - directory that directly mirrors *base_dir* structure
                       (handles the case where the generator wrote
                       `_improved/<base_dir.name>/…`)
    is_single_file   - True if the user invoked the pipeline on one file
    original_path    - the original Path object passed in (file or dir)
    """
    path = Path(raw_path)

    # ---------- single-file run ---------------------------------------------
    if path.is_file() and path.suffix == ".py":
        base_dir = path.parent
        improved_root = base_dir / "_improved"
        return base_dir, improved_root, True, path

    # ---------- directory run ------------------------------------------------
    base_dir = path
    improved_root = base_dir / "_improved"

    # Some generators nest the base dir again: _improved/<base_dir.name>/...
    nested = improved_root / base_dir.name
    if nested.is_dir():
        improved_root = nested

    return base_dir, improved_root, False, path


# --------------------------------------------------------------------------- #
# core review logic                                                           #
# --------------------------------------------------------------------------- #
def review_diff(
    original: Path,
    improved: Path,
    *,
    base_dir: Path,
    diff_viewer: DiffViewerPort,
    fs: FileWriterPort,
    interactive: bool = True,
) -> bool:
    """
    Show the diff; if accepted, back up + overwrite the original file.

    Returns True when the change was applied.
    """
    diff_viewer.view(original, improved)

    if not interactive:
        return False

    rel = original.relative_to(base_dir)
    choice = input(f"Accept changes to {rel}? [y/n] ").strip().lower()

    if choice == "y":
        fs.backup_file(original, root=base_dir)
        fs.write_file(original, improved.read_text(), root=base_dir)
        return True

    return False


def batch_review(
    raw_path: Union[str, Path],
    *,
    diff_viewer: DiffViewerPort,
    fs: FileWriterPort,
    interactive: bool = True,
) -> None:
    """
    Walk every *.py* under *_improved* (correctly handling the “nested base”
    case) and pipe them through `review_diff`, tallying the results.
    """
    base_dir, improved_root, is_single, original_path = get_improved_roots(raw_path)

    # ---------- single file --------------------------------------------------
    if is_single:
        print(f"\nReviewing {original_path.name}...")
        review_diff(
            original_path,
            improved_root / original_path.name,
            base_dir=base_dir,
            diff_viewer=diff_viewer,
            fs=fs,
            interactive=interactive,
        )
        return

    # ---------- directory ----------------------------------------------------
    accepted = rejected = 0

    for improved_file in improved_root.glob("**/*.py"):
        rel_path = improved_file.relative_to(improved_root)
        original = base_dir / rel_path

        if not original.exists():
            print(f"Skipping {rel_path} (original not found)")
            continue

        print(f"\nReviewing {rel_path}...")
        ok = review_diff(
            original,
            improved_file,
            base_dir=base_dir,
            diff_viewer=diff_viewer,
            fs=fs,
            interactive=interactive,
        )
        accepted += int(ok)
        rejected += int(not ok)

    print(f"\nReview complete: {accepted} accepted, {rejected} rejected")
