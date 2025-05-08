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
    """
    Generates validated ModuleEdit objects from prompts using an LLM client, schema
    validator, and mapping function.
    """

    def __init__(
        self,
        *,
        client: LLMClientPort,
        validator: JSONSchemaValidator,
        mapper: JSONToEditMapper,
    ) -> None:
        """
        Initializes the ModuleEditGenerator with a client, validator, and mapper.

        Parameters
        ----------
        client : LLMClientPort
            The LLM client used to generate raw JSON from prompts.
        validator : JSONSchemaValidator
            The validator used to check the raw JSON against a schema.
        mapper : JSONToEditMapper
            Function to map validated JSON to a ModuleEdit object.
        """
        self._client = client
        self._validator = validator
        self._mapper = mapper

    # ------------------------------------------------------------------ #
    #  Public API                                                         #
    # ------------------------------------------------------------------ #
    def generate(self, prompt: str) -> ModuleEdit:
        """
        Generate a validated ModuleEdit from a prompt synchronously.

        Parameters
        ----------
        prompt : str
            Fully-formed user prompt.

        Returns
        -------
        ModuleEdit
            Parsed and validated edit instructions.
        """
        raw = self._client.request(prompt)
        self._validator.validate(raw)
        return self._mapper(raw)

        # ------------------------------------------------------------------ #

    #  Async companion                                                   #
    # ------------------------------------------------------------------ #
    async def generate_async(self, prompt: str) -> ModuleEdit:
        """
        Asynchronously generate a validated ModuleEdit from a prompt.

        Calls an async-capable LLM client adapter in a non-blocking way. The validator
        and mapper logic are identical to the synchronous version.

        Parameters
        ----------
        prompt : str
            Fully-formed user prompt.

        Returns
        -------
        ModuleEdit
            Parsed and validated edit instructions.
        """
        raw = await self._client.request(prompt)  # type: ignore[attr-defined]
        self._validator.validate(raw)
        return self._mapper(raw)
