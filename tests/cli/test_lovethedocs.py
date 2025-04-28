import sys

import pytest

from src.cli import lovethedocs


def test_cli_main_invokes_pipeline(monkeypatch):
    """
    * Replaces sys.argv so argparse thinks the user typed two paths.
    * Patches run_pipeline.run_pipeline to a stub that records its call.
    * Asserts main() exits normally and passes the parsed paths verbatim.
    """

    called = {}

    def fake_run(paths, review_diffs=False):
        called["paths"] = paths

    monkeypatch.setattr("src.cli.lovethedocs.run_pipeline.run_pipeline", fake_run)
    monkeypatch.setattr(sys, "argv", ["lovethedocs", "pkg1", "pkg2"])

    # main should not raise and should forward the paths
    lovethedocs.main()
    assert called["paths"] == ["pkg1", "pkg2"]

    # Missing arg → argparse triggers SystemExit (optional extra check)
    monkeypatch.setattr(sys, "argv", ["lovethedocs"])
    with pytest.raises(SystemExit):
        lovethedocs.main()
