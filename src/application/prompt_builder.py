"""
Build per file prompts for the LLM.
"""

import libcst as cst


# TODO: Check on node types in the visitor methods (lovethedocs suggested them).
class ObjCollector(cst.CSTVisitor):
    """
    Collects qualified names of classes and functions in a CST module.

    This visitor traverses a LibCST module and records the qualified names of all
    classes and functions encountered, maintaining a stack to track nesting.
    """

    def __init__(self) -> None:
        """Initialize the ObjCollector with empty stack and qualnames list."""
        self.stack = []  # keeps current qualname parts
        self.qualnames = []

    def _push(self, name: str) -> None:
        """
        Push a name onto the stack and record its qualified name.

        Parameters
        ----------
        name : str
            The name of the class or function to add to the current qualified name
            stack.
        """
        self.stack.append(name)
        qualname = ".".join(self.stack)
        self.qualnames.append(qualname)
        return

    # ---- nodes ----
    def visit_FunctionDef(self, node):
        """
        Visit a function definition node and record its qualified name.

        Parameters
        ----------
        node : cst.FunctionDef
            The function definition node being visited.
        """
        self._push(node.name.value)

    def visit_ClassDef(self, node):
        """
        Visit a class definition node and record its qualified name.

        Parameters
        ----------
        node : cst.ClassDef
            The class definition node being visited.
        """
        self._push(node.name.value)

    def leave_FunctionDef(self, node):
        """
        Pop the last function name from the stack after leaving its definition.

        Parameters
        ----------
        node : cst.FunctionDef
            The function definition node being left.
        """
        self.stack.pop()

    def leave_ClassDef(self, node):
        """
        Pop the last class name from the stack after leaving its definition.

        Parameters
        ----------
        node : cst.ClassDef
            The class definition node being left.
        """
        self.stack.pop()


def build_prompts(modules: dict[str, str]) -> dict:
    """
    Build prompts for each module in the input dictionary.

    The function generates a prompt for each module, listing all qualified object names
    and including the module's source code between BEGIN/END markers.

    Parameters
    ----------
    modules : dict[str, str]
        A dictionary mapping relative file paths to their corresponding source code as
        strings.

    Returns
    -------
    - prompts : dict[str, str]
        A dictionary mapping module names to their generated prompts.
    """
    prompts = {}
    for path, source in modules.items():
        tree = cst.parse_module(source)
        wrapper = cst.metadata.MetadataWrapper(tree)
        collector = ObjCollector()
        wrapper.visit(collector)

        header = (
            "### Objects in this file:\n"
            + "\n".join(f"  {qn}" for qn in collector.qualnames)
            + "\n\n"
        )
        prompts[path] = header + f"BEGIN {path}\n{source.strip()}\nEND {path}"
    return prompts
