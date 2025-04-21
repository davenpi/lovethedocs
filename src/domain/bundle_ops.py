# domain/bundle_ops.py
from typing import Dict, List


def _collect_docstrings(obj_list: List[dict]) -> List[str]:
    """Return all docstrings found in a list of function/method objects."""
    out: List[str] = []
    for obj in obj_list:
        if "docstring" in obj:
            out.append(obj["docstring"].strip())
    return out


def flatten(json_payload: dict) -> Dict[str, str]:
    """
    Convert a validated `code_documentation_edits` payload into
    { "pkg/module.py": "<placeholder updated source>", ... }.

    Phase-0 strategy:
      • take every new docstring we got for the module,
      • join them with blank lines,
      • use that block as the “updated” file content.
    """
    files: Dict[str, str] = {}

    for mod in json_payload.get("modules", []):
        path = mod["path"]  # e.g. "infra/openai_client.py"

        doc_parts: List[str] = []

        # module‑level docstring (optional in later schema versions)
        if "docstring" in mod:
            doc_parts.append(mod["docstring"].strip())

        # top‑level functions
        doc_parts.extend(_collect_docstrings(mod.get("functions", [])))

        # classes + their methods
        for cls in mod.get("classes", []):
            if "docstring" in cls:
                doc_parts.append(cls["docstring"].strip())
            doc_parts.extend(_collect_docstrings(cls.get("methods", [])))

        files[path] = "\n\n".join(doc_parts).strip() + "\n"

    return files
