"""
Tiny helpers that run a single-module update and never raise.
"""

import asyncio
import logging
from typing import Tuple

from lovethedocs.domain import docstyle
from lovethedocs.domain.models import SourceModule
from lovethedocs.domain.use_cases.update_docs import DocumentationUpdateUseCase

Result = Tuple[SourceModule, str | None, Exception | None]


def safe_update(
    use_case: DocumentationUpdateUseCase,
    module: SourceModule,
    *,
    style: docstyle.DocStyle,
) -> Result:
    """Synchronous wrapper."""
    try:
        [(mod, new_code)] = use_case.run([module], style=style)
        return mod, new_code, None
    except Exception as exc:  # noqa: BLE001
        logging.exception("Failure in %s", module.path, exc_info=exc)
        return module, None, exc


async def safe_update_async(
    use_case: DocumentationUpdateUseCase,
    module: SourceModule,
    *,
    style: docstyle.DocStyle,
    sem: asyncio.Semaphore,
) -> Result:
    """Async wrapper honouring a global semaphore."""

    async with sem:
        try:
            async for mod, new_code in use_case.run_async(
                [module], style=style, concurrency=1
            ):
                return mod, new_code, None
        except Exception as exc:
            logging.exception("Failure in %s", module.path, exc_info=exc)
            return module, None, exc
