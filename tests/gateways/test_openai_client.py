import json
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from lovethedocs.gateways import openai_client as oc


# --------------------------------------------------------------------------- #
# Helpers                                                                     #
# --------------------------------------------------------------------------- #
class _DummyStyle:  # minimal stand-in for DocStyle
    name = "dummy"


def _clear_client_cache() -> None:
    """Reset the lru_cache between tests so each test starts fresh."""
    oc._get_sdk_client.cache_clear()


# --------------------------------------------------------------------------- #
# 1. request() parses JSON and forwards kwargs                                 #
# --------------------------------------------------------------------------- #
def test_request_returns_parsed_json(monkeypatch):
    _clear_client_cache()
    captured = {}

    # --- fake SDK client ----------------------------------------------------
    class FakeResponses:
        def create(self, **kwargs):
            captured.update(kwargs)
            return SimpleNamespace(output_text=json.dumps({"ok": True}))

    fake_client = SimpleNamespace(responses=FakeResponses())

    # patch: use our fake SDK client, and short-circuit the prompt loader
    monkeypatch.setattr(oc, "_get_sdk_client", lambda: fake_client)
    monkeypatch.setattr(oc, "_PROMPTS", SimpleNamespace(get=lambda _n: "TEST_PROMPT"))

    # instantiate the adapter under test
    adapter = oc.OpenAIClientAdapter(style=_DummyStyle(), model="gpt-test")

    result = adapter.request("PROMPT")

    assert result == {"ok": True}
    assert captured["model"] == "gpt-test"
    assert captured["instructions"] == "TEST_PROMPT"
    assert captured["text"]["format"]["type"] == "json_schema"


# --------------------------------------------------------------------------- #
# 2. _get_sdk_client raises if the API key is missing                          #
# --------------------------------------------------------------------------- #
def test_get_sdk_client_raises_when_missing(monkeypatch):
    _clear_client_cache()

    # Stub that mimics the SDK raising when no key is configured
    class _RaisesValueError:
        def __init__(self, *_, **__):
            raise ValueError("missing api key")

    monkeypatch.delenv("OPENAI_API_KEY", raising=False)  # ensure env var absent
    monkeypatch.setattr(oc, "OpenAI", _RaisesValueError)  # patch constructor

    with pytest.raises(RuntimeError):
        oc._get_sdk_client()


# --------------------------------------------------------------------------- #
# 3. _get_sdk_client is cached (constructor runs once)                         #
# --------------------------------------------------------------------------- #
def test_get_sdk_client_is_cached(monkeypatch):
    _clear_client_cache()

    calls = {"n": 0}

    class FakeOpenAI:
        def __init__(self, *args, **kwargs):  # accept any signature
            calls["n"] += 1
            self.responses = SimpleNamespace()  # lightweight placeholder

    monkeypatch.setenv("OPENAI_API_KEY", "dummy")  # key to satisfy flow
    monkeypatch.setattr(oc, "OpenAI", FakeOpenAI)  # patch constructor

    c1 = oc._get_sdk_client()  # first call – builds
    c2 = oc._get_sdk_client()  # second call – cached

    assert c1 is c2
    assert calls["n"] == 1
