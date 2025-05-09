from .base import DocStyle
from .google_style import GoogleDocStyle
from .numpy_style import NumPyDocStyle

# Make commonly used styles available directly from the package
__all__ = ["DocStyle", "NumPyDocStyle", "GoogleDocStyle"]
