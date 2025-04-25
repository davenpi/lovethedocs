import libcst as cst

from src.domain.models import ModuleEdit
from src.application.transformers import DocSigPatcher


def update_module_docs(old_module, module_edit: ModuleEdit):
    edits_by_qual = module_edit.map_qnames_to_edits()
    patcher = DocSigPatcher(edits_by_qual)
    updated_code = cst.parse_module(old_module).visit(patcher).code
    return updated_code
