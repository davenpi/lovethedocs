import asyncio

import pytest

from lovethedocs.application.pipeline import safety
from lovethedocs.domain import docstyle
from lovethedocs.domain.models import SourceModule

# --- local test doubles ---------------------------------------------------
STYLE = docstyle.DocStyle.from_string("numpy")


class DummyUseCase:
    """
    Minimal stand-in for DocumentationUpdateUseCase.

    If `should_fail` is True the runner raises, letting the safety wrapper
    exercise the failure branch.
    """

    def __init__(self, *, should_fail: bool = False):
        self.should_fail = should_fail
        self.calls = []

    # sync path
    def run(self, modules, *, style):
        self.calls.extend(modules)
        if self.should_fail:
            raise ValueError("boom")
        return [(m, m.code + "\n# updated") for m in modules]

    # async path
    async def run_async(self, modules, *, style, concurrency):
        self.calls.extend(modules)
        for m in modules:
            if self.should_fail:
                raise RuntimeError("async-boom")
            yield m, m.code + "\n# updated"


MOD = SourceModule("a.py", "print('hi')")


def test_safe_update_ok():
    uc = DummyUseCase()
    mod, new, exc = safety.safe_update(uc, MOD, style=STYLE)
    assert exc is None
    assert new.endswith("# updated")


def test_safe_update_failure():
    uc = DummyUseCase(should_fail=True)
    mod, new, exc = safety.safe_update(uc, MOD, style=STYLE)
    assert new is None
    assert isinstance(exc, ValueError)


@pytest.mark.asyncio
async def test_safe_update_async_semaphore():
    uc = DummyUseCase()
    sem = asyncio.Semaphore(1)
    mod, new, exc = await safety.safe_update_async(uc, MOD, style=STYLE, sem=sem)
    assert sem._value == 1  # was released
    assert new.endswith("# updated")
