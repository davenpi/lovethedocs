"""
Generate a validated `ModuleEdit` from a prompt.

This service is pure domain logic:

  Prompt ─► LLMClientPort ─► raw JSON ─► validator ─► ModuleEdit
"""

from __future__ import annotations

from typing import Protocol, Callable

from src.domain.docstyle.base import DocStyle
from src.domain.models import ModuleEdit


# --------------------------------------------------------------------------- #
#  Ports (minimal)                                                            #
# --------------------------------------------------------------------------- #
class LLMClientPort(Protocol):
    """Anything that can turn a prompt into JSON."""

    def request(self, prompt: str) -> dict:  # noqa: D401
        ...


class JSONSchemaValidator(Protocol):
    """Anything with .validate(raw_json) that raises on failure."""

    def validate(self, raw_json: dict) -> None:  # noqa: D401
        ...


# --------------------------------------------------------------------------- #
#  Type aliases                                                               #
# --------------------------------------------------------------------------- #
JSONToEditMapper = Callable[[dict], ModuleEdit]
LLMClientFactory = Callable[[str], LLMClientPort]  # factory(style) -> LLMClientPort


# --------------------------------------------------------------------------- #
#  Service                                                                    #
# --------------------------------------------------------------------------- #
class DocstringGeneratorService:
    """
    A *style-specific* generator.

    The chosen style is visible as `.style` and is passed once to the client
    factory when the service is constructed.
    """

    def __init__(
        self,
        *,
        style: str,
        client_factory: LLMClientFactory,
        validator: JSONSchemaValidator,
        mapper: JSONToEditMapper,
    ) -> None:
        self.style = style
        self._client = client_factory(style)  # binds style inside adapter
        self._validator = validator
        self._mapper = mapper

    # ------------------------------------------------------------------ #
    #  Public API                                                         #
    # ------------------------------------------------------------------ #
    def generate(self, prompt: str) -> ModuleEdit:
        raw = self._client.request(prompt)
        self._validator.validate(raw)
        return self._mapper(raw)
