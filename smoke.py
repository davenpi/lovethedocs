import libcst as cst

from src.domain.models import FunctionEdit
from src.infra.ast_patcher import DocSigPatcher

src = '''
class A:
    def m(self, x): 
        """old"""
        return x
'''

edits = {
    "A.m": FunctionEdit(
        qualname="A.m",
        edit_type="signature",
        docstring="new",
        signature="(self, x: int) -> int",
    )
}
new_code = cst.parse_module(src).visit(DocSigPatcher(edits)).code
assert "def m(self, x: int) -> int" in new_code
assert '"""new"""' in new_code
