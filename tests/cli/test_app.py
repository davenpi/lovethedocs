from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from lovethedocs.cli import app

runner = CliRunner()


def test_version_command():
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "lovethedocs version" in result.output


@patch("lovethedocs.cli.app.run_pipeline")
@patch("lovethedocs.cli.app.diff_review.batch_review")
def test_update_triggers_pipeline_and_optional_review(
    mock_review, mock_run_pipeline, tmp_path
):
    mock_fs = MagicMock()
    mock_run_pipeline.return_value = [mock_fs]

    result = runner.invoke(app, ["update", "-r", str(tmp_path)])
    assert result.exit_code == 0
    mock_run_pipeline.assert_called_once()
    mock_review.assert_called_once()


@patch("lovethedocs.cli.app.ProjectFileSystem")
@patch("lovethedocs.cli.app.diff_review.batch_review")
def test_review_skips_if_no_staged_edits(mock_review, mock_fs_class, tmp_path):
    mock_fs = MagicMock()
    mock_fs.staged_root.exists.return_value = False
    mock_fs_class.return_value = mock_fs

    result = runner.invoke(app, ["review", str(tmp_path)])
    assert "No staged edits found" in result.output
    mock_review.assert_not_called()


@patch("lovethedocs.cli.app.ProjectFileSystem")
@patch("lovethedocs.cli.app.diff_review.batch_review")
def test_review_runs_if_staged_edits_exist(mock_review, mock_fs_class, tmp_path):
    mock_fs = MagicMock()
    mock_fs.staged_root.exists.return_value = True
    mock_fs_class.return_value = mock_fs

    result = runner.invoke(app, ["review", str(tmp_path)])
    assert result.exit_code == 0
    mock_review.assert_called_once()


@patch("lovethedocs.cli.app.shutil.rmtree")
def test_clean_removes_lovethedocs_with_yes(mock_rmtree, tmp_path):
    clean_path = tmp_path / ".lovethedocs"
    clean_path.mkdir(parents=True)

    result = runner.invoke(app, ["clean", "-y", str(tmp_path)])
    assert result.exit_code == 0
    mock_rmtree.assert_called_once_with(clean_path)


@patch("lovethedocs.cli.app.shutil.rmtree")
def test_clean_skips_if_nothing_to_clean(mock_rmtree, tmp_path):
    result = runner.invoke(app, ["clean", "-y", str(tmp_path)])
    assert "Nothing to clean" in result.output
    mock_rmtree.assert_not_called()


def test_update_fails_cleanly_on_unknown_style(tmp_path):
    result = runner.invoke(app, ["update", "-s", "reST", str(tmp_path)])
    assert result.exit_code != 0
    print("-" * 20)
    print(result.output)
    assert "Unknown documentation style" in result.output


def test_review_fails_cleanly_on_unknown_viewer(tmp_path):
    # Simulate bad viewer input
    result = runner.invoke(app, ["review", "-v", "sublime", str(tmp_path)])
    assert result.exit_code != 0
    assert "Viewer 'sublime' is not yet supported." in result.output
