from src.application import build_prompt


class TestApplication:

    def test_build_prompt(self):
        test_prompt = "def test(): pass"
        built_prompt = build_prompt.build_prompt(test_prompt)
        assert (
            built_prompt == test_prompt
        ), "The built prompt does not match the expected output."
