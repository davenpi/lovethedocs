"""
Build per file prompts for the LLM.
"""

import libcst as cst


# TODO: Check on node types in the visitor methods (lovethedocs suggested them).
class ObjCollector(cst.CSTVisitor):
    """
    Collect qualified names of classes and functions in a LibCST module.

    This CSTVisitor traverses a LibCST module, recording the qualified names of all
    classes and functions encountered. It maintains a stack to track nesting and builds
    fully qualified names for each object.
    """

    def __init__(self) -> None:
        """
        Initialize the ObjCollector with an empty stack and qualnames list.

        Initializes the stack for tracking nested object names and the qualnames list
        for storing fully qualified names of classes and functions encountered during
        traversal.
        """
        self.stack = []  # keeps current qualname parts
        self.qualnames = []

    def _push(self, name: str) -> None:
        """
        Push a name onto the stack and record its qualified name.

        Appends the given name to the stack, constructs the current qualified name, and
        adds it to the qualnames list.

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

        Pushes the function name onto the stack and records its qualified name when a
        FunctionDef node is visited.

        Parameters
        ----------
        node : cst.FunctionDef
            The function definition node being visited.
        """
        self._push(node.name.value)

    def visit_ClassDef(self, node):
        """
        Visit a class definition node and record its qualified name.

        Pushes the class name onto the stack and records its qualified name when a ClassDef
        node is visited.

        Parameters
        ----------
        node : cst.ClassDef
            The class definition node being visited.
        """
        self._push(node.name.value)

    def leave_FunctionDef(self, node):
        """
        Pop the last function name from the stack after leaving its definition.

        Removes the most recent function name from the stack when leaving a FunctionDef
        node.

        Parameters
        ----------
        node : cst.FunctionDef
            The function definition node being left.
        """
        self.stack.pop()

    def leave_ClassDef(self, node):
        """
        Pop the last class name from the stack after leaving its definition.

        Removes the most recent class name from the stack when leaving a ClassDef node.

        Parameters
        ----------
        node : cst.ClassDef
            The class definition node being left.
        """
        self.stack.pop()


def build_prompts(modules: dict[str, str]) -> dict:
    """
    Build prompts for each module, listing qualified object names and source code.

    The function iterates over the provided modules, collects all qualified object
    names (classes and functions) using ObjCollector, and constructs a prompt for each
    module that includes the object list and the module's source code between BEGIN/END
    markers.

    Parameters
    ----------
    modules : dict[str, str]
        A dictionary mapping relative file paths to their corresponding source code as
        strings.

    Returns
    -------
    prompts : dict[str, str]
        A dictionary mapping module names to their generated prompts, each containing a
        list of qualified object names and the module's source code.
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
