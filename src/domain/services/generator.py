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
# In domain/services/generator.py - Update the LLMClientPort
class LLMClientPort(Protocol):
    """Turns a prompt into JSON using a specific documentation style."""

    @property
    def style(self) -> DocStyle:
        """The documentation style used by this client."""
        ...

    def request(self, prompt: str) -> dict:
        """Convert a prompt to a JSON response using the client's style."""
        ...


class JSONSchemaValidator(Protocol):
    """Implements a .validate(raw_json) that raises on failure."""

    def validate(self, raw_json: dict) -> None:  # noqa: D401
        ...


# --------------------------------------------------------------------------- #
#  Type aliases                                                               #
# --------------------------------------------------------------------------- #
JSONToEditMapper = Callable[[dict], ModuleEdit]


# --------------------------------------------------------------------------- #
#  Service                                                                    #
# --------------------------------------------------------------------------- #
class ModuleEditGenerator:

    def __init__(
        self,
        *,
        client: LLMClientPort,
        validator: JSONSchemaValidator,
        mapper: JSONToEditMapper,
    ) -> None:
        self._client = client
        self._validator = validator
        self._mapper = mapper

    # ------------------------------------------------------------------ #
    #  Public API                                                         #
    # ------------------------------------------------------------------ #
    def generate(self, prompt: str) -> ModuleEdit:
        raw = self._client.request(prompt)
        self._validator.validate(raw)
        return self._mapper(raw)
