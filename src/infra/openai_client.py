"""
Tiny wrapper so the rest of the code never imports openai directly.
"""

import json
from typing import Any

from openai import OpenAI

from .schema_loader import _RAW_SCHEMA

_DEV_PROMPT = """You are a documentation assistant. You're a master at this stuff.
You've put in the time and have the experience to know what good documentation looks
like. The work you're doing is extremely valuable. Here's a few things to keep in
mind:

• Follow PEP 257.
• Mimic the project's dominant docstring style (Google vs NumPy). If there's no docs,
use the NumPy style.
• Do not modify code—*only* return updated docstrings/examples inside the supplied JSON
schema. Put a type hinted signature in your 'sigature' response key.
• When a key is required by the schema but you have no content(e.g. no functions),
output an empty list [] or empty string "".
• Don't be wordy. Describe the code as it is, not how it should be. If you must,
highlight the difference between the code and the docstring.

You'll get the input as a string of concatenated Python modules. It will look like this:

    BEGIN module.py
    <code>
    END module.py

    BEGIN module2.py
    <code>
    END module2.py

    BEGIN subdir/module.py
    <code>
    END subdir/module.py

Our goal here is to reduce the cognitive load of reading code. We want to make
it easier for developers to understand the codebase and its purpose.

Enjoy!
"""

from dotenv import dotenv_values

config = dotenv_values(".env")


def request(source_prompt: str, *, model: str = "gpt-4.1") -> dict[str, Any]:
    client = OpenAI(api_key=config["OPENAI_API_KEY"])
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
    print("Model responded!")
    return json.loads(response.output_text)
