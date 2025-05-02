"""
Unit-tests for lovethedocs.domain.models.source_module.SourceModule
"""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from lovethedocs.domain.models.source_module import SourceModule

pytest.importorskip("libcst")  # ensure LibCST is available


# --------------------------------------------------------------------------- #
# 1 ── .from_path stores *relative* paths and preserves code text             #
# --------------------------------------------------------------------------- #
def test_from_path_relative(tmp_path):
    root = tmp_path / "proj"
    root.mkdir()
    file_path = root / "pkg" / "mod.py"
    file_path.parent.mkdir()
    code_text = "def foo():\n    pass\n"
    file_path.write_text(code_text, encoding="utf-8")

    mod = SourceModule.from_path(file_path, root=root)

    assert mod.path == Path("pkg/mod.py")  # relative
    assert mod.code == code_text  # unchanged source


# --------------------------------------------------------------------------- #
# 2 ── .objects lists qualnames in lexical order                              #
# --------------------------------------------------------------------------- #
def test_objects_collects_names():
    src = textwrap.dedent(
        """
        def util():
            pass

        class Foo:
            def bar(self):
                pass

        def outer():
            def inner():
                pass
            return inner()
        """
    )
    mod = SourceModule(path=Path("dummy.py"), code=src)

    expected = ["util", "Foo", "Foo.bar", "outer", "outer.inner"]
    assert mod.objects == expected


# --------------------------------------------------------------------------- #
# 3 ── .objects is cached (same list object returned)                         #
# --------------------------------------------------------------------------- #
def test_objects_cached_property():
    src = "def f():\n    pass\n"
    mod = SourceModule(path=Path("x.py"), code=src)

    first = mod.objects
    second = mod.objects

    # identity implies @cached_property memoization worked
    assert first is second
