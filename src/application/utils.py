"""
Small helpers that aren't worth their own module yet.
"""

from typing import Callable, Optional


def apply_formatter(code: str, fmt: Optional[Callable[[str], str]] = None) -> str:
    """
    Return ``fmt(code)`` if a formatter was supplied, else the code unchanged.

    Parameters
    ----------
    code : str
        The source to format.
    fmt : Callable[[str], str] | None
        A function that returns formatted code (e.g. Black) or ``None`` to skip.

    Returns
    -------
    str
        Formatted or original source.
    """
    return fmt(code) if fmt else code
