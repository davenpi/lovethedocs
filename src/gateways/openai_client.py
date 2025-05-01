"""
Concrete adapter that satisfies `LLMClientPort`.
"""

from __future__ import annotations

import json
import os
from functools import lru_cache
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI

from src.domain.docstyle import DocStyle
from src.domain.templates import PromptTemplateRepository

from .schema_loader import _RAW_SCHEMA


# --------------------------------------------------------------------------- #
#  One-time helpers                                                           #
# --------------------------------------------------------------------------- #
@lru_cache(maxsize=1)
def _get_sdk_client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:  # fallback → .env search
        project_root = Path(__file__).resolve().parents[1]
        for candidate in (project_root / ".env", project_root.parent / ".env"):
            if candidate.exists():
                load_dotenv(candidate)
                api_key = os.getenv("OPENAI_API_KEY")
                break
    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY not found in env or .env file at project root."
        )
    return OpenAI(api_key=api_key)


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
