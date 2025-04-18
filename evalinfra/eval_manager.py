"""
Manage the evals and their configurations.
"""

from evalinfra.eval_config import EvalConfig


class EvalManager:
    """
    Class to manage evals and their configurations.
    """

    def __init__(self, config: EvalConfig):
        self.config = config

    def create_eval(self, config: EvalConfig) -> str:
        """
        Create an eval using the provided configuration.

        Parameters
        ----------
        config : EvalConfig
            The configuration for the eval.

        Returns
        -------
        None
        """
        # Implementation to create the eval using the provided configuration.
        pass

    def run_eval(self) -> None:
        """
        Run the eval using the provided configuration.

        Returns
        -------
        None
        """
        # Implementation to run the eval using the provided configuration.
        pass
