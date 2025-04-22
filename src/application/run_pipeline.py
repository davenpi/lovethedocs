"""
High-level orchestration. Glue code only.
"""

import timeit
import json
from pathlib import Path
from typing import Sequence
import sys

import tiktoken

from src.infra import file_system, openai_client, schema_loader
from . import config, prompt_builder
from src.domain import bundle_ops

encoding = tiktoken.encoding_for_model("gpt-4o")


def run_pipeline(paths: Sequence[str], settings: config.Settings = config.Settings()):
    validator = schema_loader.VALIDATOR

    for raw_path in paths:
        base = Path(raw_path)
        modules = file_system.load_modules(base)
        prompts = prompt_builder.build_prompts(modules)
        for rel_path, prompt in prompts.items():

            tokens = len(encoding.encode(prompt))
            print(f"Prompt tokens for {rel_path}: {tokens}")
            # time the model call
            start = timeit.default_timer()
            raw_json = openai_client.request(prompt, model=settings.model_name)
            elapsed = timeit.default_timer() - start
            print(f"Model call took {elapsed:.2f} seconds")
            validator.validate(raw_json)  # fail fast

            (base / "_improved").mkdir(exist_ok=True)
            (raw_json_path := base / "_improved" / "raw_response.json").write_text(
                json.dumps(raw_json, indent=2)
            )
            print(f"Saved model response to {raw_json_path}")

        # Phase‑0 adapter: expect {"module.py": "<code>", ...}
        edited_files = bundle_ops.flatten(raw_json)  # << was raw_json

        file_system.write_files(edited_files, base)
