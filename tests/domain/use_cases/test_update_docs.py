"""
Interaction-level tests for `DocumentationUpdateUseCase`.

The class itself owns **no domain logic**; it merely orchestrates collaborators.
These tests therefore focus on call-ordering and propagation of data/​errors.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List

import pytest

from src.domain.models import ModuleEdit, SourceModule
from src.domain.use_cases.update_docs import DocumentationUpdateUseCase


# --------------------------------------------------------------------------- #
#  Test doubles                                                               #
# --------------------------------------------------------------------------- #
class FakeBuilder:
    def __init__(self) -> None:
        self.called_with: Dict[str, object] = {}

    def build(self, mods, *, style):
        # record and return {path: prompt}
        self.called_with = {"mods": list(mods), "style": style}
        return {m.path: f"prompt<{m.path}>" for m in self.called_with["mods"]}


class FakeGenerator:
    def __init__(self) -> None:
        self.prompts: List[str] = []

    def generate(self, prompt):
        self.prompts.append(prompt)
        return ModuleEdit()  # sentinel (content unused by patcher)


class FakePatcher:
    def __init__(self, postfix: str) -> None:
        self.calls: List[tuple] = []
        self._postfix = postfix

    def apply(self, edit, code):
        self.calls.append((edit, code))
        return code + self._postfix  # observable transformation


# --------------------------------------------------------------------------- #
#  Helpers                                                                    #
# --------------------------------------------------------------------------- #
def _make_module(name: str, code: str = "x = 1\n") -> SourceModule:
    return SourceModule(path=Path(f"{name}.py"), code=code)


STYLE = object()  # anything truthy – only identity matters for assertions


# --------------------------------------------------------------------------- #
#  1 ── happy-path orchestration                                              #
# --------------------------------------------------------------------------- #
def test_update_docs_happy_path():
    mods = [_make_module("a"), _make_module("b")]
    builder = FakeBuilder()
    gen = FakeGenerator()
    patcher = FakePatcher(postfix="#patched")

    uc = DocumentationUpdateUseCase(builder=builder, generator=gen, patcher=patcher)

    out = list(uc.run(mods, style=STYLE))

    # ----- builder called once with full module list and style
    assert builder.called_with == {"mods": mods, "style": STYLE}

    # ----- generator called once per module with correct prompt
    expected_prompts = [f"prompt<{m.path}>" for m in mods]
    assert gen.prompts == expected_prompts

    # ----- patcher called once per module and output collected
    assert len(patcher.calls) == len(mods)
    for (mod, new_code), original in zip(out, mods, strict=True):
        assert new_code.endswith("#patched")
        assert mod is original  # same object, not a copy


# --------------------------------------------------------------------------- #
#  2 ── generator error propagates                                            #
# --------------------------------------------------------------------------- #
def test_update_docs_propagates_generator_error():
    class BoomGen(FakeGenerator):
        def generate(self, prompt):
            raise RuntimeError("LLM failed")

    uc = DocumentationUpdateUseCase(
        builder=FakeBuilder(),
        generator=BoomGen(),
        patcher=FakePatcher(postfix=""),
    )

    with pytest.raises(RuntimeError):
        list(uc.run([_make_module("solo")], style=STYLE))
