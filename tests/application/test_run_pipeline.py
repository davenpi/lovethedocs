from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pytest

# --- patch prompt_builder & validator -----------------------------------
import src.gateways.schema_loader as sl
import src.domain.services.prompt_builder as pb


def _stub_ai_noop():
    class DummyAI:
        def request(self, prompt, *, model, style):
            # no edits ⇒ update_module_docs returns the original source
            return {"function_edits": [], "class_edits": []}

    return DummyAI()


def test_run_pipeline_happy_path(tmp_path):
    """
    Orchestrates the entire flow with injected stubs:

    - DummyAI returns no edits.
    - StubWriter works purely in-memory.
    - prompt_builder.build_prompts is patched to a trivial lambda.
    - schema_loader.VALIDATOR is patched to a no-op.
    """

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
        pb.PromptBuilder,
        "build",
        lambda _self, mods, *, style="numpy": {mod: "PROMPT" for mod in mods},
    ), patch.object(sl, "VALIDATOR", SimpleNamespace(validate=lambda *_: None)):
        from src.application.run_pipeline import run_pipeline

        run_pipeline(
            paths=[tmp_path],
            ai_client=_stub_ai_noop(),
            file_writer=writer,
        )

    # Assertions: loader called, write_file wrote unchanged code
    assert writer.loaded == tmp_path
    assert Path("foo.py") in writer.written
    assert writer.written[Path("foo.py")].startswith("def foo()")


def test_run_pipeline_single_python_file(tmp_path):
    """Passing a lone .py file should skip load_modules and still write output."""
    file_path = tmp_path / "solo.py"
    file_path.write_text("def solo():\n    pass\n", encoding="utf-8")

    class StubWriter:
        def __init__(self):
            self.written = {}

        def load_modules(self, *_):
            raise AssertionError("load_modules must not be called for a single file")

        def write_file(self, path, code, *, root):
            # path is already relative to root
            self.written[path] = code

    writer = StubWriter()

    with patch.object(
        pb.PromptBuilder,
        "build",
        lambda _self, mods, *, style="numpy": {m: "PROMPT" for m in mods},
    ), patch.object(sl, "VALIDATOR", SimpleNamespace(validate=lambda *_: None)):
        from src.application.run_pipeline import run_pipeline

        run_pipeline(
            paths=str(file_path), ai_client=_stub_ai_noop(), file_writer=writer
        )

    assert Path("solo.py") in writer.written
    assert "def solo" in writer.written[Path("solo.py")]


def test_run_pipeline_mixed_inputs(tmp_path):
    """
    A list containing both a directory and an individual .py file should
    process each branch correctly.
    """
    # directory with two modules
    pkg_dir = tmp_path / "mypkg"
    pkg_dir.mkdir()
    (pkg_dir / "__init__.py").write_text("", encoding="utf-8")
    (pkg_dir / "foo.py").write_text("def foo():\n    pass\n", encoding="utf-8")

    # stand-alone file
    bar_file = tmp_path / "bar.py"
    bar_file.write_text("def bar():\n    pass\n", encoding="utf-8")

    class StubWriter:
        def __init__(self):
            self.loaded = []
            self.written = {}

        def load_modules(self, base):
            # mimic file-system loading so keys are Path objects relative to base
            self.loaded.append(base)
            return {
                p.relative_to(base): p.read_text(encoding="utf-8")
                for p in base.rglob("*.py")
            }

        def write_file(self, path, code, *, root):
            # record for later assertions
            self.written[(root, path)] = code

    writer = StubWriter()

    with patch.object(
        pb.PromptBuilder,
        "build",
        lambda _self, mods, *, style="numpy": {m: "PROMPT" for m in mods},
    ), patch.object(sl, "VALIDATOR", SimpleNamespace(validate=lambda *_: None)):
        from src.application.run_pipeline import run_pipeline

        run_pipeline(
            paths=[pkg_dir, bar_file],
            ai_client=_stub_ai_noop(),
            file_writer=writer,
        )

    # directory branch exercised
    assert pkg_dir in writer.loaded

    # directory’s module written
    assert any(
        root == pkg_dir and path.name == "foo.py" for root, path in writer.written
    )

    # single-file branch exercised
    assert any(path.name == "bar.py" for _, path in writer.written)


# --------------------------------------------------------------------------- sanity: ports are imported (counts for coverage)
import src.ports  # noqa: E402
