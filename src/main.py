"""
Main script to run `lovethedocs` on a given directory.
"""

import argparse
from dotenv import dotenv_values
from pathlib import Path

from openai import OpenAI

from src.editor import CodeEditor
from src import utils


def edit_all_dirs(editor: CodeEditor, path: str | Path) -> None:
    """
    Edit all Python modules in the given directory and its subdirectories.

    Parameters
    ----------
    editor : CodeEditor
        The CodeEditor instance to use for editing.
    path : str | Path
        The path to the directory to process.

    Returns
    -------
    None
    """
    base = Path(path)
    editor.process_directory(base)
    for subdir in utils._iter_project_dirs(base):
        editor.process_directory(subdir)


config = dotenv_values(".env")

parser = argparse.ArgumentParser()
parser.add_argument(
    "-p",
    "--path",
    type=str,
    required=True,
    help="Path to the directory containing the files to be analyzed.",
)
args = parser.parse_args()
path = args.path


client = OpenAI(api_key=config["OPENAI_API_KEY"])
editor = CodeEditor(
    client=client,
    model="gpt-4.1",
)
edit_all_dirs(editor, path)

print("Done!")
