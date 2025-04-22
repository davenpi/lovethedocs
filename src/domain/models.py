from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class ObjectEdit:
    """
    A single function or class to patch inside a module.

    Attributes
    ----------
    id : str
        The id of the object to be edited in the AST.
    docstring : Optional[str]
        The new docstring for the object. If None, the docstring will be left unchanged.
    signature : Optional[str]
        The new signature for the object. If None, the signature will be left unchanged.
    """

    id: str  # e.g. ID001
    docstring: Optional[str] = None  # None → leave unchanged
    signature: Optional[str] = None  # canonical string, e.g. "(x: int) -> str"


@dataclass
class ModuleEdit:
    """
    A bundle of ObjectEdits that apply to one source file.

    Attributes
    ----------
    path : str
        The repo-relative path to the module.
    functions : List[ObjectEdit]
        A list of ObjectEdit instances representing functions to be edited.
    classes : List[ObjectEdit]
        A list of ObjectEdit instances representing classes to be edited.
    """

    path: str
    functions: List[ObjectEdit] = field(default_factory=list)
    classes: List[ObjectEdit] = field(default_factory=list)

    # convenience so the patcher can iterate in one go
    def all_objects(self) -> List[ObjectEdit]:
        return self.functions + self.classes
