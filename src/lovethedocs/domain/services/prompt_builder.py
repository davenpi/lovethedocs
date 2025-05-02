"""
Build *user* prompts for every SourceModule.

Pure domain logic—no I/O, no network, no OpenAI SDK calls.
The gateway will prepend the system prompt; here we only construct
the per-file user prompt that lists objects and embeds the source code.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Sequence

from lovethedocs.domain.docstyle.base import DocStyle  # type: ignore
from lovethedocs.domain.models import SourceModule
from lovethedocs.domain.templates import PromptTemplateRepository


class PromptBuilder:
    """
    Compose user-prompts for a collection of modules.

    Parameters
    ----------
    templates : PromptTemplateRepository
        Used mainly for `templates.get(style.name)` so we could (later)
        embed few-shot examples or hints inside the user prompt. We don’t
        use that text yet, but the dependency keeps wiring simple.
    """

    def __init__(self, templates: PromptTemplateRepository) -> None:
        self._templates = templates

    # ------------------------------------------------------------------ #
    #  Public API                                                         #
    # ------------------------------------------------------------------ #
    def build(
        self,
        modules: Sequence[SourceModule],
        *,
        style: DocStyle,
    ) -> Dict[Path, str]:
        """
        Return a mapping ``{module.path: user_prompt}``.

        The format matches the previous builder, so the gateway can switch
        over without behavioural change.
        """
        prompts: Dict[Path, str] = {}

        # We fetch the style’s template once—even if unused for now—to keep
        # the call signature stable when we later add style-specific hints.
        _ = self._templates.get(style.name)

        for mod in modules:
            header = (
                f"### Objects in {mod.path}:\n"
                + "\n".join(f"  {qn}" for qn in mod.objects)
                + "\n\n"
            )
            body = f"BEGIN {mod.path}\n{mod.code.strip()}\nEND {mod.path}"
            prompts[mod.path] = header + body

        return prompts
