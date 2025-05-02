"""
Glue code to run the documentation-update pipeline.

The file is now a *thin adapter*: all business logic lives in domain
services and the DocumentationUpdateUseCase.  This module only

    • normalises incoming paths,
    • loads / writes files through gateway ports,
    • feeds data into the use-case,
    • shows progress bars and a final summary.
"""

from __future__ import annotations

import logging
from functools import lru_cache
from pathlib import Path
from typing import Callable, Sequence, Union

from rich.console import Console
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
    TimeElapsedColumn,
)
from rich.table import Table

from lovethedocs.application import logging_setup  # noqa: F401
from lovethedocs.application import config, mappers, utils
from lovethedocs.domain import docstyle
from lovethedocs.domain.models import SourceModule
from lovethedocs.domain.services import PromptBuilder
from lovethedocs.domain.services.generator import ModuleEditGenerator
from lovethedocs.domain.services.patcher import ModulePatcher
from lovethedocs.domain.templates import PromptTemplateRepository
from lovethedocs.domain.use_cases.update_docs import DocumentationUpdateUseCase
from lovethedocs.gateways import schema_loader
from lovethedocs.gateways.openai_client import OpenAIClientAdapter
from lovethedocs.gateways.project_file_system import ProjectFileSystem

# --------------------------------------------------------------------------- #
#  Helpers                                                                    #
# --------------------------------------------------------------------------- #
console = Console()


def _make_progress() -> Progress:
    """
    Create and return a two-line, color-blind-friendly progress bar.

    The progress bar uses a spinner, colored text, a green bar, task progress, and elapsed time.
    It is configured to clear itself when finished.

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
        console=console,
        transient=True,  # clear bar when done
    )


def _summarize_failures(failures: list[tuple[Path, Exception]], processed: int) -> None:
    """
    Display a summary of failed and successful module updates.

    Prints a green panel if there are no failures. Otherwise, prints a table of failed modules
    and their associated errors, and logs each failure.

    Parameters
    ----------
    failures : list of tuple[Path, Exception]
        List of (module path, exception) pairs for failed updates.
    processed : int
        Total number of modules processed.
    """
    if not failures:
        console.print(
            Panel.fit(
                f"✓ {processed} modules updated without errors.",
                style="bold green",
            )
        )
        return

    table = Table(title="Failed modules", show_lines=True, expand=True)
    table.add_column("Module")
    table.add_column("Error", overflow="fold")

    for path, exc in failures:
        table.add_row(str(path), str(exc))
        logging.exception("Failure in %s", path, exc_info=exc)

    console.print(
        Panel(
            table,
            title=f"✓ {processed - len(failures)} ok   ✗ {len(failures)} failed",
            style="red",
        )
    )


@lru_cache
def _make_use_case() -> DocumentationUpdateUseCase:
    """
    Create and return a configured DocumentationUpdateUseCase instance.

    Initializes configuration, doc style, OpenAI client, edit generator, prompt
    builder, and patcher, then assembles the use case object.

    Returns
    -------
    DocumentationUpdateUseCase
        The fully configured use case for updating documentation.
    """
    cfg = config.Settings()

    doc_style = docstyle.DocStyle.from_string(cfg.doc_style)
    openai_client = OpenAIClientAdapter(
        model=cfg.model,
        style=doc_style,
    )
    edit_generator = ModuleEditGenerator(
        client=openai_client,
        validator=schema_loader.VALIDATOR,
        mapper=mappers.map_json_to_module_edit,
    )
    _BUILDER = PromptBuilder(PromptTemplateRepository())
    _USES = DocumentationUpdateUseCase(
        builder=_BUILDER,
        generator=edit_generator,
        patcher=ModulePatcher(),
    )
    return _USES


# --------------------------------------------------------------------------- #
#  Public adapter                                                             #
# --------------------------------------------------------------------------- #
def run_pipeline(
    paths: Union[str | Path, Sequence[str | Path]],
    *,
    fs_factory: Callable[[Path], ProjectFileSystem] = utils.fs_factory,
    use_case_factory: Callable[[], DocumentationUpdateUseCase] = _make_use_case,
) -> list[ProjectFileSystem]:
    """
    Update documentation for all Python files under the given paths.

    Normalizes input paths, loads files using the provided file system factory, runs
    the documentation update use case, stages updated files, and displays progress and
    a summary.

    Parameters
    ----------
    paths : str, Path, or Sequence of (str or Path)
        One or more files or directories to process. Mixed input is allowed.
    fs_factory : Callable[[Path], ProjectFileSystem], optional
        Factory function that returns a ProjectFileSystem for a given project root.
    use_case_factory : Callable[[], DocumentationUpdateUseCase], optional
        Factory function that returns a DocumentationUpdateUseCase instance.

    Returns
    -------
    list[ProjectFileSystem]
        List of file system adapters used for the processed projects.
    """
    # -- TODO: REFACTOR ------
    cfg = config.Settings()
    doc_style = docstyle.DocStyle.from_string(cfg.doc_style)
    use_case = use_case_factory()

    # Normalise input --------------------------------------------------------
    if isinstance(paths, (str, Path)):
        paths = [paths]  # type: ignore[list-item]

    failures: list[tuple[Path, Exception]] = []
    processed = 0

    file_systems: list[ProjectFileSystem] = []

    # Live progress ----------------------------------------------------------
    with _make_progress() as progress:
        proj_task = progress.add_task("Projects", total=len(paths))

        for raw in paths:
            root = Path(raw).resolve()

            # ── establish a project‑scoped file‑system adapter ───────────────
            if root.is_file() and root.suffix == ".py":
                fs = fs_factory(root.parent)
                module_map = {root.relative_to(root.parent): root.read_text("utf-8")}
            elif root.is_dir():
                fs = fs_factory(root)
                module_map = fs.load_modules()
            else:
                logging.warning("Skipping %s (not a directory or .py file)", raw)
                progress.advance(proj_task)
                continue

            src_modules = [SourceModule(p, code) for p, code in module_map.items()]

            # ── inner bar: modules inside one project ────────────────────────
            mod_task = progress.add_task(f"[cyan]{root.name}", total=len(src_modules))

            updates = use_case.run(src_modules, style=doc_style)

            for mod, new_code in updates:
                rel_path = mod.path if isinstance(mod.path, Path) else Path(mod.path)
                try:
                    fs.stage_file(rel_path, new_code)
                except Exception as exc:
                    failures.append((rel_path, exc))
                    logging.exception("Failure in %s", rel_path, exc_info=exc)
                finally:
                    processed += 1
                    progress.advance(mod_task)
            file_systems.append(fs)

            progress.advance(proj_task)

    # Final summary ----------------------------------------------------------
    _summarize_failures(failures, processed)
    return file_systems
