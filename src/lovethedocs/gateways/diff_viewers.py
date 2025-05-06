import shutil
import subprocess
from pathlib import Path

from lovethedocs.ports import DiffViewerPort


class DiffViewerError(RuntimeError):
    """Exception raised for errors related to diff viewers."""

    pass


class CodeCLIDiffViewer(DiffViewerPort):
    """Diff viewer that launches the VS Code CLI to show file differences."""

    def view(self, original: Path, staged: Path) -> None:
        """
        Open a diff view between two files using the VS Code CLI.

        Parameters
        ----------
        original : Path
            The path to the original file.
        staged : Path
            The path to the staged or modified file.

        Raises
        ------
        DiffViewerError
            If the VS Code CLI ('code') is not found on the system PATH or the command
            fails.
        """
        try:
            subprocess.run(
                ["code", "-d", str(original), str(staged)],
                check=True,
                capture_output=True,
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise DiffViewerError("Code CLI ('code') not found on PATH.")


class TerminalDiffViewer(DiffViewerPort):
    """Diff viewer that displays a colorized unified diff in the terminal using Rich."""

    def view(self, original: Path, improved: Path) -> None:
        """
        Display a colorized unified diff between two files in the terminal.

        Parameters
        ----------
        original : Path
            The path to the original file.
        improved : Path
            The path to the improved or modified file.
        """
        from difflib import unified_diff

        from rich.console import Console
        from rich.syntax import Syntax

        a = original.read_text().splitlines(keepends=True)
        b = improved.read_text().splitlines(keepends=True)
        diff = "".join(unified_diff(a, b, fromfile=str(original), tofile=str(improved)))
        Console().print(Syntax(diff, "diff"))


class GitDiffViewer(DiffViewerPort):
    """Diff viewer that pipes 'git diff --no-index' output to the user's pager."""

    def view(self, original: Path, staged: Path) -> None:
        """
        Show a diff between two files using 'git diff --no-index'.

        Parameters
        ----------
        original : Path
            The path to the original file.
        staged : Path
            The path to the staged or modified file.
        """
        subprocess.run(
            ["git", "--no-pager", "diff", "--no-index", str(original), str(staged)],
            check=False,
        )


_VIEWER_REGISTRY = {
    "code": CodeCLIDiffViewer,
    "vscode": CodeCLIDiffViewer,
    "git": GitDiffViewer,
    "terminal": TerminalDiffViewer,
}


def resolve_viewer(name: str = "auto") -> DiffViewerPort:
    """
    Return an instantiated DiffViewerPort based on the given viewer name.

    If 'auto', prefer VS Code if available, then Git, then fall back to a terminal diff.
    If a specific name is given, instantiate the corresponding viewer or raise
    DiffViewerError.

    Parameters
    ----------
    name : str, default 'auto'
        The name of the diff viewer to use ('auto', 'code', 'vscode', 'git', or
        'terminal').

    Returns
    -------
    DiffViewerPort
        An instance of the selected diff viewer.

    Raises
    ------
    DiffViewerError
        If the specified viewer name is unknown.
    """
    name = name.lower()
    if name != "auto":
        try:
            return _VIEWER_REGISTRY[name]()
        except KeyError as exc:
            raise DiffViewerError(f"Unknown diff viewer '{name}'.") from exc

    if shutil.which("code"):
        return CodeCLIDiffViewer()
    if shutil.which("git"):
        return GitDiffViewer()
    return TerminalDiffViewer()
