"""
The editor class defining the actual object which will be used to edit the code.
"""

from pathlib import Path

from openai import OpenAI
from src import utils

from src.contracts import (
    DEFAULT_START_PHRASE,
    DEFAULT_END_PHRASE,
    get_dev_prompt,
)


class CodeEditor:

    def __init__(
        self,
        client: OpenAI,
        model: str,
        start_phrase: str = DEFAULT_START_PHRASE,
        end_phrase: str = DEFAULT_END_PHRASE,
    ) -> None:
        """
        Initialize the CodeEditor with OpenAI client and model parameters.

        Parameters
        ----------
        client : OpenAI
            The OpenAI client for making API calls.
        model : str
            The model to use for code editing. For example, "gpt-4.1".
        start_phrase : str
            Formatting token for highlighting relevant parts of model input/output.
        end_phrase : str
            Formatting token for highlighting relevant parts of model input/output.
        """
        self.client = client
        self.model = model
        self.start_phrase = start_phrase
        self.end_phrase = end_phrase
        self.dev_prompt = get_dev_prompt(
            start_phrase=self.start_phrase, end_phrase=self.end_phrase
        )

    def process_directory(self, path: str | Path) -> None:
        """
        Process all Python modules in the specified directory.

        Parameters
        ----------
        path : str | Path
            The path to the directory to process.

        Returns
        -------
        None
        """
        code = utils.concatenate_modules(path)
        if not code:
            print(f"No Python modules found in {path}.")
            return
        response_code = self._run_inference(code)
        module_code_dict = utils.parse_response(
            response_code, self.start_phrase, self.end_phrase
        )
        utils.write_response(module_code_dict, path)

    def _run_inference(self, content: str) -> str:
        """
        Run inference on the given content using the OpenAI client.

        Parameters
        ----------
        content : str
            The content to run inference on. Should be formatted as follows::

                BEGIN <module1_name>.py
                <module code>
                END <module1_name>.py

                BEGIN <module2_name>
                <module code>
                END <module2_name>
                ...

            This is done to have a standard format for passing the modules to the model.

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
