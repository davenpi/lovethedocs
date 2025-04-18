# Assume we run this script from the root directory of the project.
from pprint import pprint


# print the directory the interpreter is running in
from openai import OpenAI
from dotenv import dotenv_values

config = dotenv_values(".env")


client = OpenAI(api_key=config["OPENAI_API_KEY"])

with open("evals/hello_eval.jsonl", "rb") as f:
    file = client.files.create(
        file=f,
        purpose="evals",
    )

pprint(file, indent=2)
