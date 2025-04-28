"""
Tiny wrapper so the rest of the code never imports openai directly.
"""

from functools import lru_cache
import json
import os
from pathlib import Path
from typing import Any

from openai import OpenAI
from dotenv import load_dotenv

from .schema_loader import _RAW_SCHEMA
from src.domain.templates import PromptTemplateRepository


@lru_cache(maxsize=1)
def _get_client() -> OpenAI:
    """
    Return a cached OpenAI client instance using the API key from the environment.

    Uses LRU caching to ensure only one client instance is created per process.

    Returns
    -------
    OpenAI
        An instance of the OpenAI client initialized with the API key.
    """
    api_key = _get_api_key()
    return OpenAI(api_key=api_key)


def _get_api_key() -> str:
    """
    Retrieve the OpenAI API key from the environment or a .env file.

    Checks the environment variable 'OPENAI_API_KEY'. If not found, attempts to load
    it from a .env file located in the project root or its parent directory. Raises an
    error if the key is not found.

    Returns
    -------
    str
        The OpenAI API key as a string.

    Raises
    ------
    RuntimeError
        If the API key is not found in the environment or .env file.
    """
    # Check if the API key is already set in the environment
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        # Look for .env file in the current directory or parent directories
        project_root = Path(__file__).resolve().parent.parent  # /abs_path/to/src
        for candidate in [project_root / ".env", project_root.parent / ".env"]:
            if candidate.exists():
                load_dotenv(candidate)  # Load the .env file into the environment
                api_key = os.getenv("OPENAI_API_KEY")
                break
    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY not found. "
            "Set it in the environment or in a .env file at project root."
        )
    return api_key


_prompt_template_repo = PromptTemplateRepository()


def request(
    source_prompt: str,
    *,
    style: str = "numpy",
    model: str = "gpt-4.1",
) -> dict[str, Any]:
    """
    Send a prompt to the OpenAI API and return the parsed JSON response.

    Uses the specified model to generate a response according to the developer prompt
    and schema. The response is parsed from JSON and returned as a dictionary.

    Parameters
    ----------
    source_prompt : str
        The user prompt to send to the OpenAI API.
    model : str, optional
        The model name to use for the request (default is 'gpt-4.1').

    Returns
    -------
    dict[str, Any]
        The parsed JSON response from the OpenAI API.
    """
    client = _get_client()
    dev_prompt = _prompt_template_repo.get(style)
    response = client.responses.create(
        model=model,
        instructions=dev_prompt,
        input=[
            {"role": "user", "content": source_prompt},
        ],
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
    response_json = json.loads(response.output_text)
    return response_json
