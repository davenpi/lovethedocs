"""
The editor class defining the actual object which will be used to edit the code.
"""

from pathlib import Path

from openai import OpenAI
import utils


class CodeEditor:

    def __init__(
        self, client: OpenAI, model: str, start_phrase: str, end_phrase: str
    ) -> None:
        """
        Initialize the CodeEditor with OpenAI client and model parameters.

        Parameters
        ----------
        client : OpenAI
            The OpenAI client for making API calls.
        model : str
            The model to use for code editing. For example::

                "gpt-4o"

        start_phrase : str
            The phrase indicating the start of the code to be edited. For example::

                "BEGIN lovethedocs"

        end_phrase : str
            The phrase indicating the end of the code to be edited. For example::

                "END lovethedocs"
        """
        self.client = client
        self.model = model
        self.start_phrase = start_phrase
        self.end_phrase = end_phrase
        self.dev_prompt = self._create_prompt()

    def run_inference(self, content: str) -> str:
        """
        Run inference on the given content using the OpenAI client.

        Parameters
        ----------
        content : str
            The content to run inference on.

        Returns
        -------
        str
            The model response with improved docstrings.
        """
        response = self.client.responses.create(
            model=self.model,
            instructions=self.dev_prompt,
            input=[{"role": "user", "content": content}],
            temperature=0,
        )
        return response.output[0].content[0].text

    def process_directory(self, path: str | Path) -> None:
        code = utils.concatenate_modules(path)
        if not code:
            return
        response_code = self.run_inference(code)
        module_code_dict = utils.parse_response(
            response_code, self.start_phrase, self.end_phrase
        )
        utils.write_response(module_code_dict, path)

    def _create_prompt(self) -> str:
        """Create the developer prompt using the provided template."""
        dev_prompt = f"""Your job is to be an expert documentation assistant. You are
a master of docstrings and of understanding python code. You've spent a long time
developing your taste. You are now going to help a user improve the
documentation of their code. The docstring should follow the style of the
pandas/numpy/requests libraries. For example, the docstring for a function
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
clearly and follows the pandas/numpy/requests style. Do make sure to highlight
where there are unused variables, imports, or other obvious code smells. Do this by
adding a comment next to unused imports, for example.

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

    {self.start_phrase} <module1_name>.py
    ```python
    <updated module code>
    ```
    {self.end_phrase} <module1_name>.py

    {self.start_phrase} <module2_name>.py
    ```python
    <updated module code>
    ```
    {self.end_phrase} <module2_name>.py
    ...

Return a response for each module even if the module is very similar to the others it
has been concatenated with. This is imperative. Otherwise the user will be confused
and not benefit from your help.

To summarize - You'll be given a python module or a series of modules and your job is
to analyze the code and generate improved docstrings for functions and classes. Only
edit docstrings. Also, only edit the docstrings that need improvement. We want to keep
diffs small. Do not change the code at all and do not say anything else in the response
outside of the format stated. Your work speaks for itself. Remember that!"""
        return dev_prompt
