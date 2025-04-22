# src/domain/models.py
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class FunctionEdit:
    qualname: str
    edit_type: str  # "docstring" | "signature" | "examples"
    docstring: Optional[str] = None
    signature: Optional[str] = None
    examples: Optional[List[str]] = None  # future‑use


@dataclass
class ClassEdit:
    qualname: str
    docstring: Optional[str] = None
    methods: List[FunctionEdit] = field(default_factory=list)


@dataclass
class ModuleEdit:
    path: str
    functions: List[FunctionEdit] = field(default_factory=list)
    classes: List[ClassEdit] = field(default_factory=list)

    # flatten for quick lookup
    def edits_by_qualname(self) -> dict[str, FunctionEdit | ClassEdit]:
        m: dict[str, FunctionEdit | ClassEdit] = {}
        for f in self.functions:
            m[f.qualname] = f
        for c in self.classes:
            m[c.qualname] = c
            for mtd in c.methods:
                m[f"{c.qualname}.{mtd.qualname}"] = mtd
        return m
