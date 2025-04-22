"""
Build per file prompts for the LLM.
"""


def build_prompts(modules: dict[str, str]) -> dict[str, str]:
    """Return {relative_path: prompt} for every module in *modules*.

    The input *modules* is a mapping of relative file paths to raw source strings
    produced by `infra.file_system.load_modules()`. Each prompt looks like::

        BEGIN <relative_path>
        <source code unchanged>
        END <relative_path>

    Parameters
    ----------
    modules : dict[str, str]
        A dictionary where the keys are the module names and the values are their
        corresponding code as strings.

    Returns
    -------
    dict[str, str]
        A dictionary where the keys are the module names and the values are the
        corresponding prompts with BEGIN/END blocks.
    """
    prompts = {}
    for module_name, module_code in modules.items():
        prompts[module_name] = f"BEGIN {module_name}\n{module_code}\nEND {module_name}"
    return prompts
