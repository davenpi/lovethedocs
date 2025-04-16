import os
import random


class Greeter:

    def __init__(self, name):
        self.name = name

    def greet(self):
        print(f"Hello, {self.name}!")

    def farewell(self):
        print(f"Goodbye, {self.name}!")

    @classmethod
    def from_env(cls):
        name = os.getenv("NAME", "World")
        return cls(name)


def create_greeter(name):
    return Greeter(name)


def rand_greet():
    names = ["Alice", "Bob", "Charlie", "Diana"]
    name = random.choice(names)
    greeter = Greeter(name)
    greeter.greet()
