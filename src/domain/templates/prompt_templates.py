from importlib import resources
from pathlib import Path


class UnknownStyleError(KeyError):
    """The requested style key is not found in the prompt template repository."""

    def __init__(self, style_key: str):
        super().__init__(f"Unknown style key: {style_key}")
        self.style_key = style_key


class PromptTemplateRepository:
    """Return the long-lived system prompt for a given doc-style key."""

    _template_dir = Path(resources.files(__package__))  # pkg-data directory

    def get(self, style_key: str) -> str:
        try:
            with open(self._template_dir / f"{style_key}.txt", encoding="utf-8") as fh:
                return fh.read()
        except FileNotFoundError as exc:
            raise UnknownStyleError(style_key) from exc
