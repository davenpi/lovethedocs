class DocStyle:
    """
    Immutable description of a documentation style.

    Only carries constants used while *building* the prompt.  No parsing, no I/O.
    """

    # lowercase key used by config & template repository
    name: str
    # hard-wrap rule for the summary + body lines
    max_line_len: int
    # canonical order for sections inside a docstring
    section_order: tuple[str, ...]
