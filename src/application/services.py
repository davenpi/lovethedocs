import libcst as cst

from src.domain.models import ModuleEdit
from src.application.transformers import DocSigPatcher


def update_module_docs(
    old_module,
    module_edit: ModuleEdit,
    patcher_cls: type[DocSigPatcher] = DocSigPatcher,
):
    edits_by_qname = module_edit.map_qnames_to_edits()
    patcher = patcher_cls(edits_by_qname)
    updated_code = cst.parse_module(old_module).visit(patcher).code
    return updated_code
