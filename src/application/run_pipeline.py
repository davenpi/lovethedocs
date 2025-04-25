"""
Glue code to run the pipeline.
"""

import json
import logging
from pathlib import Path
from typing import Iterable, Sequence

from black import FileMode, format_str
from tqdm import tqdm

from src import ports
from src.application import config, mappers, prompt_builder, services, utils
from src.application import logging_setup  # noqa: F401  (import side-effects only)

from src.gateways import file_system as fs_gateway
from src.gateways import openai_client as ai_gateway
from src.gateways import schema_loader


def _summarize_and_log_failures(
    failures: Iterable[tuple[Path, Exception]], processed: int
) -> None:
    """
    Summarize and log failures encountered during module processing.

    Prints a summary of successful and failed modules to the console, writes details of
    failures to 'failed_modules.json', and logs full exception tracebacks to 'pipeline.log'.
    If there are no failures, prints a success message.

    Parameters
    ----------
    failures : Iterable[tuple[Path, Exception]]
        An iterable of (Path, Exception) tuples representing failed modules and their
        associated exceptions.
    processed : int
        The total number of modules processed.
    """
    failures = list(failures)  # exhaust any iterator
    if not failures:
        print("✓ All modules processed without errors.")
        return

    # ----- console summary -----
    ok = processed - len(failures)
    print(f"\n✓ {ok} modules updated   |   ✗ {len(failures)} failed")
    print("See failed_modules.json for details.")

    # ----- JSON dump -----
    payload = [{"module": str(path), "error": str(exc)} for path, exc in failures]
    with open("failed_modules.json", "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2)

    # ----- full tracebacks in log -----
    for path, exc in failures:
        logging.exception("Failure in %s", path, exc_info=exc)


# ------- main pipeline function ---------------------------------------------
def run_pipeline(
    paths: Sequence[str],
    *,
    settings: config.Settings = config.Settings(),
    ai_client: ports.AIClientPort = ai_gateway,
    file_writer: ports.FileWriterPort = fs_gateway,
):
    """
    Run the documentation update pipeline for a sequence of module paths.

    Loads modules, builds prompts, requests AI-generated documentation edits, validates
    responses, updates module files, and logs any failures. At the end, writes a summary of
    failures.

    Parameters
    ----------
    paths : Sequence[str]
        A sequence of string paths to the codebase roots to process.
    settings : config.Settings, optional
        Pipeline configuration settings (default is a new Settings instance).
    ai_client : ports.AIClientPort, optional
        AI client port for making requests (default is the OpenAI gateway).
    file_writer : ports.FileWriterPort, optional
        File writer port for loading and writing modules (default is the file system
        gateway).
    """
    validator = schema_loader.VALIDATOR
    failures: list[tuple[Path, Exception]] = []
    processed = 0

    for raw_path in tqdm(paths, desc="Paths", unit="pkg"):
        base = Path(raw_path)
        modules = file_writer.load_modules(base)
        prompts = prompt_builder.build_prompts(modules)

        for path, prompt in tqdm(
            prompts.items(), desc="Modulues", unit="mod", leave=False
        ):
            processed += 1
            resp_json = ai_client.request(prompt, model=settings.model_name)
            try:

                validator.validate(resp_json)

                module_edit = mappers.map_json_to_module_edit(resp_json)
                updated_code = services.update_module_docs(
                    old_module_source=modules[path], module_edit=module_edit
                )
                updated_code = utils.apply_formatter(
                    updated_code,
                    lambda code: format_str(code, mode=FileMode()),
                )
                file_writer.write_file(path, updated_code, root=base)
            except Exception as exc:
                print(f"Response JSON: {json.dumps(resp_json, indent=2)}")
                failures.append((path, exc))
                print(f"x {path} -> {exc}")
    _summarize_and_log_failures(failures, processed)
