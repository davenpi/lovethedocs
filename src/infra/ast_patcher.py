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


# TODO: Fix the `_patch_doc` method to handle docstrings properly.
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
