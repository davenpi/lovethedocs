import subprocess
from pathlib import Path

from src.ports import DiffViewerPort


class VSCodeDiffViewer(DiffViewerPort):
    def view(self, original: Path, improved: Path) -> None:
        subprocess.run(["code", "-d", str(original), str(improved)], check=True)
