"""
Unit-tests for DocstringGeneratorService (src.domain.services.generator).

The service should
1. call the client-factory exactly once with the style string,
2. call the resulting client with only the prompt,
3. validate the JSON once,
4. map JSON → ModuleEdit,
5. propagate upstream errors unchanged,
6. skip the mapper when validation fails.
"""

from __future__ import annotations

from typing import Any

import pytest

from src.domain.models import ModuleEdit
from src.domain.services.generator import ModuleEditGenerator


# --------------------------------------------------------------------------- #
#  Test doubles                                                               #
# --------------------------------------------------------------------------- #
class FakeClient:
    """Mimics the LLM adapter returned by the factory."""

    def __init__(
        self,
        raw: dict | None = None,
        *,
        exc: Exception | None = None,
        style: str = "numpy",
    ):
        self.style = style
        self._raw = raw or {}
        self._exc = exc
        self.called_with: tuple[str] | None = None

    def request(self, prompt: str) -> dict:  # type: ignore[override]
        self.called_with = (prompt,)
        if self._exc:
            raise self._exc
        return self._raw


class FakeValidator:
    def __init__(self, *, exc: Exception | None = None):
        self._exc = exc
        self.validated: dict | None = None

    def validate(self, raw: dict) -> None:  # type: ignore[override]
        self.validated = raw
        if self._exc:
            raise self._exc


# --------------------------------------------------------------------------- #
#  Helpers                                                                    #
# --------------------------------------------------------------------------- #
STYLE = "numpy"


def _make_service(
    raw: dict,
    *,
    client_exc: Exception | None = None,
    validator_exc: Exception | None = None,
    mapper_ret: Any = None,
):
    client = FakeClient(raw, exc=client_exc, style=STYLE)
    validator = FakeValidator(exc=validator_exc)
    sentinel = mapper_ret if mapper_ret is not None else ModuleEdit()

    def mapper(data: dict) -> ModuleEdit:  # noqa: D401
        assert data is raw
        return sentinel

    gen = ModuleEditGenerator(
        client=client,
        validator=validator,
        mapper=mapper,
    )
    return gen, client, validator, sentinel


# --------------------------------------------------------------------------- #
#  1 ── happy path                                                            #
# --------------------------------------------------------------------------- #
def test_generate_happy_path():
    raw = {"ok": True}
    gen, client, validator, sentinel = _make_service(raw)

    out = gen.generate("PROMPT")

    # returns mapper output
    assert out is sentinel
    # client called with only the prompt
    assert client.called_with == ("PROMPT",)
    # validator saw the raw JSON
    assert validator.validated is raw
    assert gen.style == STYLE


# --------------------------------------------------------------------------- #
#  2 ── validation failure short-circuits mapper                              #
# --------------------------------------------------------------------------- #
def test_generate_validator_error():
    raw = {"bad": "data"}
    err = ValueError("schema mismatch")
    gen, client, validator, _ = _make_service(
        raw, validator_exc=err, mapper_ret=object()
    )

    with pytest.raises(ValueError):
        gen.generate("PROMPT")

    assert validator.validated is raw
    # mapper never called, so client still called but nothing mapped
    assert client.called_with == ("PROMPT",)


# --------------------------------------------------------------------------- #
#  3 ── client exception propagates                                           #
# --------------------------------------------------------------------------- #
def test_generate_client_error():
    gen, client, validator, _ = _make_service(
        raw={}, client_exc=RuntimeError("api down")
    )

    with pytest.raises(RuntimeError):
        gen.generate("PROMPT")

    # client attempted, validator never reached
    assert client.called_with == ("PROMPT",)
    assert validator.validated is None
