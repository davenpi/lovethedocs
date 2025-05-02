"""
Concrete adapter that satisfies `LLMClientPort`.
"""

from __future__ import annotations

import json
from functools import lru_cache
from typing import Any

from dotenv import find_dotenv, load_dotenv
from openai import OpenAI, OpenAIError

from lovethedocs.domain.docstyle import DocStyle
from lovethedocs.domain.templates import PromptTemplateRepository
from lovethedocs.gateways.schema_loader import _RAW_SCHEMA


# --------------------------------------------------------------------------- #
#  One-time helpers                                                           #
# --------------------------------------------------------------------------- #
@lru_cache(maxsize=1)
def _get_sdk_client() -> OpenAI:
    load_dotenv(find_dotenv(usecwd=True), override=False)

    try:
        return OpenAI()
    except OpenAIError as err:
        raise RuntimeError(
            "OpenAI API key not found. Set OPENAI_API_KEY or add it to a .env file "
            "in your project root (or any parent directory)."
            f"\n\nOriginal error:\n{err}"
        ) from err


_PROMPTS = PromptTemplateRepository()  # cache inside class below


# --------------------------------------------------------------------------- #
#  Adapter                                                                    #
# --------------------------------------------------------------------------- #
class OpenAIClientAdapter:
    """
    Concrete implementation of `LLMClientPort`.

    The doc-style is chosen *once* at construction; callers never pass it again.
    """

    def __init__(self, *, style: DocStyle, model: str = "gpt-4.1") -> None:
        self._style = style
        self._dev_prompt = _PROMPTS.get(style.name)
        self._model = model
        self._client = _get_sdk_client()

    def request(self, prompt: str) -> dict[str, Any]:
        response = self._client.responses.create(
            model=self._model,
            instructions=self._dev_prompt,
            input=[{"role": "user", "content": prompt}],
            text={
                "format": {
                    "type": "json_schema",
                    "name": "code_documentation_edits",
                    "schema": _RAW_SCHEMA,
                    "strict": True,
                }
            },
            temperature=0,
        )
        return json.loads(response.output_text)

    @property
    def style(self) -> DocStyle:
        """
        The documentation style used by this client.

        Returns
        -------
        DocStyle
            The documentation style used by this client.
        """
        return self._style
