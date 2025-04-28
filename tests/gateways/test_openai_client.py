import json
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from src.gateways import openai_client as oc


def test_request_returns_parsed_json(monkeypatch):
    """
    * Patches oc._get_client to return a fake client, so no real network I/O.
    * Captures kwargs to verify that model and instructions are forwarded.
    """

    captured = {}

    # --- build a fake client that mimics the real OpenAI shape -------------
    class FakeResponses:
        def create(self, **kwargs):
            captured.update(kwargs)
            return SimpleNamespace(output_text=json.dumps({"ok": True}))

    fake_client = SimpleNamespace(responses=FakeResponses())

    # --- patch the lazy getter to always return our fake -------------------
    monkeypatch.setattr(oc, "_get_client", lambda: fake_client)

    result = oc.request("PROMPT", model="gpt-test")

    # -- assertions ---------------------------------------------------------
    assert result == {"ok": True}
    assert captured["model"] == "gpt-test"
    assert captured["instructions"]
    assert captured["text"]["format"]["type"] == "json_schema"


def test_get_api_key_raises_when_missing(monkeypatch):
    from src.gateways import openai_client as oc

    # Ensure env var absent and pretend no .env exists anywhere
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setattr("pathlib.Path.exists", lambda *_: False)

    with pytest.raises(RuntimeError, match="OPENAI_API_KEY not found"):
        oc._get_api_key()


def test_get_client_is_cached(monkeypatch):

    # Stub OpenAI class so we can count constructor calls
    calls = {"n": 0}

    class FakeOpenAI(SimpleNamespace):
        def __init__(self, api_key):
            calls["n"] += 1
            super().__init__(api_key=api_key, responses=SimpleNamespace())

    monkeypatch.setenv("OPENAI_API_KEY", "dummy")
    with patch.object(oc, "OpenAI", FakeOpenAI):
        c1 = oc._get_client()  # first call — should construct
        c2 = oc._get_client()  # second call — cached

    assert c1 is c2  # same object returned
    assert calls["n"] == 1  # constructor invoked only once
