import json
from pprint import pprint

from dotenv import dotenv_values
import requests

from src.editor import CodeEditor

api_key = dotenv_values(".env")["OPENAI_API_KEY"]
headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

editor = CodeEditor(
    client=None,
    model="gpt-4.1",
    start_phrase="BEGIN lovethedocs",
    end_phrase="END lovethedocs",
)
# map eval name to eval id
eval_dict = {"eval_name": "eval_6802a45a12488190b435aaeb9afd1004"}

# Run eval
eval_run = {
    "name": "lovethedocs-formatting-discretion-run=2",
    "metadata": {"description": "First eval run"},
    "data_source": {
        "source": {"type": "file_id", "id": "file-KSv1MR7Z1MbZY9TSgwMPmA"},
        "type": "completions",
        "input_messages": {
            "template": [
                {
                    "role": "developer",
                    "content": editor.dev_prompt,
                },
                {
                    "role": "user",
                    "content": "{{item.input_content}}",
                },
            ],
            "type": "template",
        },
        "model": "gpt-4.1",
        "sampling_params": {
            "temperature": 0,
        },
    },
}

res = requests.post(
    f"https://api.openai.com/v1/evals/{eval_dict['eval_name']}/runs",
    headers=headers,
    data=json.dumps(eval_run),
)

# log the response
print(f"STATUS CODE: {res.status_code}")
print(f"RESPONSE:\n")
pprint(res.json(), indent=2)
