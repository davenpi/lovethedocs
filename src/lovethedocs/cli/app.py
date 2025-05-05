#!/usr/bin/env python3
"""
lovethedocs - Typer CLI
=======================

Usage examples
--------------

Generate docs for two packages, then open diffs:

    lovethedocs update src/ tests/
    lovethedocs review src/ tests/
"""

from __future__ import annotations

from pathlib import Path
from typing import List

import typer
from rich.console import Console

from lovethedocs.application import diff_review, run_pipeline
from lovethedocs.gateways.project_file_system import ProjectFileSystem
from lovethedocs.gateways.vscode_diff_viewer import VSCodeDiffViewer

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
)
@app.command(help="Generate improved docstrings and stage diffs.\n\n" + example)
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
) -> None:
    file_systems = run_pipeline.run_pipeline(paths)
    if review:
        console = Console()
        console.rule("[bold magenta]Reviewing documentation updates")
        for fs in file_systems:
            diff_review.batch_review(
                fs,
                diff_viewer=VSCodeDiffViewer(),
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
        help="Prompt before moving to the next diff (default: interactive).",
    ),
) -> None:
    """
    Open staged edits in your diff viewer (VS Code by default).
    """
    for root in paths:
        fs = ProjectFileSystem(root)
        if not fs.staged_root.exists():
            typer.echo(f"ℹ️  No staged edits found in {root}")
            continue

        diff_review.batch_review(
            fs,
            diff_viewer=VSCodeDiffViewer(),
            interactive=interactive,
        )


if __name__ == "__main__":
    app()
