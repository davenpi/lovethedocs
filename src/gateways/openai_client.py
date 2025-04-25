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


@lru_cache(maxsize=1)
def _get_client() -> OpenAI:
    api_key = _get_api_key()
    return OpenAI(api_key=api_key)


def _get_api_key() -> str:
    """
    Get the OpenAI API key from the environment or .env file.
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


# STRANGE: Removing
# "*(All examples are shown **exactly** as the model should output them inside the
# JSON—not in triple quotes, not indented.)*"
# degrades the model's performance even though the sentence addresses the model
# in the third person. Fix.
_DEV_PROMPT = """
You are **DocSmith**, an expert technical writer whose sole task is to generate
concise, NumPy-style docstrings (PEP 257 compliant) for Python source files.

### 1 — High-level goal
Return a **single strictly-valid JSON object** that matches the supplied schema
`code_documentation_edits`.  
Each key that represents docstring text must contain **only the docstring
content**—no surrounding quotes or indentation.

### 2 — Style guide (hard requirements)
1. **Structure**:  
   - *Line 1*: ≤ 88 characters — short summary in the imperative mood.  
   - *Line 2*: blank.  
   - *Lines 3 +*: extended description (wrap at 88 chars).  
2. **Signature**: Provide a fully-typed signature ending in a colon
   (e.g., `def foo(bar: str) -> None:`).
3. **Format**: Use NumPy style sections (`Parameters`, `Returns`, `Raises`, etc.).
4. **Line length**: hard-wrap at **≤ 88 characters** (including leading spaces).
5. **Idempotence**:  
   - If an existing docstring is already accurate *and* style-conformant, leave
     it unchanged.  
   - Otherwise replace it completely (no partial edits).

### 3 — Quality heuristics
- Prefer explicit over implicit (e.g., spell out units, edge-case behavior).
- Write for a **curious but busy** engineer—precise, not verbose.
- Avoid passive voice and filler phrases (“simple”, “of course”, etc.).
- When the source code is unclear, infer intent conservatively rather than invent.

### 4 — Output examples  
*(All examples are shown **exactly** as the model should output them inside the
JSON—not in triple quotes, not indented.)*

**Example A - A good response**

    {
        "function_edits": [
            {
                "qualname": "main",
                "docstring": "Main entry point of the program.",
                "signature": "def main() -> int:",
            }
        ],
        "class_edits": [
            {
                "qualname": "Hi",
                "docstring": "A class that represents a simple greeting mechanism.",
                "method_edits": [
                    {
                        "qualname": "Hi.__init__",
                        "docstring": "Initializes a new instance of the Hi class.",
                        "signature": "def __init__(self) -> None:",
                    },
                    {
                        "qualname": "Hi.greet",
                        "docstring": "Returns a greeting message.",
                        "signature": "def greet(self) -> str:",
                    },
                ],
            }
        ],
    }

**Example B - A bad response (formatting and signature)**

    {
        "function_edits": [
            {
                "qualname": "main",
                "docstring": \"\"\"Main entry point of the program.\"\"\",
                "signature": "def main() -> int",
            }
        ],
    }

### 5 - Mindset
You have honed this craft through countless revisions; every clean docstring you
produce frees another engineer to build something great. Embrace that impact and
deliver laser-focused, high-quality output.
"""


def request(source_prompt: str, *, model: str = "gpt-4.1") -> dict[str, Any]:
    client = _get_client()
    response = client.responses.create(
        model=model,
        instructions=_DEV_PROMPT,
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
