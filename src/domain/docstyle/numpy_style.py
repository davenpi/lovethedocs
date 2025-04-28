from src.domain.docstyle.base import DocStyle


class NumPyDocStyle(DocStyle):
    name = "numpy"
    section_order = (
        "Parameters",
        "Returns",
        "Raises",
        "Examples",
        "Notes",
        "References",
    )
