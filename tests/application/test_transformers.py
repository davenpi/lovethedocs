"""
Tests for sr.c.application.transformers.DocSigPatcher.

The goals are to
1. Verify docstring *insertion* and *replacement* at several nesting depths.
2. Check that multi-line docstrings are indented correctly (`indent_str` logic).
3. Ensure function-signature replacement works.
4. Confirm that untouched objects remain unchanged (safety net).
"""

from __future__ import annotations

import textwrap

import libcst as cst
import pytest

from src.application.transformers import DocSigPatcher
from src.domain.models import FunctionEdit, ClassEdit, ModuleEdit


# -------helpers-----------------------------------------------------
def apply(source: str, edits: dict[str, FunctionEdit | ClassEdit]) -> str:
    """Parse, transform with DocSigPatcher, and return code string."""
    tree = cst.parse_module(textwrap.dedent(source))
    new_tree = tree.visit(DocSigPatcher(edits))
    return new_tree.code


# -------1  top-level function — insert 1-liner docstring------------
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
    out = apply(src, {"foo": FunctionEdit(qualname="foo", docstring="Do something")})
    assert out.strip() == textwrap.dedent(expected).strip()


# -------2  class docstring — replace existing doc-------------------
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
    out = apply(src, {"A": ClassEdit(qualname="A", docstring="New docs")})
    assert out.strip() == textwrap.dedent(expected).strip()


# -------3  signature replacement------------------------------------
def test_replace_function_signature():
    src = """
        def add(x, y):
            return x + y
    """
    expected = """
        def add(a: int, b: int) -> int:
            return x + y
    """
    edit = FunctionEdit(qualname="add", signature="def add(a: int, b: int) -> int:")
    out = apply(src, {"add": edit})
    assert out.strip() == textwrap.dedent(expected).strip()


# -------4  nested method — multi-line docstring w/ correct indent---
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
    module_edit = ModuleEdit(
        class_edits=[class_edit],
    )
    print(module_edit)
    edits = module_edit.map_qnames_to_edits()
    out = apply(src, edits)
    assert out.strip() == textwrap.dedent(expected).strip()


# -------5  untouched code stays untouched---------------------------
def test_no_edits_no_changes():
    src = """
        def untouched():
            return 42
    """
    out = apply(src, {})  # no edits at all
    assert out.strip() == textwrap.dedent(src).strip()

    out2 = apply(
        src, {"other": FunctionEdit(qualname="touch", docstring="x")}
    )  # irrelevant edit
    assert out2.strip() == textwrap.dedent(src).strip()


# sanity: make sure the tests will be skipped gracefully if libcst is absent
pytest.importorskip("libcst")
