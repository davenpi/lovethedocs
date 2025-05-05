import subprocess
from pathlib import Path

from lovethedocs.ports import DiffViewerPort


class VSCodeDiffViewer(DiffViewerPort):
    def view(self, original: Path, staged: Path) -> None:
        subprocess.run(["code", "-d", str(original), str(staged)], check=True)
