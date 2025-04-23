import os
import random


class Greeter:
    """
    A class to greet and bid farewell to a person.

    Parameters
    ----------
    name : str
        The name of the person to greet.
    """

    def __init__(self, name):
        self.name = name

    def greet(self):
        """Print a greeting message."""
        print(f"Hello, {self.name}!")

    def farewell(self):
        """Print a farewell message."""
        print(f"Goodbye, {self.name}!")

    @classmethod
    def from_env(cls):
        """
        Create a Greeter instance using the name from the environment variable.

        Returns
        -------
        Greeter
            A Greeter instance with the name from the environment variable or "World".
        """
        name = os.getenv("NAME", "World")
        return cls(name)


def create_greeter(name):
    """
    Create a Greeter instance with the given name.

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


def rand_greet():
    """Select a random name and greet that person."""
    names = ["Alice", "Bob", "Charlie", "Diana"]
    name = random.choice(names)
    greeter = Greeter(name)
    greeter.greet()