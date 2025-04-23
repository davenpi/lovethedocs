# src/domain/models.py
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class FunctionEdit:
    qualname: str
    docstring: Optional[str] = None
    signature: Optional[str] = None


@dataclass
class ClassEdit:
    qualname: str
    docstring: Optional[str] = None
    method_edits: List[FunctionEdit] = field(default_factory=list)


@dataclass
class ModuleEdit:
    function_edits: List[FunctionEdit] = field(default_factory=list)
    class_edits: List[ClassEdit] = field(default_factory=list)

    def map_qnames_to_edits(module_edit: ModuleEdit) -> dict[FunctionEdit | ClassEdit]:
        """
        Flatten the module edits into a map from qualname to edit.

        Note the method edits are included in the class edits as well. So there is
        redundancy in the data structure.

        For example::

            ModuleEdit(
                function_edits=[FunctionEdit(qualname="foo")],
                class_edits=[
                    ClassEdit(
                        qualname="Bar",
                        docstring="?",
                        method_edits=[FunctionEdit(qualname="Bar.baz")],
                    )
                ],
            )
        produces the following map::

            {
                "foo": FunctionEdit(qualname="foo"),
                "Bar": ClassEdit(
                            qualname="Bar",
                            docstring="?",
                            method_edits=[FunctionEdit(qualname="Bar.baz")]
                        ),
                "Bar.baz": FunctionEdit(qualname="Bar.baz"),
            }
        where the 'Bar.baz' edit is included in both the class edit and its own entry.
        This is to allow for easy access to the edits by qualname for the patcher.
        """
        edits = []
        for f_edit in module_edit.function_edits:
            edits.append(f_edit)
        for c_edit in module_edit.class_edits:
            edits.append(c_edit)
            for mtd_edit in c_edit.method_edits:
                edits.append(mtd_edit)
        qualname_to_edit = {edit.qualname: edit for edit in edits}
        return qualname_to_edit
