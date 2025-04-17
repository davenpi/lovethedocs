from pathlib import Path
import tempfile

import src.utils as utils


class TestStripFormat:
    """Test the strip_format function"""

    def test_strip_format_single_line(self):
        """Test the strip_format function with a single line."""
        text = "```python\n" + 'print("Hello, world!")\n' + "```"
        stripped = utils.strip_format(text)
        expected = """print("Hello, world!")"""
        assert stripped == expected

    def test_strip_format_multiline(self):
        """Test the strip_format function on multiline text."""
        text = (
            "```python\n"
            + 'print("Hello, world!")\n'
            + 'print("Goodbye, world!")\n'
            + "def foo():\n"
            + '    print("Hello, world!")\n'
            + "```"
        )
        stripped = utils.strip_format(text)
        expected = (
            'print("Hello, world!")'
            + "\n"
            + 'print("Goodbye, world!")'
            + "\n"
            + "def foo():\n"
            + '    print("Hello, world!")'
        )
        assert stripped == expected


class TestLoadModules:
    """Test the load_modules function"""

    def test_load_modules_empty_directory(self):
        """Test the load_modules function with an empty directory"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            python_modules = utils.load_modules(temp_path)
            expected_modules = []
            assert python_modules == expected_modules

    def test_load_modules(self):
        """Test the load_modules function using a temporary directory"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create some dummy Python files
            (temp_path / "module1.py").write_text("print('module1')")
            (temp_path / "module2.py").write_text("print('module2')")
            (temp_path / "__init__.py").write_text("print('init')")
            (temp_path / "__main__.py").write_text("print('main')")
            (temp_path / "module3.txt").write_text("Not a Python file")

            python_modules = utils.load_modules(str(temp_path))
            expected_modules = ["module1.py", "module2.py"]

            assert python_modules == expected_modules

    def test_load_modules_string_path(self):
        """Test the load_modules function using a string path insted of Path."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create some dummy Python files
            (temp_path / "module1.py").write_text("print('module1')")
            (temp_path / "module2.py").write_text("print('module2')")
            (temp_path / "__init__.py").write_text("print('init')")
            (temp_path / "__main__.py").write_text("print('main')")
            (temp_path / "module3.txt").write_text("Not a Python file")

            python_modules = utils.load_modules(str(temp_path))
            expected_modules = ["module1.py", "module2.py"]

            assert python_modules == expected_modules


class TestConcatenateModules:
    """Test the concatenate_modules function"""

    def test_concatenate_modules_no_python_files(self):
        """Test the concatenate_modules function with no Python files"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create a non-Python file
            (temp_path / "module1.txt").write_text("Not a Python file")

            concatenated_code = utils.concatenate_modules(temp_path)
            expected_code = ""

            assert concatenated_code == expected_code

    def test_concatenate_modules(self):
        """Test the concatenate_modules function"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create some dummy Python files
            (temp_path / "module1.py").write_text("print('module1')")
            (temp_path / "module2.py").write_text("print('module2')")
            (temp_path / "module3.txt").write_text("Not a Python file")

            concatenated_code = utils.concatenate_modules(temp_path)
            expected_code = (
                "\nBEGIN module1.py\n"
                + "print('module1')\nEND module1.py\n"
                + "\nBEGIN module2.py\n"
                + "print('module2')\nEND module2.py\n"
            )

            assert concatenated_code == expected_code


class TestParseResponse:
    """Test the parse_response function"""

    def test_parse_single_response(self):
        """Test the parse_response function"""
        response = (
            f"{utils.START_PHRASE} module1.py\n"
            + "```python\n"
            + 'print("Hello, world!")\n'
            + "```\n"
            + f"{utils.END_PHRASE} module1.py\n"
        )
        parsed = utils.parse_response(response)
        expected_code = 'print("Hello, world!")'
        expected_dict = {"module1.py": expected_code}
        assert parsed == expected_dict

    def test_parse_multiple_responses(self):
        """Test the parse_response function with multiple responses"""
        response = (
            f"{utils.START_PHRASE} module1.py\n"
            + "```python\n"
            + 'print("Hello, world!")\n'
            + "```\n"
            + f"{utils.END_PHRASE} module1.py\n"
            + f"{utils.START_PHRASE} module2.py\n"
            + "```python\n"
            + 'print("Goodbye, world!")\n'
            + "```\n"
            + f"{utils.END_PHRASE} module2.py\n"
        )
        parsed = utils.parse_response(response)
        expected_code1 = 'print("Hello, world!")'
        expected_code2 = 'print("Goodbye, world!")'
        expected_dict = {
            "module1.py": expected_code1,
            "module2.py": expected_code2,
        }
        assert parsed == expected_dict


class TestWriteResponse:
    """Test the write_response function"""

    def test_write_response(self):
        """Test the write_response function"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            module_code_dict = {
                "module1.py": 'print("Hello, world!")',
                "module2.py": 'print("Goodbye, world!")',
            }
            utils.write_response(module_code_dict, temp_path)
            new_dir = temp_path / "_improved"
            assert new_dir.exists()
            assert (temp_path / "_improved" / "module1.py").read_text() == (
                'print("Hello, world!")'
            )
            assert (temp_path / "_improved" / "module2.py").read_text() == (
                'print("Goodbye, world!")'
            )


class TestIterProjectDirs:

    def test__iter_project_dirs_skips_ignored_dirs(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            base = Path(temp_dir)

            # Create directories
            included_dirs = ["docs", "src"]
            ignored_dirs = list(utils.IGNORED_DIRS)[:3]  # just use a subset

            for name in included_dirs + ignored_dirs:
                (base / name).mkdir()

            # Create nested directory to ensure recursion works
            (base / "src" / "nested").mkdir(parents=True)

            found = list(utils._iter_project_dirs(base))

            # Convert Path objects to directory names
            found_names = sorted(p.name for p in found)

            assert "docs" in found_names
            assert "src" in found_names
            assert "nested" in found_names

            for ignored in ignored_dirs:
                assert ignored not in found_names
