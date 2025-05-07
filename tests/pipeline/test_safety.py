import pytest
import asyncio
from lovethedocs.application.pipeline import safety
from lovethedocs.domain.models import SourceModule

from tests.helpers import DummyUseCase
from tests.helpers import STYLE

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
    mod, new, exc = await safety.safe_update_async(
        uc, MOD, style=STYLE, sem=sem
    )
    assert sem._value == 1          # was released
    assert new.endswith("# updated")