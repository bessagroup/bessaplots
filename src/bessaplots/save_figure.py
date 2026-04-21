#                                                                       Modules
# =============================================================================

# Standard
import logging
from dataclasses import dataclass
from pathlib import Path

# Third-party
import matplotlib.pyplot as plt

# Local
from .constants import PAPER_SIZES

#                                                        Authorship and Credits
# =============================================================================
__author__ = "John D. Garrett"
__credits__ = ["John D. Garrett"]
__status__ = "Stable"
#
# =============================================================================

logger = logging.getLogger(__name__)


def set_size(
    fig: plt.Figure,
    n_side_by_side=1,
    span_columns=False,
    height: float = 0.8,
    paper_size: str = "letter",
    subplot_adjust: dict | None = None,
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
    paper_size : str, optional
        The paper size ("letter", "a4", "b5"). The default is "letter".
    subplot_adjust : dict, optional
        Optional dictionary of subplot adjustments to pass to
        `fig.subplots_adjust()`.

    Returns
    -------
    fig : plt.Figure
        The matplotlib figure object with the new size.
    """

    try:
        sizes = PAPER_SIZES[paper_size.lower()]
    except KeyError:
        raise ValueError(
            f"Unknown paper size '{paper_size}'. "
            f"Available sizes: {list(PAPER_SIZES.keys())}"
        ) from None

    total_width = (
        sizes["double_col_width"]
        if span_columns
        else sizes["single_col_width"]
    )

    # 2. Account for LaTeX margins/gutters between subfigures
    # We use a 2% "safety margin" so LaTeX doesn't force a line break
    available_fraction = 0.98 / n_side_by_side
    target_width = total_width * available_fraction

    # 3. Set Height (Golden ratio is standard, but 0.8 is great for ERTD)
    target_height = target_width * height

    # 4. Apply dimensions and force 8pt font
    fig.set_size_inches(target_width, target_height)
    if subplot_adjust is not None:
        fig.subplots_adjust(**subplot_adjust)

    return fig


#                                                           Helper Functions
# =============================================================================


class FigureSaver:
    SUPPORTED_FORMATS = ("pdf", "pgf")
    format: str = "pdf"

    @classmethod
    def set_format(cls, fmt: str) -> None:
        """Set the output format for store/load operations.

        Parameters
        ----------
        fmt : str
            File format. Must be one of ``"pdf"`` or ``"pgf"``.

        Raises
        ------
        ValueError
            If *fmt* is not a supported format.
        """
        fmt = fmt.lower()
        if fmt not in cls.SUPPORTED_FORMATS:
            raise ValueError(
                f"Unsupported format '{fmt}'. "
                f"Supported formats: {cls.SUPPORTED_FORMATS}"
            )
        cls.format = fmt

    @staticmethod
    def load(path: str) -> plt.Figure:
        """Load a figure from a file."""
        _path = Path(path).with_suffix(f".{FigureSaver.format}")
        return plt.imread(_path)

    @staticmethod
    def store(object: plt.Figure, path: str) -> str:
        """Store a figure at its exact ``set_size_inches`` dimensions.

        Passes the figure's full bbox explicitly so a
        ``savefig.bbox : tight`` rcParam in the active style cannot
        crop the output to content-dependent dimensions.
        """
        fmt = FigureSaver.format
        _path = Path(path)
        object.savefig(
            _path.with_suffix(f".{fmt}"),
            format=fmt,
            bbox_inches=object.bbox_inches,
            pad_inches=0.01,
            transparent=True,
            dpi=300,
        )
        return str(_path)


_FRAME_PAD = 0.005  # inches (~0.4 pt); prevents axes frame clipping


@dataclass
class FigureGrid:
    """Size and save figures for a grid layout with shared axes.

    Computes figure dimensions so that every cell in the grid has an
    identical axes (plot area) size.  When ``sharey=True`` the first
    column is wider (it retains the y-axis label and tick labels) and
    the remaining columns are narrower.  When ``sharex=True`` the
    bottom row is taller (it retains the x-axis label and tick labels)
    and the upper rows are shorter.

    The ``gutter`` parameter controls the visible gap between adjacent
    figures.  This space lives *outside* the figures and should be
    distributed by ``\\hfill`` in the LaTeX subfigure environment.

    Attributes
    ----------
    n_figures : int
        Number of figures per row (columns in the grid, must be >= 1).
    paper_size : str
        Paper size key from ``PAPER_SIZES``.
    span_columns : bool
        ``True`` for full-page width, ``False`` for single column.
    height : float
        Axes height as a fraction of axes width (aspect ratio).
    sharey : bool
        Share the y-axis: only the first column keeps its y-axis
        label and tick labels.
    sharex : bool
        Share the x-axis: only the bottom row keeps its x-axis
        label and tick labels.
    ylabel_margin : float
        Extra width (inches) reserved for the y-axis label and tick
        labels on the first column (only used when ``sharey=True``).
        Must be ``>= xtick_overhang`` — the first column's left edge
        relies on ``ylabel_margin`` to also cover the first x-tick
        label's overhang.
    xlabel_margin : float
        Extra height (inches) reserved for the x-axis label and tick
        labels on the bottom row (only used when ``sharex=True``).
    gutter : float
        Visible gap (inches) between adjacent figures.  Distributed
        by ``\\hfill`` in LaTeX.
    bottom_pad : float
        Bottom margin (inches) including x-axis tick labels and
        label.
    top_pad : float
        Top margin (inches) above the axes.
    xtick_overhang : float
        Horizontal padding (inches) reserved inside the figure on
        either side of the axes so the first and last x-tick labels
        — which are centered on their ticks and extend past the
        axes frame — are not cropped by the saved bounding box.
        Applied to the right edge of every column and the left edge
        of every non-first column; the first column's left edge is
        already covered by ``ylabel_margin``.
    """

    n_figures: int
    paper_size: str = "letter"
    span_columns: bool = False
    height: float = 0.8
    sharey: bool = True
    sharex: bool = False
    ylabel_margin: float = 0.45
    xlabel_margin: float = 0.33
    gutter: float = 0.06
    bottom_pad: float = 0.38
    top_pad: float = 0.05
    xtick_overhang: float = 0.1

    def __post_init__(self) -> None:
        if self.n_figures < 1:
            raise ValueError("n_figures must be >= 1")

        if self.xtick_overhang < 0:
            raise ValueError("xtick_overhang must be >= 0")

        if self.sharey and self.ylabel_margin < self.xtick_overhang:
            raise ValueError(
                f'ylabel_margin ({self.ylabel_margin}") must be '
                f'>= xtick_overhang ({self.xtick_overhang}") '
                f"when sharey=True"
            )

        try:
            sizes = PAPER_SIZES[self.paper_size.lower()]
        except KeyError:
            raise ValueError(
                f"Unknown paper size '{self.paper_size}'. "
                f"Available sizes: {list(PAPER_SIZES.keys())}"
            ) from None

        self.paper_size = self.paper_size.lower()

        col_key = (
            "double_col_width" if self.span_columns else "single_col_width"
        )
        self._total_textwidth: float = sizes[col_key]

        # Gutter space lives outside the figures (LaTeX \hfill)
        n_gutters = self.n_figures - 1
        W = self._total_textwidth - n_gutters * self.gutter

        # -- widths --------------------------------------------------

        # On the first column, ylabel_margin covers both the y-axis
        # label/tick labels *and* the first x-tick label's overhang,
        # so the "extra" width the first column gets over the rest
        # is ylabel_margin - xtick_overhang.  This keeps axes widths
        # identical across columns while preserving the textwidth
        # invariant.
        if self.sharey and self.n_figures > 1:
            effective_ylabel = self.ylabel_margin - self.xtick_overhang
            self._rest_width = (W - effective_ylabel) / self.n_figures
            self._first_width = self._rest_width + effective_ylabel
        else:
            self._first_width = W / self.n_figures
            self._rest_width = self._first_width

        if self._rest_width <= 0:
            raise ValueError(
                f'ylabel_margin ({self.ylabel_margin}") is too large '
                f'for {self.n_figures} figures in {W:.2f}" total width'
            )

        self._axes_width = self._rest_width - 2 * (
            _FRAME_PAD + self.xtick_overhang
        )
        if self._axes_width <= 0:
            raise ValueError(
                "Computed axes width is non-positive; "
                "reduce margins, ylabel_margin, or xtick_overhang"
            )

        # -- heights -------------------------------------------------

        if self.sharex and self.xlabel_margin > self.bottom_pad:
            raise ValueError(
                f'xlabel_margin ({self.xlabel_margin}") exceeds '
                f'bottom_pad ({self.bottom_pad}")'
            )

        axes_height = self._axes_width * self.height
        self._fig_height = self.top_pad + axes_height + self.bottom_pad

        if self.sharex:
            self._inner_row_height = (
                self.top_pad
                + axes_height
                + (self.bottom_pad - self.xlabel_margin)
            )
        else:
            self._inner_row_height = self._fig_height

    # -- read-only properties ----------------------------------------

    @property
    def first_width(self) -> float:
        """Figure width (inches) for the first column."""
        return self._first_width

    @property
    def rest_width(self) -> float:
        """Figure width (inches) for non-first columns."""
        return self._rest_width

    @property
    def axes_width(self) -> float:
        """Axes (plot area) width (inches), identical for all."""
        return self._axes_width

    @property
    def fig_height(self) -> float:
        """Figure height (inches) for the bottom row."""
        return self._fig_height

    @property
    def inner_row_height(self) -> float:
        """Figure height (inches) for non-bottom rows.

        Equal to :attr:`fig_height` when ``sharex=False``.
        """
        return self._inner_row_height

    @property
    def textwidth_fractions(self) -> list[float]:
        r"""Figure widths as fractions of ``\textwidth``.

        Returns a list of length *n_figures*.  When ``sharey=True``
        the first entry is larger than the rest.  The remaining
        fraction is gutter space distributed by ``\hfill`` in LaTeX.
        """
        return [
            (self._first_width if i == 0 else self._rest_width)
            / self._total_textwidth
            for i in range(self.n_figures)
        ]

    # -- public methods ----------------------------------------------

    def apply(
        self,
        fig: plt.Figure,
        first_column: bool = True,
        last_row: bool = True,
    ) -> plt.Figure:
        """Apply grid sizing to *fig*.

        Sets figure dimensions and ``subplots_adjust`` margins so that
        the axes occupies the same absolute rectangle in every figure.
        Strips y-axis decorations when ``sharey=True`` and
        *first_column* is ``False``; strips x-axis decorations when
        ``sharex=True`` and *last_row* is ``False``.

        Parameters
        ----------
        fig : plt.Figure
            The matplotlib figure to resize.
        first_column : bool
            ``True`` for the leftmost figure in a row (keeps y-axis
            when ``sharey`` is enabled).
        last_row : bool
            ``True`` for figures in the bottom row (keeps x-axis
            when ``sharex`` is enabled).

        Returns
        -------
        plt.Figure
            The same figure, mutated in place.
        """
        w = self._first_width if first_column else self._rest_width
        h = self._fig_height if last_row else self._inner_row_height

        fig.set_size_inches(w, h)

        # Left margin: first column's left side is covered by
        # ylabel_margin; every other left side needs xtick_overhang.
        if self.sharey and first_column:
            left_frac = (self.ylabel_margin + _FRAME_PAD) / w
        else:
            left_frac = (_FRAME_PAD + self.xtick_overhang) / w

        # Bottom margin
        if self.sharex and not last_row:
            bottom_frac = (self.bottom_pad - self.xlabel_margin) / h
        else:
            bottom_frac = self.bottom_pad / h

        fig.subplots_adjust(
            left=left_frac,
            right=1.0 - (_FRAME_PAD + self.xtick_overhang) / w,
            bottom=bottom_frac,
            top=1.0 - self.top_pad / h,
        )

        # Strip y-axis on non-first columns
        if self.sharey and not first_column:
            for ax in fig.get_axes():
                ax.set_ylabel("")
                ax.tick_params(axis="y", labelleft=False)

        # Strip x-axis on non-bottom rows
        if self.sharex and not last_row:
            for ax in fig.get_axes():
                ax.set_xlabel("")
                ax.tick_params(axis="x", labelbottom=False)

        return fig

    def save(
        self,
        fig: plt.Figure,
        path: str,
        first_column: bool = True,
        last_row: bool = True,
        format: str = "pgf",
    ) -> None:
        """Apply sizing and save with deterministic bounding box.

        Calls :meth:`apply` then saves with ``bbox_inches`` set to
        the figure's full bbox so the output file has the exact
        computed dimensions.  The explicit bbox is required (rather
        than ``None``) because matplotlib maps
        ``bbox_inches=None`` to the ``savefig.bbox`` rcParam, which
        some styles set to ``"tight"`` — that would crop the output
        to content-dependent dimensions and break grid alignment.

        Parameters
        ----------
        fig : plt.Figure
            Figure to save.
        path : str
            Output path (extension replaced by *format*).
        first_column : bool
            ``True`` for the leftmost figure in a row.
        last_row : bool
            ``True`` for figures in the bottom row.
        format : str
            Output format (default ``"pgf"``).
        """
        self.apply(fig, first_column=first_column, last_row=last_row)
        _path = Path(path).with_suffix(f".{format}")
        fig.savefig(
            _path,
            format=format,
            bbox_inches=fig.bbox_inches,
            pad_inches=0.0,
            transparent=True,
        )
        logger.info(f"Saved figure: {_path}")


def savefig(
    fig: plt.Figure,
    path: str,
    n_side_by_side=1,
    span_columns=False,
    height=0.8,
    paper_size: str = "letter",
    format: str = "pdf",
) -> None:
    """
    Saves a figure scaled exactly for an IEEE subfigure slot.

    Parameters
    ----------
    fig : plt.Figure
        The matplotlib figure object.
    path : str
        The storage location (including file name) for the figure.
        The .pdf suffix is added automatically.
    n_side_by_side : int, optional
        How many figures will sit horizontally (1, 2, or 3).
        The default is 1.
    span_columns : bool, optional
        False for single column (3.48"), True for full page (7.14").
        The default is False.
    height : float, optional
        The height of the figure as a fraction of the width.
        The default is 0.8.
    paper_size : str, optional
        The paper size ("letter", "a4", "b5"). The default is "letter".
    format : str, optional
        The file format to save (e.g., "pdf", "png"). The default is "pdf".
    """

    fig = set_size(
        fig,
        n_side_by_side=n_side_by_side,
        span_columns=span_columns,
        height=height,
        paper_size=paper_size,
    )

    _path = Path(path).with_suffix(f".{format}")

    # 5. Save with tight bounding box
    # pad_inches is tiny to ensure the figure maximizes the LaTeX slot
    fig.savefig(
        _path,
        format=format,
        bbox_inches="tight",
        pad_inches=0.01,
        transparent=True,
    )
    logger.info(f"Saved figure: {_path}")
