"""
Module to create and run evals for the `lovethedocs` project.
"""

import json

import requests
from dotenv import dotenv_values

config = dotenv_values(".env")
API_KEY = config["OPENAI_API_KEY"]
headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

# Create a new eval

eval_payload = {
    "name": "lovethedocs-formatting-discretion",
    "data_source_config": {
        "type": "custom",
        "item_schema": {
            "type": "object",
            "properties": {
                "input_content": {"type": "string"},
                "expected_output": {"type": "string"},
            },
            "required": ["input_content", "expected_output"],
        },
        "include_sample_schema": True,
    },
    "testing_criteria": [
        {
            "type": "string_check",
            "name": "Match expected output exactly",
            "input": "{{sample.output_text}}",
            "operation": "eq",
            "reference": "{{item.expected_output}}",
        }
    ],
    "metadata": {
        "description": "A simple eval for matching text exactly.",
    },
}

# Upload the eval
response = requests.post(
    "https://api.openai.com/v1/evals", headers=headers, data=json.dumps(eval_payload)
)

if response:
    print("Eval created successfully.")
    print("Response:", response.json())
else:
    print("Failed to create eval.")
    print(response)
