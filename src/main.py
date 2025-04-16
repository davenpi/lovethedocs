"""
This modules analysize a file and generates the same code with improved documentation.
For now we will follow the docstring style of Kenneth Reitz/pandas.
"""

import argparse
import os
import sys

from openai import OpenAI
from utils import API_KEY, DEV_PROMPT, strip_format


# get the file we want to analyze
parser = argparse.ArgumentParser()
parser.add_argument(
    "-f",
    "--file",
    type=str,
    help="Path to the file containing the code to be analyzed.",
)
args = parser.parse_args()
if args.file is None:
    print("Please provide a file to analyze.")
    sys.exit(1)

# set up OpenAI client
client = OpenAI(api_key=API_KEY)


# read the file
input_file = args.file
with open(input_file, "r") as f:
    code = f.read()

print("-" * 20)
print(f"Code to be analyzed:\n{code}")
print("-" * 20)


# pass the file to gpt for analysis
response = client.responses.create(
    model="gpt-4o-mini",
    instructions=DEV_PROMPT,
    input=[{"role": "user", "content": code}],
    temperature=0,
)


# write the response to a file

print("-" * 20)
print(f"Response from OpenAI:\n{response.output[0].content[0].text}")
print("-" * 20)

output_file = os.path.splitext(input_file)[0] + "_improved.py"
formatted_code = strip_format(response.output[0].content[0].text)
with open(output_file, "w") as f:
    f.write(formatted_code)
print(f"Improved code written to {output_file}")
