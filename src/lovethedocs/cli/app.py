#!/usr/bin/env python3
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

from lovethedocs.application import diff_review, run_pipeline
from lovethedocs.gateways.diff_viewers import resolve_viewer
from lovethedocs.gateways.project_file_system import ProjectFileSystem

app = typer.Typer(
    name="lovethedocs",
    add_completion=True,
    help=(
        "Improve Python docstrings with help from an LLM.\n\n"
        "Typical workflow:\n\n"
        "lovethedocs update <path>    # call the LLM to update docs \n\n"
        "lovethedocs review <path>    # open diffs in your viewer\n\n"
        "lovethedocs update -r <path> # update & review in one step\n\n"
    ),
)

example = (
    "Examples\n\n"
    "--------\n\n"
    "lovethedocs update gateways/ application/      # stage edits only\n\n"
    "lovethedocs update -r gateways/                # stage and review\n\n"
    "lovethedocs update -a 6 src/                   # run with 6 concurrent requests"
)


@app.command(help="Generate new docstrings and stage diffs.\n\n" + example)
def update(
    paths: List[Path] = typer.Argument(
        ...,
        exists=True,
        resolve_path=True,
        metavar="PATHS",
        help="Project roots or package paths to process.",
    ),
    review: bool = typer.Option(
        False,
        "-r",
        "--review",
        help="Open diffs immediately after generation.",
    ),
    viewer: str = typer.Option(
        "auto",
        "-v",
        "--viewer",
        help="Diff viewer to use (auto, vscode, git, terminal).",
    ),
    concurrency: int = typer.Option(
        0,
        "-c",
        "--concurrency",
        metavar="N",
        min=0,
        help=(
            "Number of concurrent requests to the LLM. "
            "0 (default) keeps the synchronous behavior; "
            "Use 4-8 for a bigger speedup."
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
    review : bool, optional
        If True, open diffs immediately after generation. Default is False.
    viewer : str, optional
        Diff viewer to use ('auto', 'vscode', 'git', 'terminal'). Default is 'auto'.
    concurrency : int, optional
        Number of concurrent requests to the LLM. 0 (default) processes synchronously.
    """
    file_systems = run_pipeline.run_pipeline(paths, concurrency=concurrency)
    selected_viewer = resolve_viewer(viewer)
    if review:
        console = Console()
        console.rule("[bold magenta]Reviewing documentation updates")
        for fs in file_systems:
            diff_review.batch_review(
                fs,
                diff_viewer=selected_viewer,
                interactive=True,
            )


@app.command()
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
        "auto",
        "-v",
        "--viewer",
        help="Diff viewer to use (auto, vscode, git, terminal).",
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
        Diff viewer to use ('auto', 'vscode', 'git', 'terminal'). Default is 'auto'.
    """
    selected_viewer = resolve_viewer(viewer)
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
