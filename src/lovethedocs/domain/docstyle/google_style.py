from lovethedocs.domain.docstyle.base import DocStyle


class GoogleDocStyle(DocStyle):
    name = "google"
    section_order = (
        "Args",
        "Returns",
        "Raises",
        "Yields",
        "Examples",
        "Notes",
        "References",
    )


# Register the GoogleDocStyle in the registry
DocStyle.register("google", GoogleDocStyle)
