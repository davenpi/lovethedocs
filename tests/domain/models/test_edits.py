from dataclasses import asdict

from src.domain.models import ClassEdit, FunctionEdit, ModuleEdit


def _make_function_edit(qualname):
    return {
        "qualname": qualname,
        "docstring": f"{qualname} docs",
        "signature": f"{qualname}()",
    }


def test_moduleedit_roundtrip():
    raw = {
        "function_edits": [
            _make_function_edit("foo"),
        ],
        "class_edits": [],
    }
    obj = ModuleEdit(
        function_edits=[FunctionEdit(**raw["function_edits"][0])],
        class_edits=raw["class_edits"],
    )

    assert asdict(obj) == raw


def test_moduleedit_all_objects():
    raw = {
        "function_edits": [
            _make_function_edit("foo"),
        ],
        "class_edits": [
            {
                "qualname": "Bar",
                "docstring": "?",
                "method_edits": [FunctionEdit(**_make_function_edit("Bar.baz"))],
            },
        ],
    }
    obj = ModuleEdit(
        function_edits=[FunctionEdit(**raw["function_edits"][0])],
        class_edits=[ClassEdit(**raw["class_edits"][0])],
    )
    qname_to_edit = obj.map_qnames_to_edits()

    assert len(qname_to_edit) == 3
    assert qname_to_edit["foo"].qualname == "foo"
    assert qname_to_edit["Bar.baz"].qualname == "Bar.baz"
    assert qname_to_edit["Bar"].docstring == "?"
