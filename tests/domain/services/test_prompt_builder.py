"""
Unit-tests for src.domain.services.prompt_builder.PromptBuilder
"""

from __future__ import annotations

import textwrap
from pathlib import Path
from types import SimpleNamespace

import pytest

from src.domain.models import SourceModule
from src.domain.services.prompt_builder import PromptBuilder


# --------------------------------------------------------------------------- #
#  Fixtures – tiny fakes keep dependencies minimal                            #
# --------------------------------------------------------------------------- #
class FakeTemplateRepo:
    """Bare-bones stub recording calls to .get()."""

    def __init__(self):
        self.called_with: list[str] = []

    def get(self, name: str) -> str:  # signature compatible
        self.called_with.append(name)
        return "<template stub>"


@pytest.fixture()
def builder():
    repo = FakeTemplateRepo()
    style = SimpleNamespace(name="numpy")  # anything with a .name attr works
    return PromptBuilder(repo), repo, style


def _make_module(name: str, body: str) -> SourceModule:
    code = textwrap.dedent(body)
    return SourceModule(path=Path(f"{name}.py"), code=code)


# --------------------------------------------------------------------------- #
# 1 ── Single-module prompt contains header + BEGIN/END                       #
# --------------------------------------------------------------------------- #
def test_build_single_module(builder):
    pb, repo, style = builder
    mod = _make_module(
        "foo",
        """
        def add(x, y):
            return x + y
        """,
    )

    prompts = pb.build([mod], style=style)

    # ---- repository .get called exactly once with style.name
    assert repo.called_with == [style.name]

    # ---- key and value structure
    assert list(prompts.keys()) == [mod.path]
    prompt = prompts[mod.path]

    # header lists objects
    assert f"### Objects in {mod.path}:" in prompt
    assert "  add" in prompt

    # body wrapped with BEGIN/END + file name
    assert prompt.splitlines()[-1] == f"END {mod.path}"


# --------------------------------------------------------------------------- #
# 2 ── Multiple modules → distinct prompts and single template lookup         #
# --------------------------------------------------------------------------- #
def test_build_multiple_modules(builder):
    pb, repo, style = builder
    mod1 = _make_module("a", "def f():\n    pass\n")
    mod2 = _make_module(
        "b",
        """
        class C:
            def g(self): ...
        """,
    )

    prompts = pb.build([mod1, mod2], style=style)

    # Exactly two prompts produced
    assert set(prompts.keys()) == {mod1.path, mod2.path}

    p1, p2 = prompts[mod1.path], prompts[mod2.path]
    assert "BEGIN a.py" in p1 and "END a.py" in p1
    assert "BEGIN b.py" in p2 and "END b.py" in p2

    # Objects correctly listed
    assert " f():" in p1
    assert " C:" in p2 and "  C.g" in p2

    # Template fetched only once despite two modules
    assert repo.called_with.count(style.name) == 1
