"""
This is a module to print a number of random numbers.
"""

import random


def print_random_numbers(n: int) -> None:
    """
    Print n random numbers.
    """
    for _ in range(n):
        r = random.randint(0, 10)
        print(f"Number is {r}")


class Randy:

    def __init__(self, n):
        self.n = n
        self.r = random.randint(0, 10)

    def printout(self):
        """
        Print Randy's random number.
        """
        print(f"Number is {self.r}")
