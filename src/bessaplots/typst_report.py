#                                                                       Modules
# =============================================================================

# Standard
import datetime
import logging
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

# Local
from .constants import PAPER_SIZES

#                                                        Authorship and Credits
# =============================================================================
__author__ = "Martin van der Schelling"
__credits__ = ["Martin van der Schelling"]
__status__ = "Stable"
#
# =============================================================================

logger = logging.getLogger(__name__)

_TYPST_PAPER_NAMES: dict[str, str] = {
    "letter": "us-letter",
    "a4": "a4",
    "b5": "iso-b5",
}


# ---------------------------------------------------------------------------
# Private helpers (pure functions, no class dependency)
# ---------------------------------------------------------------------------


def _preamble(paper_size: str) -> str:
    """Return the Typst ``#set`` directives for page, text, and paragraph.

    Parameters
    ----------
    paper_size : str
        Key into ``_TYPST_PAPER_NAMES`` (e.g. ``"a4"``, ``"letter"``).

    Returns
    -------
    str
        Multi-line string of Typst ``#set`` directives.
    """
    paper = _TYPST_PAPER_NAMES[paper_size]
    return (
        f'#set page(paper: "{paper}",'
        f" margin: (x: 25mm, y: 25mm))\n"
        '#set text(font: "New Computer Modern", size: 10pt)\n'
        "#set par(justify: true)"
    )


def _title_block(title: str, author: str, date: str) -> str:
    """Return a centred Typst block with the title, author, and date.

    Lines for *author* and *date* are omitted when the corresponding
    argument is falsy (empty string or ``None``).

    Parameters
    ----------
    title : str
        Report title rendered in bold 16 pt.
    author : str
        Author name rendered in 11 pt.  Omitted when empty.
    date : str
        Date string rendered in italic 10 pt.  Omitted when empty.

    Returns
    -------
    str
        Typst ``#align(center)[...]`` block.
    """
    lines = [
        "#align(center)[",
        f'  #text(size: 16pt, weight: "bold")[{title}]',
    ]
    if author:
        lines.append("  #v(4pt)")
        lines.append(f"  #text(size: 11pt)[{author}]")
    if date:
        lines.append("  #v(2pt)")
        lines.append(f'  #text(size: 10pt, style: "italic")[{date}]')
    lines.append("]")
    return "\n".join(lines)


def _figure_block(
    paths: list[str | Path],
    columns: int | list[str],
    caption: str | None,
    gutter: str,
) -> str:
    """Return a Typst grid of images, optionally wrapped in a figure.

    When *caption* is ``None`` the images are placed in a bare
    ``#grid`` block.  When a caption is provided the grid is wrapped
    in a ``#figure`` block with automatic numbering.

    Parameters
    ----------
    paths : list of str or Path
        Paths to image files.  Each path is resolved to an absolute
        POSIX path.
    columns : int or list of str
        Number of equal-width columns (``int``) or explicit Typst
        column-width strings (e.g. ``["1fr", "2fr"]``).
    caption : str or None
        Figure caption.  ``None`` produces a bare grid.
    gutter : str
        Typst ``column-gutter`` value (e.g. ``"1em"``).

    Returns
    -------
    str
        Typst markup for the grid or figure block.
    """
    cols_str = (
        str(columns)
        if isinstance(columns, int)
        else "(" + ", ".join(columns) + ")"
    )
    image_lines = [
        f'  image("{Path(p).resolve().as_posix()}"),' for p in paths
    ]
    images = "\n".join(image_lines)

    if caption is None:
        return (
            f"#grid(\n"
            f"  columns: {cols_str},\n"
            f"  column-gutter: {gutter},\n"
            f"{images}\n"
            f")"
        )
    else:
        return (
            f"#figure(\n"
            f"  grid(\n"
            f"    columns: {cols_str},\n"
            f"    column-gutter: {gutter},\n"
            + "\n".join(f"    {line.strip()}" for line in image_lines)
            + f"\n  ),\n"
            f"  caption: [{caption}],\n"
            f")"
        )


def _render(
    blocks: list[str],
    title: str,
    author: str,
    date: str,
    paper_size: str,
) -> str:
    """Assemble the full Typst source string from report components.

    Combines the preamble, an optional title block, and all content
    blocks into a single Typst source document.

    Parameters
    ----------
    blocks : list of str
        Content blocks (paragraphs, figure grids) in insertion order.
    title : str
        Report title.  Empty string omits the title block.
    author : str
        Author name for the title block.
    date : str
        Date string for the title block.
    paper_size : str
        Paper size key (e.g. ``"a4"``, ``"letter"``).

    Returns
    -------
    str
        Complete Typst source document ending with a newline.
    """
    parts: list[str] = [_preamble(paper_size)]
    if title:
        parts.append(_title_block(title, author, date))
        parts.append("#v(1em)")
    if blocks:
        parts.append("\n\n".join(blocks))
    return "\n\n".join(parts) + "\n"


