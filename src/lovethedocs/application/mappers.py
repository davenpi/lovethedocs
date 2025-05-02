from lovethedocs.domain.models import ClassEdit, FunctionEdit, ModuleEdit


def map_json_to_module_edit(json_data: dict) -> ModuleEdit:
    """
    Convert a JSON dictionary to a ModuleEdit instance.

    Parses the input dictionary to extract function and class edit specifications, then
    constructs a ModuleEdit object containing the corresponding FunctionEdit and
    ClassEdit instances.

    Parameters
    ----------
    json_data : dict
        Dictionary with 'function_edits' and 'class_edits' keys, each containing lists
        of edit specifications.

    Returns
    -------
    ModuleEdit
        A ModuleEdit instance populated with the parsed function and class edits.
    """
    function_edits = [FunctionEdit(**f) for f in json_data["function_edits"]]
    class_edits = [
        ClassEdit(
            qualname=c["qualname"],
            docstring=c["docstring"],
            method_edits=[FunctionEdit(**m) for m in c["method_edits"]],
        )
        for c in json_data["class_edits"]
    ]
    return ModuleEdit(function_edits=function_edits, class_edits=class_edits)
