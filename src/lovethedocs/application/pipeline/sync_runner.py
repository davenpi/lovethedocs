"""
Concrete synchronous pipeline.
"""

from pathlib import Path
from typing import Callable, List, Sequence, Union

from lovethedocs.application import config
from lovethedocs.domain import docstyle
from lovethedocs.domain.models import SourceModule
from lovethedocs.domain.use_cases.update_docs import DocumentationUpdateUseCase
from lovethedocs.gateways.project_file_system import ProjectFileSystem

from .progress import make_progress
from .safety import safe_update
from .summary import summarize

cfg = config.Settings()
style = docstyle.DocStyle.from_string(cfg.doc_style)


def run_sync(
    *,
    paths: Union[str | Path, Sequence[str | Path]],
    fs_factory: Callable[[Path], ProjectFileSystem],
    use_case: DocumentationUpdateUseCase,
    style: docstyle.DocStyle = style,
) -> List[ProjectFileSystem]:
    """Serial but failure-tolerant pipeline."""
    # — normalise input
    if isinstance(paths, (str, Path)):
        paths = [paths]

    failures: list[tuple[Path, Exception]] = []
    processed = 0
    file_systems: list[ProjectFileSystem] = []

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

            for module in src_modules:
                mod, new_code, exc = safe_update(use_case, module, style=style)
                rel_path = mod.path

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
