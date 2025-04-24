"""
High-level orchestration. Glue code only.
"""

from pathlib import Path
from typing import Sequence

from src.gateways import file_system, openai_client, schema_loader
from . import config, mappers, prompt_builder, services


def run_pipeline(paths: Sequence[str], settings: config.Settings = config.Settings()):
    validator = schema_loader.VALIDATOR

    for raw_path in paths:
        base = Path(raw_path)
        modules = file_system.load_modules(base)  # dict[module_path, code]
        prompts = prompt_builder.build_prompts(modules)

        for path, prompt in prompts.items():
            print("-" * 80)
            print(f"Prompt for {path}:\n {prompt}")
            resp_json = openai_client.request(prompt, model=settings.model_name)
            validator.validate(resp_json)  # raise error if invalid

            # module_edit = _create_module_edit_from_json(resp_json)
            module_edit = mappers.create_module_edit_from_json(resp_json)
            new_code = services.write_new_code(
                old_code=modules[path], module_edit=module_edit
            )
            print(f"New code for {path}: {new_code}")
            file_system.write_file(path, new_code, root=base)
