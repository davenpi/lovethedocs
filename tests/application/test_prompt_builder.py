import textwrap
import libcst as cst
from src.application.prompt_builder import ObjCollector
from src.application.prompt_builder import build_prompts


def _collect_ids(source: str):
    wrapper = cst.metadata.MetadataWrapper(cst.parse_module(source))
    collector = ObjCollector()
    wrapper.visit(collector)
    return collector.result  # List[(id, qualname)]


def test_simple_module_ids():
    code = "def foo(): pass\nclass Bar: pass"
    ids = _collect_ids(code)
    assert ids == [("ID001", "foo"), ("ID002", "Bar")]


def test_nested_function_and_class():
    code = """
    def outer():
        def inner():
            pass
        return inner

    class A:
        class Meta:
            pass
        def method(self):
            def helper(): pass
            return helper
    """
    code = textwrap.dedent(code)
    ids = dict(_collect_ids(code))  # {ID001: qualname, ...}
    # We care about the QUALNAMES, IDs just need to be unique
    assert set(ids.values()) == {
        "outer",
        "outer.inner",
        "A",
        "A.Meta",
        "A.method",
        "A.method.helper",
    }
    # IDs are sequential and restart at 001 for each new collector
    assert list(ids) == ["ID001", "ID002", "ID003", "ID004", "ID005", "ID006"]


def test_collector_resets_per_file():
    code1 = "def a(): pass"
    code2 = "def b(): pass"
    ids1 = dict(_collect_ids(code1))
    ids2 = dict(_collect_ids(code2))
    # Each file’s first object gets ID001
    assert list(ids1) == ["ID001"]
    assert list(ids2) == ["ID001"]


def test_build_prompts_single_module():
    modules = {"foo.py": "def foo(): pass\n"}

    prompts, id_maps = build_prompts(modules)

    # Correct keys returned
    assert set(prompts) == {"foo.py"}
    assert set(id_maps) == {"foo.py"}

    prompt_text = prompts["foo.py"]
    id_map = id_maps["foo.py"]  # e.g. {"ID001": "foo"}

    # ­── BEGIN/END guards
    assert prompt_text.startswith("### Objects in this file:")
    assert prompt_text.rstrip().endswith("END foo.py")

    # Header contains the ID/qualname line
    assert "### Objects in this file:" in prompt_text
    header_line = next(line for line in prompt_text.splitlines() if "ID001" in line)
    assert header_line.strip().endswith("foo")

    # id_map matches the header
    assert id_map == {"ID001": "foo"}


def test_build_prompts_nested_objects_two_files():
    modules = {
        "pkg/a.py": textwrap.dedent(
            """
            def outer():
                def inner(): pass
                return inner
            """
        ),
        "b.py": "class C:\n    def m(self): pass\n",
    }

    prompts, id_maps = build_prompts(modules)

    # pkg/a.py  →  IDs 001,002 ;  b.py → IDs start again at 001
    assert id_maps["pkg/a.py"] == {
        "ID001": "outer",
        "ID002": "outer.inner",
    }
    assert id_maps["b.py"] == {
        "ID001": "C",
        "ID002": "C.m",
    }

    # Quick sanity: header lines present in each prompt
    for path, prompt in prompts.items():
        for obj_id, qual in id_maps[path].items():
            assert f"{obj_id}" in prompt and qual in prompt
