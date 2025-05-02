"""
Generate a validated `ModuleEdit` from a prompt.

This service is pure domain logic:

  Prompt ─► LLMClientPort ─► raw JSON ─► validator ─► ModuleEdit
"""

from __future__ import annotations

from typing import Callable

from lovethedocs.domain.models import ModuleEdit
from lovethedocs.domain.ports import JSONSchemaValidator, LLMClientPort

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