@dataclass
class TypstReport:
    """
    Builder for Typst-based PDF reports.

    Accumulates paragraphs and figure grids, then renders them to a
    ``.typ`` source file and optionally compiles to PDF via the
    ``typst`` CLI.

    Parameters
    ----------
    title : str, optional
        Report title. Empty string omits the title block entirely.
        The default is ``""``.
    author : str, optional
        Author name shown below the title. Ignored when title is empty.
        The default is ``""``.
    date : str or None, optional
        Date string shown below the author.  ``None`` uses today's ISO
        date; ``""`` omits the date line.  The default is ``None``.
    paper_size : str, optional
        One of ``"letter"``, ``"a4"``, or ``"b5"``.
        The default is ``"a4"``.

    Examples
    --------
    >>> from bessaplots import TypstReport
    >>> r = TypstReport(title="My Report", author="J. Doe")
    >>> r.add_paragraph("Introduction.")
    >>> r.add_figures(["fig1.pdf", "fig2.pdf"], columns=2)
    >>> r.save("report")  # writes report.typ + compiles report.pdf
    """

    title: str = ""
    author: str = ""
    date: str | None = None
    paper_size: str = "a4"
    _blocks: list[str] = field(default_factory=list, init=False, repr=False)

    def __post_init__(self) -> None:
        """Validate *paper_size* and default *date* to today's ISO date.

        Raises
        ------
        ValueError
            If *paper_size* is not a recognised size in
            ``PAPER_SIZES``.
        """
        try:
            _ = PAPER_SIZES[self.paper_size.lower()]
        except KeyError:
            raise ValueError(
                f"Unknown paper size '{self.paper_size}'. "
                f"Available sizes: {list(PAPER_SIZES.keys())}"
            ) from None

        self.paper_size = self.paper_size.lower()
        if self.date is None:
            self.date = datetime.date.today().isoformat()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def add_paragraph(self, text: str) -> None:
        """
        Add a paragraph of text to the report.

        Parameters
        ----------
        text : str
            Plain text or Typst markup passed through verbatim.
            Special Typst characters (``#``, ``[``, ``]``) are not
            escaped; advanced users may include Typst markup directly.
        """
        self._blocks.append(text)

    def add_figures(
        self,
        paths: list[str | Path],
        columns: int | list[str] = 1,
        caption: str | None = None,
        gutter: str = "1em",
    ) -> None:
        """
        Add a grid of figures to the report.

        Parameters
        ----------
        paths : list of str or Path
            Paths to the figure files (e.g. PDF or PNG).  Each path is
            resolved to an absolute POSIX path so the generated ``.typ``
            file works regardless of where it is written.
        columns : int or list of str, optional
            Number of equal-width columns (``int``) or explicit Typst
            column-width strings such as ``["1fr", "2fr"]``.
            The default is ``1``.
        caption : str or None, optional
            When provided, wraps the grid in a Typst ``figure`` block
            with this caption, enabling automatic figure numbering.
            The default is ``None`` (no caption, no figure numbering).
        gutter : str, optional
            Typst ``column-gutter`` value (e.g. ``"1em"``, ``"5mm"``).
            The default is ``"1em"``.

        Raises
        ------
        ValueError
            If ``paths`` is empty or ``columns`` is an integer <= 0.
        """
        if not paths:
            raise ValueError("paths must be non-empty")
        if isinstance(columns, int) and columns <= 0:
            raise ValueError("columns must be a positive integer")
        if isinstance(columns, list) and len(columns) == 0:
            raise ValueError("columns list must be non-empty")

        self._blocks.append(_figure_block(paths, columns, caption, gutter))

    def write(self, path: str | Path) -> Path:
        """
        Write the ``.typ`` source file.

        Parameters
        ----------
        path : str or Path
            Destination path.  The ``.typ`` extension is enforced
            regardless of what suffix is provided.

        Returns
        -------
        Path
            Absolute path to the written ``.typ`` file.
        """
        resolved = Path(path).with_suffix(".typ")
        resolved.write_text(
            _render(
                self._blocks,
                self.title,
                self.author,
                self.date,
                self.paper_size,
            ),
            encoding="utf-8",
        )
        logger.info(f"Wrote Typst source: {resolved}")
        return resolved

    def compile(
        self,
        typ_path: str | Path,
        pdf_path: str | Path | None = None,
    ) -> Path:
        """
        Compile a ``.typ`` file to PDF using the ``typst`` CLI.

        Parameters
        ----------
        typ_path : str or Path
            Path to the ``.typ`` source file.
        pdf_path : str or Path or None, optional
            Output PDF path.  ``None`` replaces the ``.typ`` suffix with
            ``.pdf``.  The default is ``None``.

        Returns
        -------
        Path
            Path to the compiled PDF.

        Raises
        ------
        RuntimeError
            If the ``typst`` executable is not found or compilation
            fails.
        """
        typ = Path(typ_path).with_suffix(".typ")
        pdf = (
            typ.with_suffix(".pdf")
            if pdf_path is None
            else Path(pdf_path).with_suffix(".pdf")
        )
        try:
            result = subprocess.run(
                ["typst", "compile", str(typ), str(pdf)],
                capture_output=True,
                text=True,
            )
        except FileNotFoundError:
            raise RuntimeError(
                "typst CLI not found. Install via "
                "https://github.com/typst/typst#installation"
            ) from None

        if result.returncode != 0:
            raise RuntimeError(f"typst compile failed:\n{result.stderr}")
        if result.stderr:
            logger.warning(result.stderr)

        logger.info(f"Compiled PDF: {pdf}")
        return pdf

    def save(self, stem: str | Path) -> Path:
        """
        Write the ``.typ`` file and compile it to PDF.

        Parameters
        ----------
        stem : str or Path
            Base name (without extension) for the output files.
            Produces ``<stem>.typ`` and ``<stem>.pdf``.

        Returns
        -------
        Path
            Path to the compiled PDF.
        """
        stem = Path(stem)
        typ_path = self.write(stem.with_suffix(".typ"))
        return self.compile(typ_path)
