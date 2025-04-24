from textwrap import dedent
from src.application.services import write_new_code
from src.domain.models import FunctionEdit, ModuleEdit


def test_write_new_code_inserts_docstring():

    old_code = dedent(
        """
        def foo():
            pass
        """
    )
    mod_edit = ModuleEdit(function_edits=[FunctionEdit(qualname="foo", docstring="Hi")])

    new_code = write_new_code(old_code, mod_edit)
    assert '"""Hi"""' in new_code
    assert new_code.endswith("pass\n")  # preserves body
