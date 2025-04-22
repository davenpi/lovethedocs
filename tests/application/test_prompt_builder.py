import textwrap
import libcst as cst
from src.application.prompt_builder import ObjCollector
from src.application.prompt_builder import build_prompts


def _collect_qualnames(source: str):
    wrapper = cst.metadata.MetadataWrapper(cst.parse_module(source))
    collector = ObjCollector()
    wrapper.visit(collector)
    return collector.qualnames


def test_simple_module_ids():
    code = "def foo(): pass\nclass Bar: pass"
    qualnames = _collect_qualnames(code)
    assert qualnames == ["foo", "Bar"]


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
    qualnames = _collect_qualnames(code)
    assert qualnames == [
        "outer",
        "outer.inner",
        "A",
        "A.Meta",
        "A.method",
        "A.method.helper",
    ]


def test_collector_resets_per_file():
    code1 = "def a(): pass"
    code2 = "def b(): pass"
    qualnames1 = _collect_qualnames(code1)
    qualnames2 = _collect_qualnames(code2)
    assert qualnames1 == ["a"]
    assert qualnames2 == ["b"]


def test_build_prompts_single_module():
    modules = {"foo.py": "def foo(): pass\n"}

    prompts = build_prompts(modules)

    # Correct keys returned
    assert set(prompts) == {"foo.py"}

    prompt_text = prompts["foo.py"]

    # ­── BEGIN/END guards
    assert prompt_text.startswith("### Objects in this file:")
    assert prompt_text.rstrip().endswith("END foo.py")

    # Header contains the ID/qualname line
    assert "### Objects in this file:" in prompt_text


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

    prompts = build_prompts(modules)

    # check prompt has the correct keys
    assert set(prompts) == {"pkg/a.py", "b.py"}

    # assert nesting is preserved
    assert "outer.inner" in prompts["pkg/a.py"]
    assert "C.m" in prompts["b.py"]
    assert "C" in prompts["b.py"]
    assert "outer" in prompts["pkg/a.py"]
    assert "inner" in prompts["pkg/a.py"]
