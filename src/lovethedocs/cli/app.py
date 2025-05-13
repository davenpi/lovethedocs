"""
lovethedocs - Typer CLI
=======================

Usage examples
--------------

Generate docs for two packages, then open diffs:

    lovethedocs update src/
    lovethedocs review src/
"""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import List

import typer
from rich.console import Console

from lovethedocs import __version__
from lovethedocs.application import diff_review
from lovethedocs.application.pipeline import run_pipeline
from lovethedocs.gateways.diff_viewers import DiffViewerError, resolve_viewer
from lovethedocs.gateways.project_file_system import ProjectFileSystem

app = typer.Typer(
    name="lovethedocs",
    add_completion=True,
    help=(
        "Automate Python docstrings in seconds.\n\n"
        "Quick workflow:\n\n"
        "lovethedocs update -c 8 <path>            # fast with 8 workers\n\n"
        "lovethedocs review <path>                 # open diffs (Cursor default)\n\n"
        "lovethedocs clean <path>                  # remove path/.lovethedocs\n\n"
        "lovethedocs update -s google -r <path>    # generate & review, Google style\n\n"
    ),
)


@app.command()
def version() -> None:
    """Show the version and exit."""
    typer.echo(f"lovethedocs version {__version__}")


example = (
    "Examples\n\n"
    "--------\n\n"
    "lovethedocs update -c 8 src/                  # fast, 8 concurrent requests\n\n"
    "lovethedocs update -s google -r src/          # Google style; generate & review\n\n"
)


@app.command(help="Generate & stage docstrings (use -s STYLE and -c N).\n\n" + example)
def update(
    paths: List[Path] = typer.Argument(
        ...,
        exists=True,
        resolve_path=True,
        metavar="PATHS",
        help="Project roots or package paths to process.",
    ),
    style: str = typer.Option(
        "numpy",
        "-s",
        "--style",
        help=("Docstring style to use (numpy or google)."),
    ),
    review: bool = typer.Option(
        False,
        "-r",
        "--review",
        help="Open diffs immediately after generation.",
    ),
    viewer: str = typer.Option(
        None,
        "-v",
        "--viewer",
        help="Diff viewer to use (auto, cursor, vscode, git, terminal).",
    ),
    concurrency: int = typer.Option(
        0,
        "-c",
        "--concurrency",
        metavar="N",
        min=0,
        help=(
            "Number of concurrent requests to the LLM. "
            "0 keeps the synchronous behavior; "
            "Use 2+ for more speed."
        ),
    ),
) -> None:
    """
    Generate new docstrings for the given paths and stage diffs.

    Optionally opens the diffs for review after generation. Supports concurrent
    requests to the LLM for faster processing of large projects.

    Parameters
    ----------
    paths : List[Path]
        Project roots or package paths to process.
    style : str, optional
        Docstring style to use ('numpy' or 'google'). Default is 'numpy'.
    review : bool, optional
        If True, open diffs immediately after generation. Default is False.
    viewer : str, optional
        Diff viewer to use ('auto', 'cursor', 'vscode', 'git', 'terminal'). Default
        is 'auto'.
    concurrency : int, optional
        Number of concurrent requests to the LLM.
    """
    style = style.lower() or "numpy"
    try:
        file_systems = run_pipeline(paths, concurrency=concurrency, style=style)
    except ValueError as e:
        typer.echo(f"❌ {e}")
        raise typer.Exit(code=1)
    if review or viewer:
        selected_viewer = resolve_viewer(name=(viewer or "auto"))
        console = Console()
        console.rule("[bold magenta]Reviewing documentation updates")
        for fs in file_systems:
            diff_review.batch_review(
                fs,
                diff_viewer=selected_viewer,
                interactive=True,
            )


review_example = (
    "Examples\n\n"
    "--------\n\n"
    "lovethedocs review src/                      # open diffs for review (Cursor defualt)\n\n"
    "lovethedocs review -v git src/               # use git as a diff viewer\n\n"
)


@app.command(
    help="Open staged documentation edits in the specified diff viewer.\n\n"
    + review_example
)
def review(
    paths: List[Path] = typer.Argument(
        ...,
        exists=True,
        resolve_path=True,
        metavar="PATHS",
        help="Project roots that contain a .lovethedocs folder.",
    ),
    interactive: bool = typer.Option(
        True,
        "--interactive/--no-interactive",
        help="Prompt before moving to the next diff.",
    ),
    viewer: str = typer.Option(
        "cursor",
        "-v",
        "--viewer",
        help="Diff viewer to use (auto, cursor, vscode, git, terminal).",
    ),
) -> None:
    """
    Open staged documentation edits in the specified diff viewer.

    Parameters
    ----------
    paths : List[Path]
        Project roots that contain a .lovethedocs folder.
    interactive : bool, optional
        If True, prompt before moving to the next diff. Default is True.
    viewer : str, optional
        Diff viewer to use ('auto', 'cursor', 'vscode', 'git', 'terminal'). Default
        is 'auto'.
    """
    try:
        selected_viewer = resolve_viewer(viewer)
    except DiffViewerError as e:
        typer.echo(f"❌ {e}")
        raise typer.Exit(code=1)
    for root in paths:
        fs = ProjectFileSystem(root)
        if not fs.staged_root.exists():
            typer.echo(f"ℹ️  No staged edits found in {root}")
            continue

        diff_review.batch_review(
            fs,
            diff_viewer=selected_viewer,
            interactive=interactive,
        )


@app.command(help="Remove lovethedocs artifacts from a project.")
def clean(
    paths: List[Path] = typer.Argument(
        ...,
        exists=True,
        resolve_path=True,
        metavar="PATHS",
        help="Project roots to purge (will delete path/.lovethedocs/*).",
    ),
    yes: bool = typer.Option(
        False,
        "-y",
        "--yes",
        help="Skip confirmation prompt.",
    ),
) -> None:
    """
    Remove lovethedocs artifacts from the specified project roots.

    Deletes the .lovethedocs directory in each given path. Prompts for confirmation
    unless 'yes' is specified.

    Parameters
    ----------
    paths : List[Path]
        Project roots to purge (deletes path/.lovethedocs/*).
    yes : bool, optional
        If True, skip the confirmation prompt. Default is False.
    """
    for root in paths:
        trash = [root / ".lovethedocs"]
        trash = [p for p in trash if p.exists()]

        if not trash:
            typer.echo(f"Nothing to clean in {root}.")
            continue

        if not yes:
            names = ", ".join(str(p.relative_to(root)) for p in trash if p.exists())
            if not typer.confirm(
                f"The following will be deleted in {root}: {names}\n\n"
                "Are you sure you want to proceed?",
                abort=False,
            ):
                typer.echo(f"❌ Cleanup skipped for {root}.")
                continue

        for path in trash:
            if path.exists():
                shutil.rmtree(path)
        typer.echo(f"🗑️  Cleaned up {root}")


if __name__ == "__main__":
    app()
