#                                                                       Modules
# =============================================================================

# Standard
import logging
from pathlib import Path

# Third-party
import matplotlib.pyplot as plt

# Local
from .constants import DOUBLE_COL_WIDTH, SINGLE_COL_WIDTH

#                                                        Authorship and Credits
# =============================================================================
__author__ = "John D. Garrett"
__credits__ = ["John D. Garrett"]
__status__ = "Stable"
#
# =============================================================================

logger = logging.getLogger(__name__)


def set_size(
    fig: plt.Figure, n_side_by_side=1, span_columns=False, height: float = 0.8
) -> plt.Figure:
    """
    Set figure size to fit in IEEE column layout.

    Parameters
    ----------
    fig : plt.Figure
        The matplotlib figure object.
    n_side_by_side : int, optional
        How many figures will sit horizontally (1, 2, or 3). The default is 1.
    span_columns : bool, optional
        False for single column (3.48"), True for full page (7.14").
        The default is False.
    height : float, optional
        The height of the figure as a fraction of the width.
        The default is 0.8.

    Returns
    -------
    fig : plt.Figure
        The matplotlib figure object with the new size.
    """

    total_width = DOUBLE_COL_WIDTH if span_columns else SINGLE_COL_WIDTH

    # 2. Account for LaTeX margins/gutters between subfigures
    # We use a 2% "safety margin" so LaTeX doesn't force a line break
    available_fraction = 0.98 / n_side_by_side
    target_width = total_width * available_fraction

    # 3. Set Height (Golden ratio is standard, but 0.8 is great for ERTD)
    target_height = target_width * height

    # 4. Apply dimensions and force 8pt font
    fig.set_size_inches(target_width, target_height)
    return fig


#                                                           Helper Functions
# =============================================================================


class FigureSaver:
    @staticmethod
    def load(path: str) -> plt.Figure:
        """Load a figure from a file."""
        _path = Path(path).with_suffix(".pdf")
        return plt.imread(_path)

    @staticmethod
    def store(object: plt.Figure, path: str) -> str:
        _path = Path(path)
        """Store a figure to a file."""
        object.savefig(
            _path.with_suffix(".pdf"),
            format="pdf",
            bbox_inches="tight",
            pad_inches=0.01,
            transparent=True,
            dpi=300,
        )
        return str(_path)


def savefig(
    fig: plt.Figure,
    name: str,
    n_side_by_side=1,
    span_columns=False,
    height=0.8,
) -> None:
    """
    Saves a figure scaled exactly for an IEEE subfigure slot.

    Parameters
    ----------
    fig : plt.Figure
        The matplotlib figure object.
        name : str
        The name of the figure.
    n_side_by_side : int, optional
        How many figures will sit horizontally (1, 2, or 3).
        The default is 1.
    span_columns : bool, optional
        False for single column (3.48"), True for full page (7.14").
        The default is False.
    height : float, optional
        The height of the figure as a fraction of the width.
        The default is 0.8.
    """

    fig = set_size(
        fig,
        n_side_by_side=n_side_by_side,
        span_columns=span_columns,
        height=height,
    )

    # 5. Save with tight bounding box
    # pad_inches is tiny to ensure the figure maximizes the LaTeX slot
    fig.savefig(
        f"{name}.pdf",
        format="pdf",
        bbox_inches="tight",
        pad_inches=0.01,
        transparent=True,
    )
    logger.info(f"Saved figure: {name}.pdf")
