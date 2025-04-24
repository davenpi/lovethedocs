import libcst as cst

from src.domain.models import ModuleEdit
from src.application.transformers import DocSigPatcher


def write_new_code(old_code, module_edit: ModuleEdit):
    edits_by_qual = module_edit.map_qnames_to_edits()
    patcher = DocSigPatcher(edits_by_qual)
    new_code = cst.parse_module(old_code).visit(patcher).code
    return new_code
