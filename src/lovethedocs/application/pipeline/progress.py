from rich.console import Console
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
    TimeElapsedColumn,
)

_console = Console()


def make_progress() -> Progress:
    """
    Create and return a two-line, color-blind-friendly progress bar.

    The progress bar uses a spinner, colored text, a green bar, task progress, and
    elapsed time. It is configured to clear itself when finished.

    Returns
    -------
    Progress
        A configured Rich Progress instance for tracking tasks.
    """
    return Progress(
        SpinnerColumn(style="yellow"),
        TextColumn("[bold blue]{task.description}"),
        BarColumn(bar_width=None, complete_style="green"),
        TaskProgressColumn(),
        TimeElapsedColumn(),
        console=_console,
        transient=True,  # clear bar when done
    )
