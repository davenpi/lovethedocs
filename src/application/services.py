import libcst as cst

from src.domain.models import ModuleEdit
from src.application.transformers import DocSigPatcher


def update_module_docs(
    old_module_source: str,
    module_edit: ModuleEdit,
    patcher_cls: type[DocSigPatcher] = DocSigPatcher,
) -> str:
    """
    Update docstrings and signatures in module source code using provided edits.

    Parses the given module source code, applies docstring and signature edits as
    specified in the `module_edit` object using the given patcher class, and returns
    the updated source code as a string.

    Parameters
    ----------
    old_module_source : str
        The source code of the module to update.
    module_edit : ModuleEdit
        An object containing mappings of qualified names to their respective edits.
    patcher_cls : type[DocSigPatcher], optional
        The patcher class to use for applying edits. Defaults to DocSigPatcher.

    Returns
    -------
    str
        The updated module source code with applied docstring and signature edits.
    """
    edits_by_qname = module_edit.map_qnames_to_edits()
    patcher = patcher_cls(edits_by_qname)
    return cst.parse_module(old_module_source).visit(patcher).code
