import json
from pathlib import Path
from pprint import pprint

from dotenv import dotenv_values
import requests
from openai import OpenAI

from src.contracts import get_dev_prompt, DEFAULT_START_PHRASE, DEFAULT_END_PHRASE
from evalinfra.eval_config import EvalConfig


# --- Load credentials and set headers ---
api_key = dotenv_values(".env")["OPENAI_API_KEY"]
client = OpenAI(api_key=api_key)
headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}


# --- Step 1: Define your eval configuration ---
eval_config = EvalConfig(
    name="formatting-hello",
    data_source_config={
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
    testing_criteria=[
        {
            "type": "string_check",
            "name": "Match expected output exactly",
            "input": "{{sample.output_text}}",
            "operation": "eq",
            "reference": "{{item.expected_output}}",
        }
    ],
    metadata={
        "description": "A simple eval for matching text exactly.",
    },
)

# --- Step 2: Upload the dataset file ---
dataset_path = Path("evals/data/gen_formatting_discretion.jsonl")
with open(dataset_path, "rb") as f:
    file = client.files.create(file=f, purpose="evals")
file_id = file.id
print(f"✅ Uploaded dataset: file_id = {file_id}")
if file_id is None:
    print("❌ Dataset upload failed")
    exit(1)

# --- Step 3: Create the eval (optional: could check if it already exists) ---
eval_payload = eval_config.to_dict()
create_response = requests.post(
    "https://api.openai.com/v1/evals",
    headers=headers,
    data=json.dumps(eval_payload),
)

if create_response.status_code not in [200, 201]:
    print("❌ Eval creation failed")
    print(create_response.json())
    exit(1)

eval_id = create_response.json()["id"]
print(f"✅ Created eval: eval_id = {eval_id}")

# --- Step 4: Run the eval ---
editor_prompt = get_dev_prompt(DEFAULT_START_PHRASE, DEFAULT_END_PHRASE)

run_payload = {
    "name": eval_config.name + "-run=1",
    "metadata": {"description": "Initial run"},
    "data_source": {
        "source": {"type": "file_id", "id": file_id},
        "type": "completions",
        "input_messages": {
            "template": [
                {"role": "developer", "content": editor_prompt},
                {"role": "user", "content": "{{item.input_content}}"},
            ],
            "type": "template",
        },
        "model": "gpt-4.1",
        "sampling_params": {"temperature": 0},
    },
}

run_response = requests.post(
    f"https://api.openai.com/v1/evals/{eval_id}/runs",
    headers=headers,
    data=json.dumps(run_payload),
)

# --- Step 5: Print the result ---
print(f"STATUS CODE: {run_response.status_code}")
pprint(run_response.json())
