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

# --------------------------------------------------------------------------- #
#  Typer root application                                                     #
# --------------------------------------------------------------------------- #
app = typer.Typer(
    name="lovethedocs",
    add_completion=False,
    help="LLM-powered documentation tool.",
)


# --------------------------------------------------------------------------- #
#  `update` – generate / stage edits                                          #
# --------------------------------------------------------------------------- #
@app.command()
def update(
    paths: List[Path] = typer.Argument(
        ...,
        exists=True,
        resolve_path=True,
        metavar="PATHS",
        help="Files or directories whose Python sources should be documented.",
    ),
    review: bool = typer.Option(
        False,
        "--review",
        "-r",
        help="Immediately open diffs after generation.",
    ),
) -> None:
    """
    Run the documentation-update pipeline and stage results under
    `path/.lovethedocs/improved`.
    """
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


# --------------------------------------------------------------------------- #
#  `review` – inspect staged edits                                            #
# --------------------------------------------------------------------------- #
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
