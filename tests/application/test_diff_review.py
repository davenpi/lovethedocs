import builtins
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from lovethedocs.application import diff_review
from lovethedocs.gateways.project_file_system import ProjectFileSystem


# ---------- fixtures ------------------------------------------------------ #
@pytest.fixture()
def tmp_project(tmp_path: Path):
    (tmp_path / "pkg").mkdir()
    root_py = tmp_path / "pkg" / "foo.py"
    root_py.write_text("print('hello')")
    fs = ProjectFileSystem(tmp_path)
    fs.stage_file(Path("pkg/foo.py"), "print('improved')")
    return fs


@pytest.fixture()
def dummy_viewer():
    viewer = Mock()
    viewer.view = Mock()
    return viewer


# ---------- unit tests ---------------------------------------------------- #
def test_no_staged_files(tmp_path, dummy_viewer, capsys):
    fs = ProjectFileSystem(tmp_path)  # nothing staged
    diff_review.batch_review(fs, diff_viewer=dummy_viewer, interactive=False)

    captured = capsys.readouterr().out
    assert "No staged files" in captured
    dummy_viewer.view.assert_not_called()


def test_accepts_change(tmp_project, dummy_viewer, monkeypatch):
    monkeypatch.setattr(builtins, "input", lambda _: "y")

    diff_review.batch_review(
        tmp_project,
        diff_viewer=dummy_viewer,
        interactive=True,
    )

    # staged file removed ⇒ accepted
    assert not tmp_project.staged_root.exists()
    dummy_viewer.view.assert_called_once()


def test_rejects_change(tmp_project, dummy_viewer, monkeypatch):
    monkeypatch.setattr(builtins, "input", lambda _: "n")
    diff_review.batch_review(tmp_project, diff_viewer=dummy_viewer, interactive=True)

    # staged file still there ⇒ rejected
    assert any(tmp_project.staged_root.rglob("*.py"))
    dummy_viewer.view.assert_called_once()


def test_noninteractive_never_applies(tmp_project, dummy_viewer):
    diff_review.batch_review(tmp_project, diff_viewer=dummy_viewer, interactive=False)

    # no prompt, nothing applied
    assert any(tmp_project.staged_root.rglob("*.py"))
    dummy_viewer.view.assert_called_once()
