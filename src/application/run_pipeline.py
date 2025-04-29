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

import json
import logging
from pathlib import Path
from typing import Iterable, Sequence, Union

from black import FileMode, format_str
from tqdm import tqdm

from src import ports
from src.application import config, logging_setup  # side-effects only
from src.application.diff_review import batch_review
from src.application import utils
from src.gateways import schema_loader
from src.gateways.openai_client import OpenAIClientAdapter
from src.application import mappers
from src.gateways import file_system as fs_gateway
from src.gateways import schema_loader

from src.domain.docstyle.numpy_style import NumPyDocStyle
from src.domain.models import SourceModule
from src.domain.services import PromptBuilder
from src.domain.templates import PromptTemplateRepository
from src.domain.use_cases.update_docs import (
    DocumentationUpdateUseCase,
)
from src.domain.services.generator import ModuleEditGenerator
from src.domain.services.patcher import ModulePatcher

# --------------------------------------------------------------------------- #
#  One-time construction of the pure, stateless services                      #
# --------------------------------------------------------------------------- #


def openai_factory(style: str):
    return OpenAIClientAdapter(style=style)  # <- style locked in


numpy_generator = ModuleEditGenerator(
    style="numpy",
    client_factory=openai_factory,
    validator=schema_loader.VALIDATOR,
    mapper=mappers.map_json_to_module_edit,
)
_BUILDER = PromptBuilder(PromptTemplateRepository())
_USES = DocumentationUpdateUseCase(
    builder=_BUILDER,
    generator=numpy_generator,
    patcher=ModulePatcher(),
)


# --------------------------------------------------------------------------- #
#  Helpers                                                                    #
# --------------------------------------------------------------------------- #
def _summarize_failures(
    failures: Iterable[tuple[Path, Exception]], processed: int
) -> None:
    failures = list(failures)
    if not failures:
        print("✓ All modules processed without errors.")
        return

    ok = processed - len(failures)
    print(f"\n✓ {ok} modules updated   |   ✗ {len(failures)} failed")
    print("See failed_modules.json for details.")

    payload = [{"module": str(p), "error": str(e)} for p, e in failures]
    Path("failed_modules.json").write_text(json.dumps(payload, indent=2))

    for p, e in failures:
        logging.exception("Failure in %s", p, exc_info=e)


# --------------------------------------------------------------------------- #
#  Public adapter                                                             #
# --------------------------------------------------------------------------- #
def run_pipeline(
    paths: Union[str, Path, Sequence[Union[str, Path]]],
    *,
    file_writer: ports.FileWriterPort = fs_gateway,
    review_diffs: bool = False,
) -> None:
    """
    High-level CLI entry: update documentation for every `.py` file
    under the given path(s).

    Parameters
    ----------
    paths
        Directory, single file, or a sequence of both.
    settings
        Model name, temperature, etc.
    ai_client
        Gateway that speaks to the LLM (defaults to OpenAI wrapper).
    file_writer
        Gateway that loads and writes files on disk.
    review_diffs
        If True, open VS Code diff view when finished.
    """
    if isinstance(paths, (str, Path)):
        paths = [paths]  # type: ignore[list-item]

    failures: list[tuple[Path, Exception]] = []
    processed = 0

    for raw in tqdm(paths, desc="Paths", unit="pkg"):
        root = Path(raw)

        # ----- load modules -------------------------------------------------
        if root.is_dir():
            module_map = file_writer.load_modules(root)
        elif root.is_file() and root.suffix == ".py":
            module_map = {root.relative_to(root.parent): root.read_text("utf-8")}
            root = root.parent
        else:
            logging.warning("Skipping %s (not a directory or .py file)", root)
            continue

        src_modules = [SourceModule(p, code) for p, code in module_map.items()]

        # ----- call domain use-case ----------------------------------------

        updates = _USES.run(src_modules, style=NumPyDocStyle())

        for mod, new_code in tqdm(updates, desc="Modules", unit="mod", leave=False):
            processed += 1
            try:
                new_code = utils.apply_formatter(
                    new_code, lambda s: format_str(s, mode=FileMode())
                )
                file_writer.write_file(mod.path, new_code, root=root)
            except Exception as exc:
                failures.append((mod.path, exc))
                print(f"x {mod.path} -> {exc}")

    _summarize_failures(failures, processed)

    if review_diffs:
        print("\nReviewing generated documentation…")
        for p in paths if isinstance(paths, Sequence) else [paths]:
            batch_review(p)
