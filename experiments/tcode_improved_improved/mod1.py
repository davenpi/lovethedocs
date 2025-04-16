import os
import random


class Greeter:
    def __init__(self, name: str) -> None:
        """
        Initialize the Greeter with a name.

        Parameters
        ----------
        name : str
            The name of the person to greet.
        """
        self.name = name

    def greet(self) -> None:
        """
        Print a greeting message.
        """
        print(f"Hello, {self.name}!")

    def farewell(self) -> None:
        """
        Print a farewell message.
        """
        print(f"Goodbye, {self.name}!")

    @classmethod
    def from_env(cls) -> "Greeter":
        """
        Create a Greeter instance using the name from the environment variable.

        Returns
        -------
        Greeter
            A Greeter instance with the name from the environment variable or "World".
        """
        name = os.getenv("NAME", "World")
        return cls(name)


def create_greeter(name: str) -> Greeter:
    """
    Create a Greeter instance.

    Parameters
    ----------
    name : str
        The name of the person to greet.

    Returns
    -------
    Greeter
        A Greeter instance.
    """
    return Greeter(name)


def rand_greet() -> None:
    """
    Randomly greet one of the predefined names.
    """
    names = ["Alice", "Bob", "Charlie", "Diana"]
    name = random.choice(names)
    greeter = Greeter(name)
    greeter.greet()
