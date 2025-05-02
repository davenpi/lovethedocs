"""
Use-case: update documentation in a batch of modules.

Pure coordination for now:
    SourceModule ─► PromptBuilder ─► ModuleEditGenerator ─► ModulePatcher
No I/O, no logging, no retries.
"""

from __future__ import annotations

from typing import Iterable, Iterator, Tuple

from lovethedocs.domain.docstyle.base import DocStyle
from lovethedocs.domain.models import SourceModule
from lovethedocs.domain.services import PromptBuilder
from lovethedocs.domain.services.generator import ModuleEditGenerator
from lovethedocs.domain.services.patcher import ModulePatcher


class DocumentationUpdateUseCase:
    """High-level domain flow; yields (path, updated_code)."""

    def __init__(
        self,
        *,
        builder: PromptBuilder,
        generator: ModuleEditGenerator,
        patcher: ModulePatcher,
    ) -> None:
        self._builder = builder
        self._generator = generator
        self._patcher = patcher

    # The public API --------------------------------------------------------
    def run(
        self,
        modules: Iterable[SourceModule],
        *,
        style: DocStyle,
    ) -> Iterator[Tuple[SourceModule, str]]:
        """Iterate over modules and yield their updated source code."""
        user_prompts = self._builder.build(modules, style=style)

        for mod in modules:
            raw_edit = self._generator.generate(user_prompts[mod.path])
            new_code = self._patcher.apply(raw_edit, mod.code)
            yield mod, new_code
