"""
Tiny sanity-checks for PromptTemplateRepository.
"""

from __future__ import annotations

import pytest

from lovethedocs.domain.templates.prompt_templates import (
    PromptTemplateRepository,
    UnknownStyleError,
)


# --------------------------------------------------------------------------- #
# 1 ── Reads template text from the configured directory                      #
# --------------------------------------------------------------------------- #
def test_get_returns_file_contents(tmp_path):
    repo = PromptTemplateRepository()

    # Redirect the private template directory to a temp dir
    repo._template_dir = tmp_path  # type: ignore[attr-defined]

    style_key = "numpy"
    expected = "Long-lived system prompt"
    (tmp_path / f"{style_key}.txt").write_text(expected, encoding="utf-8")

    assert repo.get(style_key) == expected


# --------------------------------------------------------------------------- #
# 2 ── Raises UnknownStyleError when file absent                              #
# --------------------------------------------------------------------------- #
def test_get_unknown_style(tmp_path):
    repo = PromptTemplateRepository()
    repo._template_dir = tmp_path  # type: ignore[attr-defined]

    with pytest.raises(UnknownStyleError) as exc:
        repo.get("missing")

    assert exc.value.style_key == "missing"
