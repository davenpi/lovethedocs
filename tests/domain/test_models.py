from src.domain.models import ModuleEdit, ObjectEdit


from dataclasses import asdict


def test_moduleedit_roundtrip():
    raw = {
        "path": "foo.py",
        "functions": [{"qualname": "foo", "docstring": "?", "signature": "foo()"}],
        "classes": [],
    }
    obj = ModuleEdit(
        path=raw["path"],
        functions=[ObjectEdit(**raw["functions"][0])],
        classes=[],
    )
    assert asdict(obj) == raw


def test_moduleedit_all_objects():
    raw = {
        "path": "foo.py",
        "functions": [{"qualname": "foo", "docstring": "?", "signature": "foo()"}],
        "classes": [
            {"qualname": "Bar", "docstring": "?", "signature": "Bar()"},
            {"qualname": "Baz", "docstring": "?", "signature": "Baz()"},
        ],
    }
    obj = ModuleEdit(
        path=raw["path"],
        functions=[ObjectEdit(**raw["functions"][0])],
        classes=[ObjectEdit(**raw["classes"][0]), ObjectEdit(**raw["classes"][1])],
    )
    assert len(obj.all_objects()) == 3
    assert obj.all_objects()[0].qualname == "foo"
    assert obj.all_objects()[1].qualname == "Bar"
