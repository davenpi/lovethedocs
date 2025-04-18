import tempfile
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from src.editor import CodeEditor


class TestCodeEditor:
    start_phrase = "BEGIN lovethedocs"
    end_phrase = "END lovethedocs"

    @pytest.fixture
    def temp_project(self):
        with tempfile.TemporaryDirectory() as tmpdirname:
            tmp_path = Path(tmpdirname)
            # Create dummy Python modules
            (tmp_path / "module1.py").write_text("def foo():\n    pass\n")
            (tmp_path / "module2.py").write_text("def bar():\n    pass\n")
            yield tmp_path

    @pytest.fixture
    def mock_editor(self):
        # Fake OpenAI client and dummy response
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.output[0].content[0].text = (
            f"{self.start_phrase} module1.py\n```python\ndef foo():\n    '''Doc'''\n    pass\n```\n"
            f"{self.end_phrase} module1.py\n"
            f"{self.start_phrase} module2.py\n```python\ndef bar():\n    '''Doc'''\n    pass\n```\n"
            f"{self.end_phrase} module2.py\n"
        )
        mock_client.responses.create.return_value = mock_response
        return CodeEditor(
            client=mock_client,
            model="gpt-4o",
            start_phrase=self.start_phrase,
            end_phrase=self.end_phrase,
        )

    def test_process_directory_creates_improved_files(self, temp_project, mock_editor):
        mock_editor.process_directory(temp_project)

        improved_dir = temp_project / "_improved"
        assert improved_dir.exists()
        assert (improved_dir / "module1.py").exists()
        assert (improved_dir / "module2.py").exists()

        # Confirm content includes added docstring
        mod1_code = (improved_dir / "module1.py").read_text()
        mod2_code = (improved_dir / "module2.py").read_text()
        assert "def foo()" in mod1_code and "Doc" in mod1_code
        assert "def bar()" in mod2_code and "Doc" in mod2_code
