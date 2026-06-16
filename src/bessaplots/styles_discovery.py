#                                                                       Modules
# =============================================================================

# Standard
import os

# Third-party
import matplotlib.pyplot as plt

# Local

#                                                        Authorship and Credits
# =============================================================================
__author__ = "John D. Garrett"
__credits__ = ["John D. Garrett"]
__status__ = "Stable"
#
# =============================================================================


def read_styles_in_folders(root_path):
    """
    Reads all stylesheets in the given path and its subfolders.

    Parameters
    ----------
    root_path : str
        Path to the root folder containing the stylesheets and other subfolders
        with stylesheets.

    Returns
    -------
    stylesheets : dict
        Dictionary of stylesheets in the form of {style_name: rcParams}.
        Should be compatible with matplotlib's plt.style.library dictionary.
    """
    # matplotlib >= 3.11 promoted `read_style_directory` to the public
    # `matplotlib.style` namespace and dropped the `matplotlib.style.core`
    # submodule; <= 3.10 only exposes it under `.core`. Prefer the public
    # name and fall back to `.core` for older matplotlib.
    read_style_directory = (
        getattr(plt.style, "read_style_directory", None)
        or plt.style.core.read_style_directory
    )

    stylesheets = {}  # plt.style.library is a dictionary
    for folder, _, _ in os.walk(root_path):
        new_stylesheets = read_style_directory(folder)
        stylesheets.update(new_stylesheets)
    return stylesheets
