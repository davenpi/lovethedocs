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

        for path, prompt in prompts.items():
            print("-" * 80)
            print(f"Prompt for {path}:\n {prompt}")
            response_json = openai_client.request(prompt, model=settings.model_name)
            validator.validate(response_json)  # raise error if invalid

            module_edit = _create_module_edit_from_json(response_json)
            new_code = _write_new_code(modules, path, module_edit)
            print(f"New code for {path}: {new_code}")
            file_system.write_file(path, new_code, root=base)


def _create_module_edit_from_json(json_data):
    function_edits = [FunctionEdit(**f) for f in json_data["function_edits"]]
    class_edits = [
        ClassEdit(
            qualname=c["qualname"],
            docstring=c["docstring"],
            method_edits=[FunctionEdit(**m) for m in c["method_edits"]],
        )
        for c in json_data["class_edits"]
    ]
    return ModuleEdit(function_edits=function_edits, class_edits=class_edits)


def _write_new_code(modules, path, module_edit: ModuleEdit):
    edits_by_qual = module_edit.map_qnames_to_edits()
    patcher = DocSigPatcher(edits_by_qual)
    new_code = cst.parse_module(modules[path]).visit(patcher).code
    return new_code
