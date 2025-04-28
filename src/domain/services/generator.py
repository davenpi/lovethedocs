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
    """The only method the generator cares about."""

    def request(self, prompt: str, *, style: str) -> dict:  # noqa: D401
        ...


class JSONValidator(Protocol):
    """Anything with .validate(raw_json) that raises on failure."""

    def validate(self, raw_json: dict) -> None:  # noqa: D401
        ...


# --------------------------------------------------------------------------- #
#  Mapper                                                                     #
# --------------------------------------------------------------------------- #
# Type alias so callers can inject existing mappers.map_json_to_module_edit
JSONToEditMapper = Callable[[dict], ModuleEdit]


# --------------------------------------------------------------------------- #
#  Service                                                                    #
# --------------------------------------------------------------------------- #
class DocstringGeneratorService:
    """
    Coordinates model call + schema validation + mapping to `ModuleEdit`.
    """

    def __init__(
        self,
        *,
        client: LLMClientPort,
        validator: JSONValidator,
        mapper: JSONToEditMapper,
        style: DocStyle,
    ) -> None:
        self._client = client
        self._validator = validator
        self._mapper = mapper
        self._style = style

    # ------------------------------------------------------------------ #
    #  Public API                                                         #
    # ------------------------------------------------------------------ #
    def generate(self, prompt: str) -> ModuleEdit:
        """
        Return a fully-typed `ModuleEdit`, or propagate any errors.

        Raises
        ------
        ValidationError
            If the JSON schema check fails (comes from validator).
        Exception
            Any exception bubble-ups from the client port.
        """
        raw = self._client.request(prompt, style=self._style.name)
        self._validator.validate(raw)
        return self._mapper(raw)
