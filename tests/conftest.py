import pytest

from lovethedocs.application.pipeline import async_runner
from tests.helpers import silent_progress


# Patch out progress bar so tests stay silent
@pytest.fixture
def patch_progress(monkeypatch):
    monkeypatch.setattr(async_runner, "make_progress", silent_progress)


# Patch out summarize() for the same reason
@pytest.fixture
def patch_summary(monkeypatch):
    monkeypatch.setattr(async_runner, "summarize", lambda *_: None)
