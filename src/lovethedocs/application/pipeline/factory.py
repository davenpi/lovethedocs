"""
Utilities for constructing fully-wired use-case instances.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from lovethedocs.application import config, mappers
from lovethedocs.domain import docstyle
from lovethedocs.domain.services import PromptBuilder
from lovethedocs.domain.services.generator import ModuleEditGenerator
from lovethedocs.domain.services.patcher import ModulePatcher
from lovethedocs.domain.templates import PromptTemplateRepository
from lovethedocs.domain.use_cases.update_docs import DocumentationUpdateUseCase
from lovethedocs.gateways import schema_loader
from lovethedocs.gateways.openai_client import (
    AsyncOpenAIClientAdapter,
    OpenAIClientAdapter,
)
from lovethedocs.gateways.project_file_system import ProjectFileSystem


@lru_cache
def make_use_case(*, async_mode: bool = False) -> DocumentationUpdateUseCase:
    """
    Return a configured DocumentationUpdateUseCase.

    Cached so repeated calls share the same heavy objects.
    """
    cfg = config.Settings()
    style = docstyle.DocStyle.from_string(cfg.doc_style)
    Client = AsyncOpenAIClientAdapter if async_mode else OpenAIClientAdapter

    generator = ModuleEditGenerator(
        client=Client(model=cfg.model, style=style),
        validator=schema_loader.VALIDATOR,
        mapper=mappers.map_json_to_module_edit,
    )

    builder = PromptBuilder(PromptTemplateRepository())

    return DocumentationUpdateUseCase(
        builder=builder,
        generator=generator,
        patcher=ModulePatcher(),
    )


def fs_factory(root: Path) -> ProjectFileSystem:
    """
    Create a `ProjectFileSystem` instance for the specified root directory.

    Parameters
    ----------
    root : Path
        The root directory for the project file system.

    Returns
    -------
    ProjectFileSystem
        An instance of `ProjectFileSystem` rooted at the given directory.
    """

    return ProjectFileSystem(root)
