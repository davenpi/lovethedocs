"""
Public entry-point for documentation update pipelines.
"""

from pathlib import Path
from typing import Callable, Sequence, Union

from lovethedocs.domain.use_cases.update_docs import DocumentationUpdateUseCase
from lovethedocs.gateways.project_file_system import ProjectFileSystem

from .async_runner import run_async
from .factory import fs_factory, make_use_case
from .sync_runner import run_sync

__all__ = ["run_pipeline"]


def run_pipeline(
    paths: Union[str | Path, Sequence[str | Path]],
    *,
    concurrency: int = 0,
    fs_factory: Callable[[Path], ProjectFileSystem] = fs_factory,
    use_case_factory: Callable[[bool], DocumentationUpdateUseCase] = make_use_case,
) -> list[ProjectFileSystem]:
    """
    Dispatch to the sync or async runner according to *concurrency*.
    """
    async_mode = concurrency > 0
    use_case = use_case_factory(async_mode=async_mode)

    if async_mode:
        return run_async(
            paths=paths,
            concurrency=concurrency,
            fs_factory=fs_factory,
            use_case=use_case,
        )

    return run_sync(
        paths=paths,
        fs_factory=fs_factory,
        use_case=use_case,
    )
