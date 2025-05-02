# src/domain/models.py
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class FunctionEdit:
    """
    Represents an edit to a function's docstring and/or signature.

    Attributes
    ----------
    qualname : str
        The fully qualified name of the function to edit.
    docstring : Optional[str]
        The new docstring for the function, or None if unchanged.
    signature : Optional[str]
        The new signature for the function, or None if unchanged.
    """

    qualname: str
    docstring: Optional[str] = None
    signature: Optional[str] = None


@dataclass
class ClassEdit:
    """
    Represents an edit to a class's docstring and its methods' docstrings/signatures.

    Attributes
    ----------
    qualname : str
        The fully qualified name of the class to edit.
    docstring : Optional[str]
        The new docstring for the class, or None if unchanged.
    method_edits : List[FunctionEdit]
        A list of edits to the class's methods.
    """

    qualname: str
    docstring: Optional[str] = None
    method_edits: List[FunctionEdit] = field(default_factory=list)


@dataclass
class ModuleEdit:
    """
    Represents a collection of edits to functions and classes within a module.

    Attributes
    ----------
    function_edits : List[FunctionEdit]
        A list of edits to top-level functions in the module.
    class_edits : List[ClassEdit]
        A list of edits to classes in the module.
    """

    function_edits: List[FunctionEdit] = field(default_factory=list)
    class_edits: List[ClassEdit] = field(default_factory=list)

    def map_qnames_to_edits(
        self,
    ) -> dict[str, FunctionEdit | ClassEdit]:
        """
        Return a mapping from qualified names to their corresponding edit objects.

        This method flattens the function and class edits, including method edits from
        classes, into a single dictionary keyed by qualified name. Method edits are
        included both as part of their parent class and as individual entries for
        direct access.

        Returns
        -------
        dict[str, FunctionEdit | ClassEdit]
            A mapping from qualified names to their corresponding edit objects.
        """
        edits = []
        for f_edit in self.function_edits:
            edits.append(f_edit)
        for c_edit in self.class_edits:
            edits.append(c_edit)
            for mtd_edit in c_edit.method_edits:
                edits.append(mtd_edit)
        return {edit.qualname: edit for edit in edits}
