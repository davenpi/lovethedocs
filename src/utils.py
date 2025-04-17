from pathlib import Path
from typing import Iterable

from dotenv import dotenv_values
from openai import OpenAI

config = dotenv_values(".env")


API_KEY = config["OPENAI_API_KEY"]

START_PHRASE = "START lovethedocs"
END_PHRASE = "END lovethedocs"

IGNORED_DIRS = {"venv", ".git", "__pycache__", "_improved", ".pytest_cache", ".vscode"}

DEV_PROMPT = f"""Your job is to be a benevolent documentation assistant. You are
a master of docstrings and of understanding python code. You've spent a long time
developing your taste. You are now going to help a user improve the
documentation of their code. The docstring should follow the style of the
`pandas`/`numpy`/`requests` libraries. For example, the docstring for a function
`func` should be in the following format:

    def func(param1: int, param2: str) -> str:
        \"""
        Brief description of the function. (max 88 characters)

        Longer description.

        Parameters
        ----------
        param1 : int
            Description of param1.
        param2 : str
            Description of param2.

        Returns
        -------
        str
            Description of return value.
        \"""

Do not include the longer description in the docstring if it is not needed. For simple
code the one line description is sufficient. It's important to be concise. The
docstring should be clear and easy to read. Avoid repeating unnecessary information
that is obvious from the code. If a function or class has a quality docstring already,
do not change it. Quality means the docstring explains what the associated code does
clearly and follows the `pandas`/`numpy`/`requests` style. Do make sure to highlight
where there are unused variables, imports, or other obvious code smells.

You'll be passed a python module or series of modules. They will be formatted as
follows:

    BEGIN <module1_name>.py
    <module code>
    END <module1_name>.py

    BEGIN <module2_name>
    <module code>
    END <module2_name>
    ...

Format your response as follows:

    {START_PHRASE} <module1_name>.py
    ```python
    <updated module code>
    ```
    {END_PHRASE} <module1_name>.py

    {START_PHRASE} <module2_name>.py
    ```python
    <updated module code>
    ```
    {END_PHRASE} <module2_name>.py
    ...

Return a response for each module even if the module is very similar to the others it
has been concatenated with. This is imperative. Otherwise the user will be confused
and not benefit from your help.

To summarize - You'll be given a python module or a series of modules and your job is
to analyze the code and generate improved docstrings for functions and classes. Only
edit docstrings. Also, only edit the docstrings that need improvement. We want to keep
diffs small. Do not change the code at all and do not say anything else in the response
outside of the format stated. Your work speaks for itself. Remember that!"""


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
        The text without formatting. For example, given::

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
            code += f.read()
        code += "\nEND" + f" {module}\n"
    print(f"Concatenated {modules} into a single string.")
    return code


# TODO: Make less vulnerable to changes in the response format.
def parse_response(response: str) -> dict:
    """
    Parse the model response and extract updated module code.

    The response is expected to follow this format:

        {START_PHRASE} <module1_name>.py
        <updated module code>
        {END_PHRASE} <module1_name>.py

        {START_PHRASE} <module2_name>.py
        <updated module code>
        {END_PHRASE} <module2_name>.py
        ...

    This function extracts each module name and its corresponding code block,
    returning them in a dictionary.

    Parameters
    ----------
    response : str
        The full response string returned by the model.

    Returns
    -------
    dict
        A dictionary mapping module names to updated code. For example::

            {
                "module1": "def foo():\n    pass\n",
                "module2": "def bar():\n    pass\n"
            }
    """
    modules = {}
    for line in response.splitlines():
        if line.startswith(START_PHRASE):
            # TODO: get module name without hardcoding position
            module = line.split()[2]
            print(f"PARSING MODULE: {module}")

            modules[module] = ""
        elif line.startswith(END_PHRASE):
            continue
        else:
            modules[module] += line + "\n"

    print(f"MODULE KEYS: {modules.keys()}")
    return modules


def write_response(modules: dict, path: str | Path) -> None:
    """
    Write the response to a file.

    Parameters
    ----------
    modules : dict
        A dictionary with the module name as the key and the updated code as the value.
    path : str | Path
        The path to the directory where the files will be saved.

    Returns
    -------
    None
    """
    improved_path = Path(path) / "_improved"
    improved_path.mkdir(parents=True, exist_ok=True)
    for module, code in modules.items():
        if module:  # handle empty module names
            with (improved_path / module).open("w") as f:
                # Strip formatting from the code
                code = strip_format(code)
                # Write the code to the file
                f.write(code)
            print(f"Updated '{module}' with new docstrings at {improved_path / module}")


def iter_project_dirs(base: Path, ignored: set[str] = IGNORED_DIRS) -> Iterable[Path]:
    """
    Recursively yield directories in base that are not in the ignored set.
    """
    for path in base.iterdir():
        if path.is_dir():
            if path.name in ignored:
                continue
            yield path
            yield from iter_project_dirs(path, ignored)


def edit_all_dirs(client: OpenAI, path: str) -> None:
    """
    Edit all directories in the given path, excluding ignored ones.
    """
    base = Path(path)

    # Handle root directory first
    code = concatenate_modules(base)
    response_code = run_inference(client, code)
    module_code_dict = parse_response(response_code)
    write_response(module_code_dict, base)

    # Handle subdirectories
    for subdir in iter_project_dirs(base):
        code = concatenate_modules(subdir)
        if not code:
            continue
        response_code = run_inference(client, code)
        print(f"RESPONSE CODE: {response_code}")
        module_code_dict = parse_response(response_code)
        write_response(module_code_dict, subdir)


def run_inference(client: OpenAI, content: str) -> str:
    """
    Run inference on the given content.

    Parameters
    ----------
    client : OpenAI
        The OpenAI client.
    content : str
        The content to run inference on.

    Returns
    -------
    str
        The response from OpenAI.
    """
    response = client.responses.create(
        model="gpt-4.1-2025-04-14",
        # model="gpt-4o-mini",
        instructions=DEV_PROMPT,
        input=[{"role": "user", "content": content}],
        temperature=0,
    )
    print(f"RESPONSE ON NEXT LINE:\n{response.output[0].content[0].text}")
    return response.output[0].content[0].text
