"""
Creates a dataset for evaluation of the model.
"""

from src import utils
from src.contracts import (
    DEFAULT_START_PHRASE,
    DEFAULT_END_PHRASE,
)


class DatasetBuilder:
    """
    A class to build a dataset for evaluation of the model.
    """

    def __init__(self, path: str):
        """
        Initializes the DatasetBuilder with a path to the directory containing the
        modules.

        Parameters
        ----------
        path : str
            The path to the directory containing the modules.
        """
        self.path = path
