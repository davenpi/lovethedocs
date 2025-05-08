from __future__ import annotations

from dataclasses import dataclass

from lovethedocs.domain.models import SourceModule


@dataclass(slots=True)
class UpdateResult:
    """
    Represents the result of a documentation update operation.

    Attributes
    ----------
    module : SourceModule
        The source module that was processed.
    new_code : str or None
        The patched source code, or None if the update failed.
    error : Exception or None
        The exception raised during the update, or None on success.

    A convenience `.ok` property indicates success.
    """

    module: SourceModule
    new_code: str | None = None
    error: Exception | None = None

    @property
    def ok(self) -> bool:  # noqa: D401
        """
        Return True if the update succeeded, otherwise False.

        Returns
        -------
        bool
            True if no error occurred; False otherwise.
        """
        return self.error is None
