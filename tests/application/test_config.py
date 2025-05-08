import pytest
from lovethedocs.application.config import Settings


def test_settings_default_values():
    """Test that Settings has the expected default values."""
    settings = Settings()
    assert settings.model == "gpt-4.1"
    assert settings.doc_style == "numpy"


def test_settings_custom_values():
    """Test that Settings can be initialized with custom values."""
    settings = Settings(model="gpt-3.5-turbo", doc_style="google")
    assert settings.model == "gpt-3.5-turbo"
    assert settings.doc_style == "google"


def test_settings_immutability():
    """Test that Settings instances are immutable (frozen=True)."""
    settings = Settings()
    with pytest.raises(AttributeError):
        settings.model = "different-model"
    
    with pytest.raises(AttributeError):
        settings.doc_style = "different-style"


def test_settings_equality():
    """Test that Settings instances compare correctly."""
    settings1 = Settings(model="model-a", doc_style="style-a")
    settings2 = Settings(model="model-a", doc_style="style-a")
    settings3 = Settings(model="model-b", doc_style="style-a")
    
    assert settings1 == settings2
    assert settings1 != settings3
    assert hash(settings1) == hash(settings2)