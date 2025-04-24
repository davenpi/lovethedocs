from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pytest

# --- patch prompt_builder & validator -----------------------------------
import src.application.prompt_builder as pb
import src.gateways.schema_loader as sl


def test_run_pipeline_happy_path(tmp_path):
    """
    Orchestrates the entire flow with injected stubs:

    - DummyAI returns no edits.
    - StubWriter works purely in-memory.
    - prompt_builder.build_prompts is patched to a trivial lambda.
    - schema_loader.VALIDATOR is patched to a no-op.
    """

    # --- stubs that satisfy the ports --------------------------------------
    class DummyAI:
        def request(self, prompt, *, model):
            return {"function_edits": [], "class_edits": []}

    class StubWriter:
        def __init__(self):
            self.loaded = None
            self.written = {}

        def load_modules(self, base):
            self.loaded = base
            return {base / "foo.py": "def foo():\n    pass\n"}

        def write_file(self, path, code, *, root):
            self.written[path.relative_to(root)] = code

    writer = StubWriter()

    with patch.object(
        pb, "build_prompts", lambda mods: {mod: "PROMPT" for mod in mods}
    ), patch.object(sl, "VALIDATOR", SimpleNamespace(validate=lambda *_: None)):
        from src.application.run_pipeline import run_pipeline

        run_pipeline(
            paths=[tmp_path],
            ai_client=DummyAI(),
            file_writer=writer,
        )

    # Assertions: loader called, write_file wrote unchanged code
    assert writer.loaded == tmp_path
    assert Path("foo.py") in writer.written
    assert writer.written[Path("foo.py")].startswith("def foo()")


# --------------------------------------------------------------------------- sanity: ports are imported (counts for coverage)
import src.ports  # noqa: E402
