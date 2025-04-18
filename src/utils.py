from pathlib import Path
from typing import Iterable

IGNORED_DIRS = {"venv", ".git", "__pycache__", "_improved", ".pytest_cache", ".vscode"}


def strip_format(text: str) -> str:
    """
    Strip formatting from the model response.

    For each module the model will respond with the updated code in the following
    format:

        "```python
        def foo():
            pass
        ```"

    This function removes the surrounding markdown formatting and returns just the
    code.

    Parameters
    ----------
    text : str
        The text to strip formatting from.

    Returns
    -------
    str
        The text without formatting. For example, given:

            "```python
            def foo():
                pass
            ```"
        This function will return::

            def foo():
                pass
    """
    return text.replace("```python", "").replace("```", "").strip()


def load_modules(path: str | Path) -> list:
    """
    Load all python modules in a directory.

    Parameters
    ----------
    path : str | Path
        The path to the directory containing the modules.

    Returns
    -------
    modules : list
        A list of module names. For example::

            ["module1.py", "module2.py"]
    """
    path = Path(path)
    modules = []
    ignored_files = ["__init__.py", "__main__.py"]
    for file in path.iterdir():
        if file.suffix == ".py" and file.name not in ignored_files:
            modules.append(file.name)
    return modules


def concatenate_modules(path: str | Path) -> str:
    """
    Concatenate all python modules in `path` into a single string.

    The string is formatted as follows:

        BEGIN <module1_name>
        <module code>
        END <module1_name>.py

        BEGIN <module2_name>.py
        <module code>
        END <module2_name>
        ...

    This is done to have a standard format for passing the modules to the model.

    Parameters
    ----------
    path : str | Path
        The path to the directory containing the modules.

    Returns
    -------
    str
        The concatenated modules.
    """
    modules = load_modules(path)
    if not modules:
        return ""
    code = ""
    for module in modules:
        code += "\nBEGIN" + f" {module}\n"
        file_path = Path(path) / f"{module}"
        with file_path.open("r") as f:
            code += f.read().strip()  # remove leading/trailing whitespace
        code += "\nEND" + f" {module}\n"
    print(f"Concatenated {modules} into a single string.")
    return code


def parse_response(response: str, start_phrase: str, end_phrase: str) -> dict:
    """
    Parse the model response and extract updated module code.

    The response is expected to follow this format:

        {start_phrase} <module1_name>.py
        <updated module code>
        {end_phrase} <module1_name>.py

        {start_phrase} <module2_name>.py
        <updated module code>
        {end_phrase} <module2_name>.py
        ...

    This function extracts each module name and its corresponding code block,
    returning them in a dictionary.

    Parameters
    ----------
    response : str
        The full response string returned by the model.

    Returns
    -------
    module_code_dict : dict
        A dictionary mapping module names to updated code. For example::

            {
                "module1.py": "def foo():\n    pass\n",
                "module2.py": "def bar():\n    pass\n"
            }
    """
    module_code_dict = {}
    for line in response.splitlines():
        if line.startswith(start_phrase):
            # use length of start_phrase to get the module name
            start_idx = len(start_phrase.split())
            module = line.split()[start_idx]
            module_code_dict[module] = ""
        elif line.startswith(end_phrase):
            continue
        else:
            module_code_dict[module] += line + "\n"

    # strip formatting from the code
    for module in module_code_dict:
        module_code_dict[module] = strip_format(module_code_dict[module])
    return module_code_dict


def write_response(module_code_dict: dict, path: str | Path) -> None:
    """
    Write the response to a file.

    Parameters
    ----------
    module_code_dict : dict
        A dictionary with the module name as the key and the updated code as the value.
        For example::

            {
                "module1.py": 'print("Hello, world!")',
                "module2.py": 'print("Goodbye, world!")'
            }

    path : str | Path
        The path to the directory where the files will be saved. The new code will be
        save in a subdirectory called "_improved".

    Returns
    -------
    None
    """
    improved_path = Path(path) / "_improved"
    improved_path.mkdir(parents=True, exist_ok=True)
    for module, code in module_code_dict.items():
        if module:  # handle empty module names
            with (improved_path / module).open("w") as f:
                f.write(code)
            print(f"Updated '{module}' with new docstrings at {improved_path / module}")


def _iter_project_dirs(base: Path, ignored: set[str] = IGNORED_DIRS) -> Iterable[Path]:
    """
    Recursively yield directories in base that are not in the ignored set.
    """
    for path in base.iterdir():
        if path.is_dir():
            if path.name in ignored:
                continue
            yield path
            yield from _iter_project_dirs(path, ignored)
