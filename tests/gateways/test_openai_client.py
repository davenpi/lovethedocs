import json
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from lovethedocs.gateways import openai_client as oc

# --------------------------------------------------------------------------- #


# minimal stand-in for DocStyle
class _DummyStyle:
    name = "dummy"


# utility: clear both caches between tests
def _clear_caches():
    oc._get_sdk_client.cache_clear()
    oc._get_async_sdk_client.cache_clear()


# --------------------------------------------------------------------------- #
# 1. Sync adapter still parses JSON and forwards kwargs                       #
# --------------------------------------------------------------------------- #
def test_sync_request_returns_parsed_json(monkeypatch):
    _clear_caches()
    captured = {}

    class FakeResponses:
        def create(self, **kwargs):
            captured.update(kwargs)
            return SimpleNamespace(output_text=json.dumps({"ok": True}))

    fake_client = SimpleNamespace(responses=FakeResponses())
    monkeypatch.setattr(oc, "_get_sdk_client", lambda: fake_client)
    monkeypatch.setattr(oc, "_PROMPTS", SimpleNamespace(get=lambda _n: "TEST_PROMPT"))

    adapter = oc.OpenAIClientAdapter(style=_DummyStyle(), model="gpt-test")
    result = adapter.request("PROMPT")

    assert result == {"ok": True}
    assert captured["model"] == "gpt-test"
    assert captured["instructions"] == "TEST_PROMPT"


# --------------------------------------------------------------------------- #
# 2. Async adapter works + returns parsed JSON                                #
# --------------------------------------------------------------------------- #
@pytest.mark.asyncio
async def test_async_request_returns_parsed_json(monkeypatch):
    _clear_caches()

    async def _fake_create(**kwargs):
        return SimpleNamespace(output_text=json.dumps({"async_ok": True}))

    fake_client = SimpleNamespace(
        responses=SimpleNamespace(create=AsyncMock(side_effect=_fake_create))
    )
    monkeypatch.setattr(oc, "_get_async_sdk_client", lambda: fake_client)
    monkeypatch.setattr(oc, "_PROMPTS", SimpleNamespace(get=lambda _n: "TEST_PROMPT"))

    adapter = oc.AsyncOpenAIClientAdapter(style=_DummyStyle(), model="gpt-test")
    result = await adapter.request("PROMPT")

    assert result == {"async_ok": True}
    fake_client.responses.create.assert_awaited_once()


# --------------------------------------------------------------------------- #
# 3. _get_sdk_client raises when the API key is missing                       #
# --------------------------------------------------------------------------- #
def test_get_sdk_client_raises_when_missing(monkeypatch):
    _clear_caches()

    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    # Fake constructor that mimics the real SDK error type
    def _raise_openai_error(*_, **__):
        raise oc.OpenAIError("missing api key")

    monkeypatch.setattr(oc, "OpenAI", _raise_openai_error)

    with pytest.raises(RuntimeError, match="OpenAI API key not found"):
        oc._get_sdk_client()


# --------------------------------------------------------------------------- #
# 4. Async helper is cached (constructor runs once)                           #
# --------------------------------------------------------------------------- #
def test_get_async_sdk_client_is_cached(monkeypatch):
    _clear_caches()
    calls = {"n": 0}

    class FakeAsyncOpenAI:
        def __init__(self, *_, **__):
            calls["n"] += 1

    monkeypatch.setenv("OPENAI_API_KEY", "dummy")
    monkeypatch.setattr(oc, "AsyncOpenAI", FakeAsyncOpenAI)

    c1 = oc._get_async_sdk_client()
    c2 = oc._get_async_sdk_client()

    assert c1 is c2
    assert calls["n"] == 1
