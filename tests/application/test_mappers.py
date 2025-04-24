from src.application.mappers import create_module_edit_from_json
from src.domain.models import FunctionEdit, ModuleEdit


def test_create_module_edit_from_json_roundtrip():

    src_json = {
        "function_edits": [
            {"qualname": "foo", "docstring": "Hello", "signature": None}
        ],
        "class_edits": [],
    }

    mod_edit = create_module_edit_from_json(src_json)
    assert isinstance(mod_edit, ModuleEdit)
    assert mod_edit.function_edits[0] == FunctionEdit(
        qualname="foo", docstring="Hello", signature=None
    )
