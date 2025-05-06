"""
Concrete adapter that satisfies `LLMClientPort`.
"""

from __future__ import annotations

import json
from functools import lru_cache
from typing import Any

from dotenv import find_dotenv, load_dotenv
from openai import AsyncOpenAI, OpenAI, OpenAIError

from lovethedocs.domain.docstyle import DocStyle
from lovethedocs.domain.templates import PromptTemplateRepository
from lovethedocs.gateways.schema_loader import _RAW_SCHEMA


# --------------------------------------------------------------------------- #
#  One-time helpers                                                           #
# --------------------------------------------------------------------------- #
@lru_cache(maxsize=1)
def _get_sdk_client() -> OpenAI:
    """
    Return a cached synchronous OpenAI SDK client.

    Loads environment variables from a .env file if present. Raises a RuntimeError if
    the API key is missing.

    Returns
    -------
    OpenAI
        An instance of the OpenAI SDK client.
    Raises
    ------
    RuntimeError
        If the OpenAI API key is not found.
    """
    load_dotenv(find_dotenv(usecwd=True), override=False)

    try:
        return OpenAI()
    except OpenAIError as err:
        raise RuntimeError(
            "OpenAI API key not found. Set OPENAI_API_KEY or add it to a .env file "
            "in your project root (or any parent directory)."
            f"\n\nOriginal error:\n{err}"
        ) from err


# --------------------------------------------------------------------------- #
#  Asynchronous one-time helper                                              #
# --------------------------------------------------------------------------- #
@lru_cache(maxsize=1)
def _get_async_sdk_client() -> AsyncOpenAI:
    """
    Return a cached asynchronous OpenAI SDK client.

    Loads environment variables from a .env file if present. Raises a RuntimeError if
    the API key is missing.

    Returns
    -------
    AsyncOpenAI
        An instance of the asynchronous OpenAI SDK client.
    Raises
    ------
    RuntimeError
        If the OpenAI API key is not found.
    """
    load_dotenv(find_dotenv(usecwd=True), override=False)

    try:
        return AsyncOpenAI()
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
    Adapter for synchronous interaction with the OpenAI API using a fixed doc-style.

    Initializes the client with a specific documentation style and model. Provides a
    method to send requests and retrieve responses in a structured format.
    """

    def __init__(self, *, style: DocStyle, model: str = "gpt-4.1") -> None:
        """
        Initialize the OpenAIClientAdapter with a documentation style and model.

        Parameters
        ----------
        style : DocStyle
            The documentation style to use for requests.
        model : str, optional
            The OpenAI model to use (default is 'gpt-4.1').
        """
        self._style = style
        self._dev_prompt = _PROMPTS.get(style.name)
        self._model = model
        self._client = _get_sdk_client()

    def request(self, prompt: str) -> dict[str, Any]:
        """
        Send a prompt to the OpenAI API and return the parsed JSON response.

        Parameters
        ----------
        prompt : str
            The prompt to send to the OpenAI API.

        Returns
        -------
        dict[str, Any]
            The parsed JSON response from the API.
        """
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


# --------------------------------------------------------------------------- #
#  Async Adapter                                                              #
# --------------------------------------------------------------------------- #
class AsyncOpenAIClientAdapter:
    """
    Adapter for asynchronous interaction with the OpenAI API using a fixed doc-style.

    Provides an async method to send requests and retrieve responses concurrently.
    """

    def __init__(self, *, style: DocStyle, model: str = "gpt-4.1") -> None:
        """
        Initialize the AsyncOpenAIClientAdapter with a documentation style and model.

        Parameters
        ----------
        style : DocStyle
            The documentation style to use for requests.
        model : str, optional
            The OpenAI model to use (default is 'gpt-4.1').
        """
        self._style = style
        self._dev_prompt = _PROMPTS.get(style.name)
        self._model = model
        self._client = _get_async_sdk_client()

    async def request(self, prompt: str) -> dict[str, Any]:
        """
        Send a prompt asynchronously to the OpenAI API and return the JSON response.

        Parameters
        ----------
        prompt : str
            The prompt to send to the OpenAI API.

        Returns
        -------
        dict[str, Any]
            The parsed JSON response from the API.
        """
        response = await self._client.responses.create(
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
    def style(self) -> DocStyle:  # keep parity with sync adapter
        """
        The documentation style used by this client.

        Returns
        -------
        DocStyle
            The documentation style used by this client.
        """
        return self._style
