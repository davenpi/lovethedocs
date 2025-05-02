from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    # Only for type checking, not runtime
    from lovethedocs.domain.docstyle import DocStyle


class LLMClientPort(Protocol):
    """Turns a prompt into JSON using a specific documentation style."""

    @property
    def style(self) -> "DocStyle":
        """The documentation style used by this client."""
        ...

    def request(self, prompt: str) -> dict:
        """Convert a prompt to a JSON response using the client's style."""
        ...


class JSONSchemaValidator(Protocol):
    """Implements a .validate(raw_json) that raises on failure."""

    def validate(self, raw_json: dict) -> None: ...
