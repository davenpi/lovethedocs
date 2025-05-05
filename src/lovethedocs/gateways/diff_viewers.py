import shutil
import subprocess
from pathlib import Path

from lovethedocs.ports import DiffViewerPort


class DiffViewerError(RuntimeError):
    """Custom exception for diff viewer errors."""

    pass


class CodeCLIDiffViewer(DiffViewerPort):
    def view(self, original: Path, staged: Path) -> None:
        try:
            subprocess.run(
                ["code", "-d", str(original), str(staged)],
                check=True,
                capture_output=True,
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise DiffViewerError("Code CLI ('code') not found on PATH.")


class TerminalDiffViewer(DiffViewerPort):
    """Colourised unified diff using Rich."""

    def view(self, original: Path, improved: Path) -> None:
        from difflib import unified_diff

        from rich.console import Console
        from rich.syntax import Syntax

        a = original.read_text().splitlines(keepends=True)
        b = improved.read_text().splitlines(keepends=True)
        diff = "".join(unified_diff(a, b, fromfile=str(original), tofile=str(improved)))
        Console().print(Syntax(diff, "diff"))


class GitDiffViewer(DiffViewerPort):
    """Fallback diff viewer that pipes `git diff --no-index` to the user's pager."""

    def view(self, original: Path, staged: Path) -> None:
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
    Return an instantiated DiffViewerPort based on *name*.

    * auto → try VS Code, then Git, then fall back to terminal
    * explicit string → instantiate that viewer or raise DiffViewerError
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
