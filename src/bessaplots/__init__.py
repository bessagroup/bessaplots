"""
Bessa Plots - Plottting utilities for scientific papers within the Bessa Group
"""

#                                                                       Modules
# =============================================================================

# Standard
import os

# Third-party
import matplotlib.pyplot as plt

# Local
import bessaplots

from .save_figure import FigureGrid, FigureSaver, savefig, set_size
from .styles_discovery import read_styles_in_folders
from .typst_report import TypstReport

#                                                        Authorship and Credits
# =============================================================================
__author__ = "John D. Garrett"
__credits__ = ["John D. Garrett"]
__status__ = "Stable"
#
# =============================================================================


# register the bundled stylesheets in the matplotlib style library
bessaplots_path = bessaplots.__path__[0]
styles_path = os.path.join(bessaplots_path, "styles")

# Reads styles in /styles folder and all subfolders
stylesheets = read_styles_in_folders(styles_path)

# matplotlib >= 3.11 promoted these style helpers to the public
# `matplotlib.style` namespace and dropped the `matplotlib.style.core`
# submodule; <= 3.10 only exposes them under `.core`. Prefer the public
# name and fall back to `.core` for older matplotlib.
_update_nested_dict = (
    getattr(plt.style, "update_nested_dict", None)
    or plt.style.core.update_nested_dict
)

# Update dictionary of styles - plt.style.library
_update_nested_dict(plt.style.library, stylesheets)
# Update `plt.style.available`, copy-paste from:
# https://github.com/matplotlib/matplotlib/blob/a170539a421623bb2967a45a24bb7926e2feb542/lib/matplotlib/style/core.py#L266  # noqa: E501
plt.style.available[:] = sorted(plt.style.library.keys())

__all__ = [
    "FigureGrid",
    "FigureSaver",
    "save_figure",
    "set_size",
    "TypstReport",
]
