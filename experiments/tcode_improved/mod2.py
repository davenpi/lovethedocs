import mod1 as m1


def greet() -> None:
    """
    Print a greeting message from mod2.
    """
    print("Hello from mod2!")


if __name__ == "__main__":
    greet()
    m1.rand_greet()
    greeter = m1.Greeter.from_env()
    greeter.greet()
    greeter.farewell()
