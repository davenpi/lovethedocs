from contextlib import contextmanager

import pytest

from lovethedocs.application.pipeline import async_runner, sync_runner


@contextmanager
def _silent_progress():
    """No-op replacement for rich progress bars."""

    class _P:
        def add_task(self, *_, **__):
            return None

        def advance(self, *_):
            pass

    yield _P()


# ─────────────────────────────────────────
# fixtures
# ─────────────────────────────────────────
@pytest.fixture
def patch_progress(monkeypatch):
    # silence both runners
    monkeypatch.setattr(async_runner, "make_progress", _silent_progress)
    monkeypatch.setattr(sync_runner, "make_progress", _silent_progress)


@pytest.fixture
def patch_summary(monkeypatch):
    monkeypatch.setattr(async_runner, "summarize", lambda *_: None)
    monkeypatch.setattr(sync_runner, "summarize", lambda *_: None)
