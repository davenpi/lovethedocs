import libcst as cst

from src.domain.models import ModuleEdit
from src.application.transformers import DocSigPatcher


def update_module_docs(
    old_module_source: str,
    module_edit: ModuleEdit,
    patcher_cls: type[DocSigPatcher] = DocSigPatcher,
) -> str:
    """
    Update the docstrings and signatures in module source code based on provided edits.

    Parses the given module source code, applies the specified docstring and signature
    edits using the provided patcher class, and returns the updated source code as a
    string.

    Parameters
    ----------
    old_module : str
        The source code of the module to update.
    module_edit : ModuleEdit
        An object containing the mapping of qualified names to their respective edits.
    patcher_cls : type[DocSigPatcher], optional
        The patcher class to use for applying edits. Defaults to DocSigPatcher.

    Returns
    -------
    updated_code : str
        The updated module source code with applied docstring and signature edits.
    """
    edits_by_qname = module_edit.map_qnames_to_edits()
    patcher = patcher_cls(edits_by_qname)
    updated_code = cst.parse_module(old_module_source).visit(patcher).code
    return updated_code
