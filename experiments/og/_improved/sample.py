"""
This is a module to print a number of random numbers.
"""

import random


def print_random_numbers(n: int) -> None:
    """
    Print n random numbers between 0 and 10.

    Parameters
    ----------
    n : int
        The number of random numbers to print.
    """
    for _ in range(n):
        r = random.randint(0, 10)
        print(f"Number is {r}")


class Randy:

    def __init__(self, n: int) -> None:
        """
        Initialize Randy with a random number.

        Parameters
        ----------
        n : int
            The number of random numbers to generate (not used).
        """
        self.n = n
        self.r = random.randint(0, 10)

    def printout(self) -> None:
        """
        Print Randy's random number.
        """
        print(f"Number is {self.r}")