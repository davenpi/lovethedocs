"""
Glue code to run the pipeline.
"""

from pathlib import Path
from typing import Sequence

from src import ports
from src.application import config, mappers, prompt_builder, services
from src.gateways import file_system as fs_gateway
from src.gateways import openai_client as ai_gateway
from src.gateways import schema_loader


def run_pipeline(
    paths: Sequence[str],
    *,
    settings: config.Settings = config.Settings(),
    ai_client: ports.AIClientPort = ai_gateway,  # defaults to real gateway
    file_writer: ports.FileWriterPort = fs_gateway,  # defaults to real gateway
):
    validator = schema_loader.VALIDATOR

    for raw_path in paths:
        base = Path(raw_path)
        modules = file_writer.load_modules(base)
        prompts = prompt_builder.build_prompts(modules)

        for path, prompt in prompts.items():
            resp_json = ai_client.request(prompt, model=settings.model_name)
            validator.validate(resp_json)

            module_edit = mappers.create_module_edit_from_json(resp_json)
            new_code = services.write_new_code(modules[path], module_edit)
            file_writer.write_file(path, new_code, root=base)
