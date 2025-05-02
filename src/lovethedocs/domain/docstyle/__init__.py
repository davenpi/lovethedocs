# In src/domain/docstyle/__init__.py
from .base import DocStyle
from .numpy_style import NumPyDocStyle

# Make commonly used styles available directly from the package
__all__ = ["DocStyle", "NumPyDocStyle"]
