"""
Turns raw source text into the prompt fed to the LLM.
For now we just forward the big BEGIN/END blob.
Later this module will assemble per-function snippets.
"""


def build_prompt(concatenated_modules: str) -> str:
    return concatenated_modules
