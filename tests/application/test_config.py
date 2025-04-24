from src.application.config import Settings


def test_settings_defaults_and_override():

    # default
    s = Settings()
    assert hasattr(s, "model_name") and isinstance(s.model_name, str)

    # override
    custom = Settings(model_name="custom-model")
    assert custom.model_name == "custom-model"
