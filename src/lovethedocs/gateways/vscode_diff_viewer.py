import subprocess
from pathlib import Path

from lovethedocs.ports import DiffViewerPort


class VSCodeDiffViewer(DiffViewerPort):
    def view(self, original: Path, improved: Path) -> None:
        subprocess.run(["code", "-d", str(original), str(improved)], check=True)
