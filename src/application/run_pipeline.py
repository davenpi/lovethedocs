"""
High-level orchestration. Glue code only.
"""

import json
from pathlib import Path
from typing import Sequence

import tiktoken

from src.infra import file_system, openai_client, schema_loader
from . import build_prompt, config
from src.domain import bundle_ops

encoding = tiktoken.encoding_for_model("gpt-4o")


def run_pipeline(paths: Sequence[str], settings: config.Settings = config.Settings()):
    validator = schema_loader.VALIDATOR

    for raw_path in paths:
        base = Path(raw_path)
        source_blob = file_system.concatenate_modules(base)
        prompt = build_prompt.build_prompt(source_blob)
        tokens = len(encoding.encode(prompt))
        print(f"Prompt tokens: {tokens}")
        if tokens > 4096:
            print(f"Prompt too long: {tokens} tokens")
            raise ValueError(
                f"Prompt too long: {tokens} tokens. "
                "Please reduce the size of the input files."
            )

        raw_json = openai_client.request(prompt, model=settings.model_name)
        validator.validate(raw_json)  # fail fast
        for mod in raw_json["modules"]:
            if not mod.get("qualname"):
                rel = Path(mod["path"]).with_suffix("")  # remove .py
                mod["qualname"] = str(rel).replace("/", ".")  # foo/bar → foo.bar
        (base / "_improved").mkdir(exist_ok=True)
        (raw_json_path := base / "_improved" / "raw_response.json").write_text(
            json.dumps(raw_json, indent=2)
        )
        print(f"Saved model response to {raw_json_path}")

        # Phase‑0 adapter: expect {"module.py": "<code>", ...}
        edited_files = bundle_ops.flatten(raw_json)  # << was raw_json

        file_system.write_files(edited_files, base)
