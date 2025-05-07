"""
Failure-report rendering.
"""

import sys
from pathlib import Path
from typing import List, Tuple

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()
Failure = Tuple[Path, Exception]


def summarize(failures: List[Failure], processed: int) -> None:
    """
    Print a green tick panel or a rich table of failures.
    """
    if not failures:
        console.print(
            Panel.fit(
                f"✓ {processed} modules updated without errors.", style="bold green"
            )
        )
        return

    table = Table(title="Failed modules", show_lines=True, expand=True)
    table.add_column("Module")
    table.add_column("Error", overflow="fold")

    for path, exc in failures:
        print(f"✗ {path}: {exc}", file=sys.stderr)
        table.add_row(str(path), str(exc))

    console.print(
        Panel(
            table,
            title=f"✓ {processed - len(failures)} ok   ✗ {len(failures)} failed",
            style="red",
        )
    )
