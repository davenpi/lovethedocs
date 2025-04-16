import os

from dotenv import dotenv_values

config = dotenv_values(".env")
API_KEY = config["OPENAI_API_KEY"]

DEV_PROMPT = f"""Your job is to be a benevolent documentation assistant. You are
a master of docstrings and of understanding python code. You've spent a long time
developing your docstring style. You are now going to help a user improve the
documentation of their code. The docstring should follow the style of the `pandas` and
`requests` libraries. For example, the docstring for a function `func` should be in the
following format:

    def func(param1: int, param2: str) -> None:
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
        None
            Description of return value.
        \"""

Do not include the longer description in the docstring if it is not needed. For simple
code the one line description is sufficient. It's important to be concise. The
docstring should be clear and easy to read. Avoid repeating unnecessary information
that is obvious from the code. If a function or class has a quality docstring already,
do not change it.

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
    LOVE THE DOCS <module1_name>.py
    <updated module code>
    END <module1_name>.py

    LOVE THE DOCS <module2_name>.py
    <updated module code>
    END <module2_name>.py
    ...

To summarize - You'll be given a python module or a series of modules and your job is
to analyze the code and generate improved docstrings for functions and classes. Only
edit docstrings. Also, only edit the docstrings that genuinely need improvement. We want
to keep diffs small. Do not change the code at all and do not say anything else in
the response outside of the format stated. Your work speaks for itself. Remember
that!"""


def strip_format(text: str) -> str:
    """
    Strip formatting from the text.

    GPT may respond with:
    ```python
        code
    ```
    We need to remove that formatting and write it directly as a valid python code.

    Parameters
    ----------
    text : str
        The text to strip formatting from.

    Returns
    -------
    str
        The text without formatting.
    """
    return text.replace("```python", "").replace("```", "").strip()


def load_modules(path: str) -> list:
    """
    Load all modules in a directory.

    Parameters
    ----------
    path : str
        The path to the directory containing the modules.

    Returns
    -------
    list
        A list of module names.
    """
    modules = []
    for file in os.listdir(path):
        if file.endswith(".py") and file != "__init__.py":
            modules.append(file[:-3])
    return modules


def concatenate_modules(path: list) -> str:
    """
    Concatenate all modules into a single string.

    Parameters
    ----------
    modules : list
        A list of module names.

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
        with open(os.path.join(path, f"{module}.py"), "r") as f:
            code += f.read()
        code += "\nEND" + f" {module}.py\n"
    return code


def parse_response(response: str) -> dict:
    """
    Parse the response from OpenAI.

    The response will be in the format:
    LOVE THE DOCS <module1_name>.py
    <updated module code>
    END <module1_name>.py

    LOVE THE DOCS <module2_name>.py
    <updated module code>
    END <module2_name>.py
    ...

    This function will extract the module names and updated code from the response.
    The returned dictionary will have the module name as the key and the updated code
    as the value. For example:
    {
        "module1": "updated code",
        "module2": "updated code",
        ...
    }

    Parameters
    ----------
    response : str
        The response from OpenAI.

    Returns
    -------
    dict
        A dictionary with the module name as the key and the updated code as the value.
    """
    modules = {}
    for line in response.splitlines():
        if line.startswith("LOVE THE DOCS"):
            module = line.split()[3]
            module = os.path.splitext(module)[0]
            modules[module] = ""
        elif line.startswith("END"):
            continue
        else:
            modules[module] += line + "\n"
    return modules


def write_response(modules: dict, path: str) -> None:
    """
    Write the response to a file.

    Parameters
    ----------
    modules : dict
        A dictionary with the module name as the key and the updated code as the value.
    path : str
        The path to the directory where the files will be saved.

    Returns
    -------
    None
    """
    improved_path = path + "_improved"
    os.makedirs(improved_path, exist_ok=True)
    for module, code in modules.items():
        with open(os.path.join(improved_path, module + ".py"), "w") as f:
            # Strip formatting from the code
            code = strip_format(code)
            # Write the code to the file
            f.write(code)
        print(f"Updated {module} with new docstrings.")
