from src.domain.models import ModuleEdit, FunctionEdit, ClassEdit


from dataclasses import asdict


def _make_function(name, etype):
    return {
        "qualname": name,
        "docstring": f"{name} docs",
        "signature": f"{name}()",
        "edit_type": etype,
        "examples": None,
    }


def test_moduleedit_roundtrip():
    raw = {
        "path": "foo.py",
        "functions": [
            _make_function("foo", "docstring"),
        ],
        "classes": [],
    }
    obj = ModuleEdit(
        path=raw["path"],
        functions=[FunctionEdit(**raw["functions"][0])],
        classes=[],
    )
    assert asdict(obj) == raw


def test_moduleedit_all_objects():
    function = FunctionEdit(
        qualname="foo",
        docstring="?",
        signature="foo()",
        edit_type="docstring",
        examples=None,
    )
    raw = {
        "path": "foo.py",
        "functions": [
            _make_function("foo", "docstring"),
        ],
        "classes": [
            {"qualname": "Bar", "docstring": "?", "methods": [function]},
        ],
    }
    obj = ModuleEdit(
        path=raw["path"],
        functions=[FunctionEdit(**raw["functions"][0])],
        classes=[ClassEdit(**raw["classes"][0])],
    )
    edits = obj.edits_by_qualname()
    print(edits)
    assert len(edits) == 3
    assert edits["foo"].qualname == "foo"
    assert edits["Bar"].qualname == "Bar"
    assert edits["Bar.foo"].qualname == "foo"


def test_edits_by_qualname_nested():
    raw = {
        "path": "foo.py",
        "functions": [_make_function("top", "docstring")],
        "classes": [
            {
                "qualname": "Outer",
                "docstring": "cls docs",
                "methods": [_make_function("inner", "signature")],
            }
        ],
    }
    obj = ModuleEdit(
        path=raw["path"],
        functions=[FunctionEdit(**raw["functions"][0])],
        classes=[
            ClassEdit(
                qualname="Outer",
                docstring="cls docs new",
                methods=[FunctionEdit(**raw["classes"][0]["methods"][0])],
            )
        ],
    )
    m = obj.edits_by_qualname()
    assert set(m) == {"top", "Outer", "Outer.inner"}
    assert m["Outer"].docstring == "cls docs new"
