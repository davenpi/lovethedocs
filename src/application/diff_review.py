import subprocess
from pathlib import Path
import shutil
from typing import Union


def create_backup(original_path: Path, base_dir: Path) -> Path:
    """
    Create a backup in a _backups directory parallel to _improved.
    """
    # Create backup directory parallel to _improved
    backup_dir = base_dir / "_backups"

    # Determine the relative path correctly
    try:
        rel_path = original_path.relative_to(base_dir)
    except ValueError:
        # If not a child of base_dir, just use the filename
        rel_path = Path(original_path.name)

    backup_file = backup_dir / rel_path
    backup_file.parent.mkdir(parents=True, exist_ok=True)

    # Create the backup
    shutil.copy2(original_path, backup_file)

    return backup_file


# In get_improved_path function
def get_improved_path(raw_path: Union[str, Path]) -> tuple[Path, Path, bool, Path]:
    """
    Determine the original and improved paths based on input.

    Parameters
    ----------
    raw_path : Union[str, Path]
        The path to the original file or directory

    Returns
    -------
    tuple[Path, Path, bool, Path]
        A tuple containing:
        - The base directory for operations
        - The path to the improved version (file or directory)
        - Boolean indicating if this is a single file
        - The original path
    """
    path = Path(raw_path)

    if path.is_file() and path.suffix == ".py":
        # For single file: base is parent, improved is in _improved with same name
        base_dir = path.parent
        improved_path = base_dir / "_improved" / path.name
        return base_dir, improved_path, True, path

    # For directory: base is the directory, improved is _improved subdirectory
    base_dir = path
    improved_path = base_dir / "_improved"
    return base_dir, improved_path, False, path


def review_diff(
    original_path: Path, improved_path: Path, base_dir: Path, interactive: bool = True
) -> bool:
    """
    Open the diff in VS Code and optionally prompt to accept changes.

    Parameters
    ----------
    original_path : Path
        Path to the original file
    improved_path : Path
        Path to the improved file
    interactive : bool
        Whether to prompt for acceptance

    Returns
    -------
    bool
        True if changes were accepted, False otherwise
    """
    if not original_path.exists() or not improved_path.exists():
        print(f"Error: Cannot find both original and improved versions")
        return False

    # Open VS Code diff viewer
    try:
        subprocess.run(
            ["code", "-d", str(original_path), str(improved_path)], check=True
        )
    except (subprocess.SubprocessError, FileNotFoundError):
        print(
            (
                "VS Code not found or error launching diff. Please install VS Code or"
                "check your PATH."
            )
        )
        return False

    if interactive:
        # Update the prompt in review_diff function
        rel_path = original_path.relative_to(base_dir)

        choice = input(f"\nAccept changes to {rel_path}? [y/n/e(edit)] ")
        if choice.lower() == "y":
            # Create backup and replace
            backup_path = create_backup(original_path, base_dir)
            shutil.copy2(improved_path, original_path)
            print(
                f"✓ Changes accepted for {original_path.name} (backup in {backup_path.parent})"
            )
            return True
        elif choice.lower() == "e":
            # Open for editing
            try:
                subprocess.run(["code", str(improved_path)], check=True)
                input("Press Enter when finished editing...")
                choice = input("Apply edited version? [y/n] ")
                if choice.lower() == "y":
                    backup_path = create_backup(original_path, base_dir)
                    shutil.copy2(improved_path, original_path)
                    print(
                        f"✓ Edited changes applied to {original_path.name} (backup in {backup_path.parent})"
                    )
                    return True
            except (subprocess.SubprocessError, FileNotFoundError):
                print("Error opening VS Code for editing.")

    return False


def batch_review(raw_path: Union[str, Path], interactive: bool = True) -> None:
    """
    Review all improved files in batch mode.

    Parameters
    ----------
    raw_path : Union[str, Path]
        The path to the original file or directory
    interactive : bool
        Whether to prompt for acceptance
    """
    base_dir, improved_path, is_single_file, original_path = get_improved_path(raw_path)

    if is_single_file:
        # Single file case
        print(f"\nReviewing {original_path.relative_to(base_dir)}...")
        review_diff(original_path, improved_path, base_dir, interactive)
        return
    # Directory case
    accepted = 0
    rejected = 0

    for improved_file in improved_path.glob("**/*.py"):
        # Calculate the relative path from the improved directory
        rel_path = improved_file.relative_to(improved_path)
        original = base_dir / rel_path

        if not original.exists():
            print(f"Skipping {rel_path} - original not found")
            continue

        print(f"\nReviewing {rel_path}...")
        if review_diff(original, improved_file, base_dir, interactive):
            accepted += 1
        else:
            rejected += 1

    print(f"\nReview complete: {accepted} accepted, {rejected} rejected")
