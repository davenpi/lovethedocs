"""
Tiny wrapper so the rest of the code never imports openai directly.
"""

import json
from typing import Any

from openai import OpenAI
from dotenv import dotenv_values

from .schema_loader import _RAW_SCHEMA

config = dotenv_values(".env")

_DEV_PROMPT = """You are a documentation assistant. You're a master at this stuff.
You've put in the time and have the experience to know what good documentation looks
like. The work you're doing is extremely valuable. Here's a few things to keep in
mind:

- Follow PEP 257.
- Mimic the project's dominant docstring style (e.g., Google vs NumPy). If there are no
docs, use the NumPy style.
- Do not modify code—*only* return updated docstrings/examples inside the supplied JSON
schema. Put a type hinted signature in your 'signature' response key. Make sure to
include the ending colon.
- When a key is required by the schema but you have no content (e.g. no functions),
output an empty list [].
- If you see a quality docstring, don't change it. Quality means the docstring both
conforms to the dominant style and accurately describes the code it is associated with.
If the docstring isn't accurate or doesn't conform to the dominant style, then change
it.
- Try to respect the 88 character line length limit.
- Just respond with strings. Don't try to format the docstrings with triple quotes or
    indentation. Just return the string content.

You'll get a python module alongside the qualified names of the objects inside it.
It will look like this:

        ### Objects in this file:
        qualname1
        qualname2
        ...

        BEGIN <relative_path>
        <source_code>
        END <relative_path>

Remember, the work we are doing will save milllions of hours of time. You've spent
the time to learn how to do this well. Just follow the guildelines above and enjoy!
"""


client = OpenAI(api_key=config["OPENAI_API_KEY"])


def request(source_prompt: str, *, model: str = "gpt-4.1") -> dict[str, Any]:
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
    response_json = json.loads(response.output_text)
    print("Response JSON:", response_json)
    return response_json
