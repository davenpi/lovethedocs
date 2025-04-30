class DocStyle:
    """
    Immutable description of a documentation style.

    Only carries constants used while *building* the prompt.  No parsing, no I/O.
    """

    # lowercase key used by config & template repository
    name: str
    # canonical order for sections inside a docstring
    section_order: tuple[str, ...]

    # Registry for all documentation styles
    _registry = {}

    @classmethod
    def register(cls, style_name: str, style_class: type) -> None:
        """Register a documentation style class."""
        if style_name in cls._registry:
            raise ValueError(f"Style '{style_name}' is already registered.")
        cls._registry[style_name] = style_class

    @classmethod
    def from_string(cls, style_name: str) -> "DocStyle":
        """Factory method to create a DocStyle instance from a string."""
        if style_name not in cls._registry:
            raise ValueError(f"Unknown documentation style: {style_name}")
        return cls._registry[style_name]()
