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
from typing import Callable, Iterable, Sequence, Union

from black import FileMode, format_str
from tqdm import tqdm

from src.application import logging_setup  # noqa: F401
from src.application import config, diff_review, mappers, utils
from src.domain import docstyle
from src.domain.models import SourceModule
from src.domain.services import PromptBuilder
from src.domain.services.generator import ModuleEditGenerator
from src.domain.services.patcher import ModulePatcher
from src.domain.templates import PromptTemplateRepository
from src.domain.use_cases.update_docs import DocumentationUpdateUseCase
from src.gateways import schema_loader
from src.gateways.openai_client import OpenAIClientAdapter
from src.gateways.project_file_system import ProjectFileSystem
from src.gateways.vscode_diff_viewer import VSCodeDiffViewer

# --------------------------------------------------------------------------- #
#  One-time construction of the pure, stateless services                      #
# --------------------------------------------------------------------------- #

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
    paths: Union[str | Path, Sequence[str | Path]],
    *,
    fs_factory: Callable[[Path], ProjectFileSystem] = utils.fs_factory,
    use_case: DocumentationUpdateUseCase = _USES,
    review_diffs: bool = False,
) -> None:
    """
    High-level CLI entry: update documentation for every *.py file
    under the given path(s).

    `paths` may be a mix of files and directories.
    """

    if isinstance(paths, (str, Path)):
        paths = [paths]  # type: ignore[list-item]

    failures: list[tuple[Path, Exception]] = []
    processed = 0

    for raw in tqdm(paths, desc="Projects", unit="pkg"):
        root = Path(raw).resolve()

        # --- establish a project-scoped file-system adapter ----------------
        if root.is_file() and root.suffix == ".py":
            # Single-file run: project root is the file’s parent
            fs = fs_factory(root.parent)
            module_map = {root.relative_to(root.parent): root.read_text("utf-8")}
        elif root.is_dir():
            fs = fs_factory(root)
            module_map = fs.load_modules()
        else:
            logging.warning("Skipping %s (not a directory or .py file)", raw)
            continue

        src_modules = [SourceModule(p, code) for p, code in module_map.items()]

        # --- call domain use-case -----------------------------------------
        updates = use_case.run(src_modules, style=doc_style)

        for mod, new_code in tqdm(updates, desc="Modules", unit="mod", leave=False):
            processed += 1
            try:
                rel_path = mod.path if isinstance(mod.path, Path) else Path(mod.path)
                fs.stage_file(rel_path, new_code)
            except Exception as exc:
                failures.append((rel_path, exc))
                print(f"x {rel_path} -> {exc}")

        # --- optional manual review for this project ----------------------
        if review_diffs:
            print("\nReviewing generated documentation…")
            diff_review.batch_review(
                fs,
                diff_viewer=VSCodeDiffViewer(),
                interactive=True,  # set False for CI
            )

    _summarize_failures(failures, processed)
