"""
Defines the EvalConfig class used to specify and serialize evaluation setups.
"""

from typing import Optional


class EvalConfig:
    """
    Represents a complete configuration for creating an OpenAI eval.

    This includes the data source structure, testing criteria, and metadata.

    Attributes
    ----------
    name : str
        The unique name of the eval.
    data_source_config : dict
        Configuration for the data items to be used (e.g., schema, data source type).
    testing_criteria : list[dict]
        List of evaluation criteria, each specifying a check to run.
    metadata : dict
        Any descriptive metadata about the eval (e.g. description, notes).
    """

    def __init__(
        self,
        name: str,
        data_source_config: dict,
        testing_criteria: list[dict],
        metadata: Optional[dict] = None,
    ):
        self.name = name
        self.data_source_config = data_source_config
        self.testing_criteria = testing_criteria
        self.metadata = metadata or {}

    def to_dict(self) -> dict:
        """
        Returns the full eval payload ready for submission to the OpenAI API.
        """
        return {
            "name": self.name,
            "data_source_config": self.data_source_config,
            "testing_criteria": self.testing_criteria,
            "metadata": self.metadata,
        }

    def save_json(self, filepath: str) -> None:
        """
        Saves the eval config as a JSON file.

        Parameters
        ----------
        filepath : str
            Path to the output file.
        """
        import json

        with open(filepath, "w") as f:
            json.dump(self.to_dict(), f, indent=2)
