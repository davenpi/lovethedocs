"""
Concrete asynchronous pipeline.
"""

import asyncio
from pathlib import Path
from typing import Callable, List, Sequence, Union

from lovethedocs.application import config
from lovethedocs.domain import docstyle
from lovethedocs.domain.models import SourceModule
from lovethedocs.domain.use_cases.update_docs import DocumentationUpdateUseCase
from lovethedocs.gateways.project_file_system import ProjectFileSystem

from .progress import make_progress
from .safety import safe_update_async
from .summary import summarize

cfg = config.Settings()
style = docstyle.DocStyle.from_string(cfg.doc_style)


async def _inner(
    *,
    paths: Sequence[str | Path],
    concurrency: int,
    fs_factory: Callable[[Path], ProjectFileSystem],
    use_case: DocumentationUpdateUseCase,
    style: docstyle.DocStyle,
) -> List[ProjectFileSystem]:
    failures: list[tuple[Path, Exception]] = []
    processed = 0
    file_systems: list[ProjectFileSystem] = []

    sem = asyncio.Semaphore(concurrency)

    with make_progress() as progress:
        proj_task = progress.add_task("Projects", total=len(paths))

        for raw in paths:
            root = Path(raw).resolve()

            # project-scoped FS
            if root.is_file() and root.suffix == ".py":
                fs = fs_factory(root.parent)
                module_map = {root.relative_to(root.parent): root.read_text("utf-8")}
            elif root.is_dir():
                fs = fs_factory(root)
                module_map = fs.load_modules()
            else:
                progress.advance(proj_task)
                continue

            src_modules = [
                SourceModule(path, code) for path, code in module_map.items()
            ]
            mod_task = progress.add_task(f"[cyan]{root.name}", total=len(src_modules))

            tasks = [
                asyncio.create_task(
                    safe_update_async(use_case, src_mod, style=style, sem=sem)
                )
                for src_mod in src_modules
            ]

            for coro in asyncio.as_completed(tasks):
                mod, new_code, exc = await coro
                rel_path = Path(mod.path)

                if exc:
                    failures.append((rel_path, exc))
                else:
                    fs.stage_file(rel_path, new_code)

                processed += 1
                progress.advance(mod_task)

            file_systems.append(fs)
            progress.advance(proj_task)

    summarize(failures, processed)
    return file_systems


def run_async(
    *,
    paths: Union[str | Path, Sequence[str | Path]],
    concurrency: int,
    fs_factory: Callable[[Path], ProjectFileSystem],
    use_case: DocumentationUpdateUseCase,
) -> List[ProjectFileSystem]:
    """Entry-point called by pipeline.__init__."""
    if isinstance(paths, (str, Path)):
        paths = [paths]
    return asyncio.run(
        _inner(
            paths=list(paths),
            concurrency=concurrency,
            fs_factory=fs_factory,
            use_case=use_case,
            style=style,
        )
    )
