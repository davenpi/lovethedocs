from src.application import prompt_builder


def test_build_multiple_prompts():
    test_modules = {
        "test_module.py": "print('Hello, World!')",
        "another_module.py": "print('Goodbye, World!')",
    }
    expected_prompts = {
        "test_module.py": (
            "BEGIN test_module.py\n" "print('Hello, World!')" "\nEND test_module.py"
        ),
        "another_module.py": (
            "BEGIN another_module.py\n"
            "print('Goodbye, World!')"
            "\nEND another_module.py"
        ),
    }
    built_prompts = prompt_builder.build_prompts(test_modules)
    assert (
        built_prompts == expected_prompts
    ), "The built prompts do not match the expected output."
