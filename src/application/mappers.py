from src.domain.models import ClassEdit, FunctionEdit, ModuleEdit


def map_json_to_module_edit(json_data: dict) -> ModuleEdit:
    """
    Map a JSON dictionary to a ModuleEdit object.

    Parses the input JSON data and constructs a ModuleEdit instance by converting
    function and class edits from their dictionary representations.

    Parameters
    ----------
    json_data : dict
        A dictionary containing 'function_edits' and 'class_edits' keys, each with
        lists of edit specifications.

    Returns
    -------
    ModuleEdit
        An instance of ModuleEdit populated with the parsed function and class edits.
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
