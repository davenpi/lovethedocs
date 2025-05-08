"""
Use-case: update documentation in a batch of modules.

Pure coordination for now:
    SourceModule ─► PromptBuilder ─► ModuleEditGenerator ─► ModulePatcher
No I/O, no logging, no retries.
"""

from __future__ import annotations

import asyncio
from typing import AsyncIterator, Iterable, Iterator

from lovethedocs.domain.docstyle.base import DocStyle
from lovethedocs.domain.models import SourceModule
from lovethedocs.domain.models.update_result import UpdateResult
from lovethedocs.domain.services import PromptBuilder
from lovethedocs.domain.services.generator import ModuleEditGenerator
from lovethedocs.domain.services.patcher import ModulePatcher


class DocumentationUpdateUseCase:
    """Coordinates batch documentation updates for modules."""

    def __init__(
        self,
        *,
        builder: PromptBuilder,
        generator: ModuleEditGenerator,
        patcher: ModulePatcher,
    ) -> None:
        """
        Initialize the DocumentationUpdateUseCase with required services.

        Parameters
        ----------
        builder : PromptBuilder
            Service to build prompts for documentation updates.
        generator : ModuleEditGenerator
            Service to generate documentation edits.
        patcher : ModulePatcher
            Service to apply generated edits to module source code.
        """
        self._builder = builder
        self._generator = generator
        self._patcher = patcher

    # The public API --------------------------------------------------------
    def run(
        self, modules: Iterable[SourceModule], *, style: DocStyle
    ) -> Iterator[UpdateResult]:
        """
        Iterate over modules and yield their updated source code.

        Parameters
        ----------
        modules : Iterable[SourceModule]
            Modules to update documentation for.
        style : DocStyle
            Documentation style to apply.

        Returns
        -------
        Iterator[UpdateResult]
            Iterator yielding results for each module, including updated code or
            errors.
        """
        user_prompts = self._builder.build(modules, style=style)

        for mod in modules:
            try:
                raw_edit = self._generator.generate(user_prompts[mod.path])
                new_code = self._patcher.apply(raw_edit, mod.code)
                yield UpdateResult(module=mod, new_code=new_code)
            except Exception as exc:
                yield UpdateResult(module=mod, new_code=None, error=exc)

        # ------------------------------------------------------------------ #

    #  Async API                                                         #
    # ------------------------------------------------------------------ #
    async def run_async(
        self, modules: Iterable[SourceModule], *, style: DocStyle, concurrency: int = 6
    ) -> AsyncIterator[UpdateResult]:
        """
        Asynchronously update documentation for modules with limited concurrency.

        Yields updated source code as each module finishes processing. Concurrency is
        capped by the `concurrency` parameter.

        Parameters
        ----------
        modules : Iterable[SourceModule]
            Modules to update documentation for.
        style : DocStyle
            Documentation style to apply.
        concurrency : int, optional
            Maximum number of concurrent updates (default is 6).

        Yields
        ------
        AsyncIterator[UpdateResult]
            Asynchronous iterator yielding results for each module.
        """
        user_prompts = self._builder.build(modules, style=style)
        sem = asyncio.Semaphore(concurrency)

        async def _job(mod: SourceModule) -> UpdateResult:
            """
            Process a single module asynchronously and return the update result.

            Parameters
            ----------
            mod : SourceModule
                The module to update.

            Returns
            -------
            UpdateResult
                Result containing the updated code or error for the module.
            """
            async with sem:
                try:
                    raw_edit = await self._generator.generate_async(
                        user_prompts[mod.path]
                    )
                    new_code = self._patcher.apply(raw_edit, mod.code)
                    return UpdateResult(module=mod, new_code=new_code)
                except Exception as exc:
                    return UpdateResult(module=mod, new_code=None, error=exc)

        for coro in asyncio.as_completed([_job(m) for m in modules]):
            yield await coro
