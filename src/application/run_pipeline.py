"""
High-level orchestration. Glue code only.
"""

import json
from pathlib import Path
from typing import Sequence
import sys

import tiktoken
import libcst as cst

from src.infra import file_system, openai_client, schema_loader
from src.infra.ast_patcher import DocSigPatcher
from . import config, prompt_builder
from src.domain.models import ModuleEdit, FunctionEdit, ClassEdit

encoding = tiktoken.encoding_for_model("gpt-4o")


def run_pipeline(paths: Sequence[str], settings: config.Settings = config.Settings()):
    validator = schema_loader.VALIDATOR

    for raw_path in paths:
        base = Path(raw_path)
        modules = file_system.load_modules(base)  # dict[module_path, code]
        prompts = prompt_builder.build_prompts(modules)
        # keys = list(prompts.keys())
        # print(f"PROMPT FOR {base}:\n{prompts[keys[0]]}")

        for path, prompt in prompts.items():
            response_json = openai_client.request(prompt)
            # print(f"Response JSON for {path}: {json.dumps(response_json, indent=2)}")
            validator.validate(response_json)  # raise error if invalid
            # convert each function in the response list of functions to a FunctionEdit
            function_edits = [FunctionEdit(**f) for f in response_json["functions"]]
            class_edits = [ClassEdit(**c) for c in response_json["classes"]]
            # convert each class in the response list of classes to a ClassEdit
            module_edit = ModuleEdit(
                path=path,
                functions=function_edits,
                classes=class_edits,
            )
            # print(f"Module edit for {path}: {module_edit}")
            edits_by_qual = module_edit.edits_by_qualname()
            patcher = DocSigPatcher(edits_by_qual)
            new_code = cst.parse_module(modules[path]).visit(patcher).code
            # print(f"New code for {path}:\n{new_code}")
            file_system.write_file(path, new_code, root=base)
