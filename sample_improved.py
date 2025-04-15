"""
This is a module to print a number of random numbers.
"""

import random


def print_random_numbers(n: int) -> None:
    """
    Print n random numbers.

    Parameters
    ----------
    n : int
        The number of random numbers to print.
    """
    for _ in range(n):
        r = random.randint(0, 10)
        print(f"Number is {r}")


class Randy:
    """
    Class to represent a random number generator.
    """

    def __init__(self, n: int) -> None:
        """
        Initialize the Randy object with a random number.

        Parameters
        ----------
        n : int
            The number of times to generate a random number (not used).
        """
        self.n = n
        self.r = random.randint(0, 10)

    def printout(self) -> None:
        """
        Print Randy's random number.
        """
        print(f"Number is {self.r}")