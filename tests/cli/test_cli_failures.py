from pathlib import Path

from typer.testing import CliRunner

from lovethedocs.cli.app import app

runner = CliRunner()


def test_cli_update_invalid_path(tmp_path: Path):
    bad = tmp_path / "does_not_exist"
    result = runner.invoke(app, ["update", str(bad)])
    # Typer uses Click's exit code 2 for bad params
    assert result.exit_code == 2
    assert "does not exist" in result.output


def test_cli_review_no_staged_edits(tmp_path: Path):
    # create empty dir, no .lovethedocs sub-folder
    tmp_path.mkdir(exist_ok=True)
    file = tmp_path / "foo.py"
    file.write_text("print(1)")
    # run review; should print info msg and exit 0
    result = runner.invoke(app, ["review", str(tmp_path)])
    assert result.exit_code == 0
    assert "No staged edits" in result.output


def test_cli_update_concurrency_flag(tmp_path: Path, monkeypatch):
    (tmp_path / "bar.py").write_text("print(2)")

    # stub out run_pipeline so we don't hit the network
    called = {}

    def fake_run_pipeline(paths, concurrency, **kw):
        called["paths"] = paths
        called["concurrency"] = concurrency
        return []

    monkeypatch.setattr(
        "lovethedocs.application.run_pipeline.run_pipeline", fake_run_pipeline
    )

    result = runner.invoke(
        app,
        ["update", "-c", "6", str(tmp_path)],
    )
    assert result.exit_code == 0
    assert called["concurrency"] == 6
