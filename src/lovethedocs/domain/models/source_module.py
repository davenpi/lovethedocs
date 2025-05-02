"""
Domain-level representation of a single Python module.

Only *data* + *pure computation* live here—no I/O, no LLM calls.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property
from pathlib import Path

import libcst as cst
from libcst import metadata


@dataclass(frozen=True)
class SourceModule:
    """
    Immutable snapshot of a file's source code.

    Parameters
    ----------
    path
        Path **relative to the project root** (so diffs are stable).
    code
        Full text of the module.
    """

    path: Path
    code: str

    # --------------------------------------------------------------------- #
    #  Derived data—computed lazily so callers pay only for what they use   #
    # --------------------------------------------------------------------- #

    @cached_property
    def objects(self) -> list[str]:
        """
        Fully-qualified names of every function / class in module.

        Example
        -------
        >>> sm.objects
        ['helper', 'MyClass', 'MyClass.method', 'main']
        """
        tree = cst.parse_module(self.code)
        wrapper = metadata.MetadataWrapper(tree)
        collector = _ObjCollector()
        wrapper.visit(collector)
        return collector.qualnames

    # Convenience constructor -------------------------------------------------
    @classmethod
    def from_path(cls, file_path: Path, *, root: Path | None = None) -> "SourceModule":
        """
        Read a .py file from disk and return an instance.

        `root` lets the caller store the path relative to a project root,
        which keeps prompts and diffs tidy.
        """
        text = file_path.read_text(encoding="utf-8")
        rel = file_path if root is None else file_path.relative_to(root)
        return cls(path=rel, code=text)


# --------------------------------------------------------------------------- #
#  Internal helper: collects qualified names while traversing the CST         #
# --------------------------------------------------------------------------- #
class _ObjCollector(cst.CSTVisitor):
    """Build a list like ['foo', 'Bar', 'Bar.baz'] while walking the tree."""

    def __init__(self) -> None:
        self._stack: list[str] = []
        self.qualnames: list[str] = []

    # ---- helpers ----------------------------------------------------------
    def _push(self, name: str) -> None:
        self._stack.append(name)
        self.qualnames.append(".".join(self._stack))

    def _pop(self) -> None:  # noqa: D401
        self._stack.pop()

    # ---- LibCST hooks -----------------------------------------------------
    def visit_FunctionDef(self, node):  # type: ignore  [override]
        self._push(node.name.value)

    def leave_FunctionDef(self, node):  # type: ignore  [override]
        self._pop()

    def visit_ClassDef(self, node):  # type: ignore  [override]
        self._push(node.name.value)

    def leave_ClassDef(self, node):  # type: ignore  [override]
        self._pop()
