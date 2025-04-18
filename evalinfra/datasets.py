"""
DatasetBuilder for generating .jsonl files used in evals.
"""

from pathlib import Path
from typing import Union
import json

from src.contracts import DEFAULT_START_PHRASE, DEFAULT_END_PHRASE
from src import utils


class DatasetBuilder:
    """
    Responsible for creating eval datasets from source code and expected outputs.

    Attributes
    ----------
    input_path : Union[str, Path]
        Path to the input Python file(s).
    expected_output_path : Union[str, Path]
        Path to a plain text file with the expected model output.
    """

    def __init__(
        self,
        input_path: Union[str, Path],
        expected_output_path: Union[str, Path],
        start_phrase: str = DEFAULT_START_PHRASE,
        end_phrase: str = DEFAULT_END_PHRASE,
    ):
        self.input_path = Path(input_path)
        self.expected_output_path = Path(expected_output_path)
        self.start_phrase = start_phrase
        self.end_phrase = end_phrase

    def build(self) -> dict:
        """
        Constructs the eval data dictionary for one example.

        Returns
        -------
        dict
            A dictionary in the expected evals format:
            {"item": {"input_content": ..., "expected_output": ...}}
        """
        input_content = utils.concatenate_modules(self.input_path)
        if not input_content:
            raise ValueError(f"No Python code found in {self.input_path}")

        with open(self.expected_output_path, "r") as f:
            expected_output = f.read().strip()

        return {
            "item": {"input_content": input_content, "expected_output": expected_output}
        }

    def save_jsonl(self, output_path: Union[str, Path]) -> None:
        """
        Builds and saves the dataset as a single-line JSONL file.

        Parameters
        ----------
        output_path : str or Path
            Path to write the `.jsonl` file to.
        """
        data = self.build()
        with open(output_path, "w") as f:
            f.write(json.dumps(data) + "\n")
