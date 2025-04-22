"""
Build per file prompts for the LLM.
"""

import libcst as cst


class ObjCollector(cst.CSTVisitor):

    def __init__(self):
        self.stack = []  # keeps current qualname parts
        self.result = []  # [(id, qualname)]
        self._counter = 1

    def _push(self, name: str):
        self.stack.append(name)
        qualname = ".".join(self.stack)
        obj_id = f"ID{self._counter:03d}"
        self._counter += 1
        self.result.append((obj_id, qualname))
        return obj_id

    # ---- nodes ----
    def visit_FunctionDef(self, node):
        self._push(node.name.value)

    def visit_ClassDef(self, node):
        self._push(node.name.value)

    def leave_FunctionDef(self, node):
        self.stack.pop()

    def leave_ClassDef(self, node):
        self.stack.pop()


def build_prompts(
    modules: dict[str, str],
) -> tuple[dict, dict]:
    """
    Return prompts and id maps for each module in *modules*.

    The input *modules* is a mapping of relative file paths to raw source strings
    produced by `infra.file_system.load_modules()`. Each prompt looks like::

        ### Objects in this file:
        ID001 qualname1
        ID002 qualname2
        ...

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
    tuple[dict, dict]
        - prompts : dict[str, str]
            A dictionary where the keys are the module names and the values are
              the corresponding prompts with BEGIN/END blocks.
        - id_maps : dict[str, dict[str, str]]
            A dictionary where the keys are the module names and the values are
              dictionaries mapping object IDs to their qualified names.
    """
    prompts, id_maps = {}, {}
    for path, source in modules.items():
        tree = cst.parse_module(source)
        wrapper = cst.metadata.MetadataWrapper(tree)
        collector = ObjCollector()
        wrapper.visit(collector)

        id_to_qn = dict(collector.result)
        id_maps[path] = id_to_qn

        header = (
            "### Objects in this file:\n"
            + "\n".join(f"  {obj_id:<6} {qn}" for obj_id, qn in collector.result)
            + "\n\n"
        )

        prompts[path] = (
            header + f"BEGIN {path}\n" + source.rstrip() + "\n" + f"END {path}"
        )
    return prompts, id_maps
