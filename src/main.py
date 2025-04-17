"""
Main script to run `lovethedocs` on a given directory.
"""

import argparse
import sys

from openai import OpenAI
from utils import (
    API_KEY,
    edit_all_dirs,
)

# set up OpenAI client
client = OpenAI(api_key=API_KEY)

# get the file we want to analyze
parser = argparse.ArgumentParser()
parser.add_argument(
    "-p",
    "--path",
    type=str,
    help="Path to the directory containing the files to be analyzed.",
)

args = parser.parse_args()

path = args.path
if args.path is None:
    print("Please provide a path to the directory containing the files to be analyzed.")
    sys.exit(1)

# edit the code in the given path and all its subdirectories
edit_all_dirs(client, path)

print("Done!")
