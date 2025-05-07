"""
Tests for lovethedocs.domain.services.patcher.ModulePatcher.

Goals
-----
1. Verify docstring *insertion* and *replacement* at several nesting depths.
2. Check that multi-line docstrings are indented correctly.
3. Ensure function-signature replacement works.
4. Confirm that untouched objects remain unchanged (safety net).
5. Test that docstrings are inserted into Protocol stubs at various levels.
"""

from __future__ import annotations

import textwrap

from lovethedocs.domain.models import ClassEdit, FunctionEdit, ModuleEdit
from lovethedocs.domain.services.patcher import ModulePatcher


# --------------------------------------------------------------------- helpers
def apply(source: str, mod_edit: ModuleEdit) -> str:
    """Apply `ModulePatcher` to `source` and return the transformed code."""
    patched = ModulePatcher().apply(mod_edit, textwrap.dedent(source))
    return patched


def test_insert_docstring_top_level():
    src = """
        def foo(x):
            pass
    """
    expected = """
        def foo(x):
            \"\"\"Do something\"\"\"
            pass
    """
    edit = ModuleEdit(
        function_edits=[FunctionEdit(qualname="foo", docstring="Do something")]
    )
    out = apply(src, edit)
    assert out.strip() == textwrap.dedent(expected).strip()


def test_replace_class_docstring():
    src = '''
        class A:
            """Old"""
            def func(self):
                pass
    '''
    expected = '''
        class A:
            """New docs"""
            def func(self):
                pass
    '''
    edit = ModuleEdit(class_edits=[ClassEdit(qualname="A", docstring="New docs")])
    out = apply(src, edit)
    assert out.strip() == textwrap.dedent(expected).strip()


def test_replace_function_signature():
    src = """
        def add(x, y):
            return x + y
    """
    expected = """
        def add(a: int, b: int) -> int:
            return x + y
    """
    edit = ModuleEdit(
        function_edits=[
            FunctionEdit(
                qualname="add",
                signature="def add(a: int, b: int) -> int:",
            )
        ]
    )
    out = apply(src, edit)
    assert out.strip() == textwrap.dedent(expected).strip()


def test_multiline_docstring_indent_nested():
    multiline = "Line1\nLine2"
    src = """
        class Foo:
            def bar(self):
                pass
    """
    expected = '''
        class Foo:
            def bar(self):
                """
                Line1
                Line2
                """
                pass
    '''
    method_edit = FunctionEdit(
        qualname="Foo.bar",
        docstring=multiline,
    )
    class_edit = ClassEdit(
        qualname="Foo",
        method_edits=[method_edit],
    )
    module_edit = ModuleEdit(class_edits=[class_edit])
    out = apply(src, module_edit)
    print(out)
    assert out.strip() == textwrap.dedent(expected).strip()


def test_no_edits_no_changes():
    src = """
        def untouched():
            return 42
    """
    # 5-a: no edits at all
    out = apply(src, ModuleEdit())
    assert out.strip() == textwrap.dedent(src).strip()

    # 5-b: irrelevant edit
    out2 = apply(
        src,
        ModuleEdit(function_edits=[FunctionEdit(qualname="touch", docstring="x")]),
    )
    assert out2.strip() == textwrap.dedent(src).strip()


def test_protocol_stub_docstring_insertion():
    """
    Reproduces the crash on Protocol stubs where LibCST raises
    AttributeError('SimpleStatementLine' object has no attribute 'semicolon').

    Expectation: `_patch_doc` should inject a docstring into a stub method
    and return compilable code.
    """
    src = """
        from typing import Protocol

        class FileSystemPort(Protocol):
            def load_modules(self) -> dict[str, str]: ...
    """
    expected = '''
        from typing import Protocol

        class FileSystemPort(Protocol):
            def load_modules(self) -> dict[str, str]:
                """Load modules from storage."""
                ...
    '''
    edit = ModuleEdit(
        class_edits=[
            ClassEdit(
                qualname="FileSystemPort",
                method_edits=[
                    FunctionEdit(
                        qualname="FileSystemPort.load_modules",
                        docstring="Load modules from storage.",
                    )
                ],
            )
        ]
    )
    out = apply(src, edit)
    assert out.strip() == textwrap.dedent(expected).strip()


def test_stub_function_docstring_insertion():
    """
    Ensure top-level stub functions (one-liner ellipsis) receive a docstring
    and proper indentation.

    Before:
        def ping() -> str: ...

    After:
        def ping() -> str:
            \"\"\"Ping the service\"\"\"
            ...
    """
    src = """
        def ping() -> str: ...
    """
    expected = '''
        def ping() -> str:
            """Ping the service"""
            ...
    '''
    edit = ModuleEdit(
        function_edits=[FunctionEdit(qualname="ping", docstring="Ping the service")]
    )
    out = apply(src, edit)
    assert out.strip() == textwrap.dedent(expected).strip()
