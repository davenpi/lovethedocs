# import textwrap
# import libcst as cst
# from src.domain.models import ClassEdit, FunctionEdit


# def _strip_quotes(s: str) -> str:
#     """Remove leading/trailing triple quotes & surrounding whitespace."""
#     s = textwrap.dedent(s).strip()
#     for q in ('"""', "'''"):
#         if s.startswith(q) and s.endswith(q):
#             return s[len(q) : -len(q)].strip()
#     return s


# def _make_docstring_stmt(raw: str) -> cst.SimpleStatementLine:
#     """
#     Return a *clean* docstring statement with **no** leading blank line
#     and a real newline before the closing quotes (PEP‑257 style).
#     """
#     clean = _strip_quotes(raw)
#     return cst.SimpleStatementLine(
#         body=[cst.Expr(cst.SimpleString(f'"""{clean}\n"""'))],
#         leading_lines=[],  # <- kills the stray blank line
#     )


# class DocSigPatcher(cst.CSTTransformer):
#     """
#     Receives a mapping  qualname -> edit  and applies:
#       • docstring replacement / insertion
#       • signature replacement (functions only)
#     It leaves *all other code & whitespace intact*.
#     """

#     def __init__(self, edits_by_qualname: dict[str, FunctionEdit | ClassEdit]):
#         self.edits = edits_by_qualname
#         self.scope: list[str] = []  # stack for nested qualnames

#     @staticmethod
#     def _patch_docstring(block: cst.IndentedBlock, new_doc: str) -> cst.IndentedBlock:
#         """
#         Return a copy of *block* whose first statement is the given docstring.
#         If the block already starts with a docstring, replace it;
#         otherwise insert it at the top, preserving indentation.
#         """
#         new_doc_stmt = _make_docstring_stmt(new_doc)  # clean it up

#         body = list(block.body)
#         if (
#             body
#             and isinstance(body[0], cst.SimpleStatementLine)
#             and isinstance(body[0].body[0], cst.Expr)
#             and isinstance(
#                 body[0].body[0].value, (cst.SimpleString, cst.ConcatenatedString)
#             )
#         ):
#             body[0] = new_doc_stmt  # replace existing
#         else:
#             body.insert(0, new_doc_stmt)  # insert fresh
#         return block.with_changes(body=body)

#     # ---------- class handling ----------
#     def visit_ClassDef(self, node):
#         self.scope.append(node.name.value)

#     def leave_ClassDef(self, original, updated):
#         qual = ".".join(self.scope)
#         edit = self.edits.get(qual)
#         if isinstance(edit, ClassEdit) and edit.docstring:
#             updated = updated.with_changes(
#                 body=self._patch_docstring(updated.body, edit.docstring)
#             )
#         self.scope.pop()
#         return updated

#     # ---------- function / method handling ----------
#     def visit_FunctionDef(self, node):
#         self.scope.append(node.name.value)

#     def leave_FunctionDef(self, original, updated):
#         qual = ".".join(self.scope)
#         edit = self.edits.get(qual)
#         if isinstance(edit, FunctionEdit):
#             # 1. docstring
#             if edit.docstring:
#                 updated = updated.with_changes(
#                     body=self._patch_docstring(updated.body, edit.docstring)
#                 )
#             # 2. signature
#             if edit.signature:
#                 # inside leave_FunctionDef
#                 raw = edit.signature.strip()

#                 # 1. Build a minimal, valid stub LibCST can parse
#                 if raw.startswith("def"):
#                     sig_code = raw  # already a full header
#                     if sig_code.endswith(":"):  # add body stub if model omitted it
#                         sig_code += " pass"
#                 else:
#                     sig_code = f"def f{raw}: pass"  # older path

#                 # 2. Parse and copy params + returns
#                 func_def = cst.parse_module(sig_code).body[0]  # FunctionDef
#                 updated = updated.with_changes(
#                     params=func_def.params,
#                     returns=func_def.returns,
#                 )
#                 # sig_code = f"def f{edit.signature}: pass"
#                 # func_def = cst.parse_module(sig_code).body[0]  # FunctionDef node
#                 # params = func_def.params
#                 # updated = updated.with_changes(params=params, returns=func_def.returns)
#         self.scope.pop()
#         return updated
# src/infra/ast_patcher.py
import textwrap
import libcst as cst
from src.domain.models import ClassEdit, FunctionEdit


def _make_docstring_stmt(body: str) -> cst.SimpleStatementLine:
    """
    Wrap *body* in triple quotes, ensure one real newline before the closing
    quotes, and remove any leading indentation the model might have emitted.
    """
    clean = textwrap.dedent(body).rstrip()
    return cst.SimpleStatementLine(
        body=[cst.Expr(cst.SimpleString(f'"""{clean}\n"""'))],
        leading_lines=[],  # no blank line above the docstring
    )


def _parse_header(header: str) -> cst.FunctionDef:
    """
    Parse a stand‑alone 'def …:' header into a FunctionDef node from which we
    can copy .params and .returns.  If the header ends with ':', we append
    'pass' so the snippet is valid Python for LibCST.
    """
    hdr = header.strip()
    if hdr.endswith(":"):
        hdr += " pass"
    return cst.parse_module(hdr).body[0]  # FunctionDef


class DocSigPatcher(cst.CSTTransformer):
    """
    Apply FunctionEdit / ClassEdit objects to a module:
      • replace/insert docstrings
      • replace function signatures
    """

    def __init__(self, edits_by_qualname: dict[str, FunctionEdit | ClassEdit]):
        self._edits = edits_by_qualname
        self._scope: list[str] = []  # qualname breadcrumb

    # ----------------- internal helpers -----------------
    def _fqname(self) -> str:
        return ".".join(self._scope)

    def _patch_doc(self, block: cst.IndentedBlock, text: str) -> cst.IndentedBlock:
        """Replace first stmt with docstring or insert one if missing."""
        doc_stmt = _make_docstring_stmt(text)
        body = list(block.body)

        if (
            body
            and isinstance(body[0], cst.SimpleStatementLine)
            and isinstance(body[0].body[0], cst.Expr)
            and isinstance(
                body[0].body[0].value, (cst.SimpleString, cst.ConcatenatedString)
            )
        ):
            body[0] = doc_stmt  # replace existing docstring
        else:
            body.insert(0, doc_stmt)  # insert new docstring

        return block.with_changes(body=body)

    # ----------------- class traversal -----------------
    def visit_ClassDef(self, node: cst.ClassDef) -> None:
        self._scope.append(node.name.value)

    def leave_ClassDef(
        self, original: cst.ClassDef, updated: cst.ClassDef
    ) -> cst.ClassDef:
        edit = self._edits.get(self._fqname())
        if isinstance(edit, ClassEdit) and edit.docstring:
            updated = updated.with_changes(
                body=self._patch_doc(updated.body, edit.docstring)
            )
        self._scope.pop()
        return updated

    # ----------------- function / method traversal -----------------
    def visit_FunctionDef(self, node: cst.FunctionDef) -> None:
        self._scope.append(node.name.value)

    def leave_FunctionDef(
        self, original: cst.FunctionDef, updated: cst.FunctionDef
    ) -> cst.FunctionDef:
        edit = self._edits.get(self._fqname())
        if isinstance(edit, FunctionEdit):
            # 1. Docstring
            if edit.docstring:
                updated = updated.with_changes(
                    body=self._patch_doc(updated.body, edit.docstring)
                )

            # 2. Signature
            if edit.signature:
                stub = _parse_header(edit.signature)
                updated = updated.with_changes(params=stub.params, returns=stub.returns)

        self._scope.pop()
        return updated
