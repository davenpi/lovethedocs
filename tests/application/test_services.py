from textwrap import dedent
from src.application.services import update_module_docs
from src.domain.models import FunctionEdit, ModuleEdit


def test_write_new_code_inserts_docstring():

    old_code = dedent(
        """
        def foo():
            pass
        """
    )
    mod_edit = ModuleEdit(function_edits=[FunctionEdit(qualname="foo", docstring="Hi")])

    new_code = update_module_docs(old_code, mod_edit)
    assert '"""Hi"""' in new_code
    assert new_code.endswith("pass\n")  # preserves body
