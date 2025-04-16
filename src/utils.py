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
functions the one line description is sufficient. It's important to be concise. The
docstring should be clear and easy to read. Avoid repeating unnecessary information.
that is obvious from the code.

If a function or class has a quality docstring already, do not change it.

To summarize - You'll be given a python module and your job is to analyze the
code and generate improved docstrings for functions and classes. Only add
docstrings. Also, only edit the docstrings that genuinely need improvement. We want to
keep diffs as small. Do not change the code at all and do not say anything else in your
response. Your work speaks for itself. Remember that!"""


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
