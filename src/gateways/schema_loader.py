"""
Loads the JSON schema that defines the model's response format and exposes a reusable
jsonschema.Validator instance.
"""

import json
from pathlib import Path

from jsonschema import Draft202012Validator

_SCHEMAPATH = Path(__file__).with_name("lovethedocs_schema.json")

with _SCHEMAPATH.open("r") as fp:
    _RAW_SCHEMA = json.load(fp)

VALIDATOR = Draft202012Validator(_RAW_SCHEMA)

__all__ = ["_RAW_SCHEMA", "VALIDATOR"]
