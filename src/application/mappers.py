from src.domain.models import ClassEdit, FunctionEdit, ModuleEdit


def map_json_to_module_edit(json_data):
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
