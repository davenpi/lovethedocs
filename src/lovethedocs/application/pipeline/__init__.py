"""
Public entry-point for documentation update pipelines.
"""

from pathlib import Path
from typing import Callable, Sequence, Union

from lovethedocs.domain.docstyle.base import DocStyle
from lovethedocs.domain.use_cases.update_docs import DocumentationUpdateUseCase
from lovethedocs.gateways.project_file_system import ProjectFileSystem

from .async_runner import run_async
from .factory import fs_factory, make_use_case
from .sync_runner import run_sync

__all__ = ["run_pipeline"]


def run_pipeline(
    paths: Union[str | Path, Sequence[str | Path]],
    *,
    style: str,
    concurrency: int = 0,
    fs_factory: Callable[[Path], ProjectFileSystem] = fs_factory,
    use_case_factory: Callable[[bool], DocumentationUpdateUseCase] = make_use_case,
) -> list[ProjectFileSystem]:
    """
    Dispatch to the sync or async runner according to `concurrency`.

    Parameters
    ----------
    paths : str | Path | Sequence[str | Path]
        Project roots or package paths to process.
    style : str | DocStyle
        Docstring style to use (numpy or google).
    concurrency : int
        Number of concurrent requests to make. If 0, run synchronously.
    fs_factory : Callable[[Path], ProjectFileSystem]
        Factory function to create a ProjectFileSystem instance.
    use_case_factory : Callable[[bool], DocumentationUpdateUseCase]
        Factory function to create a DocumentationUpdateUseCase instance.

    Returns
    -------
    list[ProjectFileSystem]
        List of ProjectFileSystem instances with staged files.
    """
    style = DocStyle.from_string(style)

    async_mode = concurrency > 0
    use_case = use_case_factory(async_mode=async_mode, style=style)

    if async_mode:
        return run_async(
            paths=paths,
            concurrency=concurrency,
            fs_factory=fs_factory,
            use_case=use_case,
            style=style,
        )

    return run_sync(
        paths=paths,
        fs_factory=fs_factory,
        use_case=use_case,
        style=style,
    )
