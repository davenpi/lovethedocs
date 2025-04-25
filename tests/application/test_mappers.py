from src.application.mappers import map_json_to_module_edit
from src.domain.models import FunctionEdit, ModuleEdit


def test_create_module_edit_from_json_roundtrip():

    src_json = {
        "function_edits": [
            {"qualname": "foo", "docstring": "Hello", "signature": None}
        ],
        "class_edits": [],
    }

    mod_edit = map_json_to_module_edit(src_json)
    assert isinstance(mod_edit, ModuleEdit)
    assert mod_edit.function_edits[0] == FunctionEdit(
        qualname="foo", docstring="Hello", signature=None
    )
