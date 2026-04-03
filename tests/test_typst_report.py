#                                                                       Modules
# =============================================================================

# Standard
import subprocess
from pathlib import Path

# Third-party
import pytest

# Local
from bessaplots.typst_report import TypstReport, _render

#                                                        Authorship and Credits
# =============================================================================
__author__ = "Martin van der Schelling"
__credits__ = ["Martin van der Schelling"]
__status__ = "Stable"
#
# =============================================================================


# ---------------------------------------------------------------------------
# Helpers / fixtures
# ---------------------------------------------------------------------------


def render(report: TypstReport) -> str:
    """Convenience wrapper to call the module-level _render."""
    return _render(
        report._blocks,
        report.title,
        report.author,
        report.date,
        report.paper_size,
    )


@pytest.fixture
def report():
    """Minimal report used across many tests."""
    return TypstReport(title="T", author="A", date="2026-01-01")


# ---------------------------------------------------------------------------
# Group A — __init__ and _render (no I/O)
# ---------------------------------------------------------------------------


def test_render_contains_title(report):
    """Title string appears in rendered output."""
    assert "T" in render(report)


def test_render_contains_author(report):
    """Author string appears in rendered output."""
    assert "A" in render(report)


def test_render_contains_date(report):
    """Explicit date appears in rendered output."""
    assert "2026-01-01" in render(report)


def test_render_default_date_is_today():
    """
    None date defaults to today's ISO date in rendered output.
    """
    import datetime

    today = datetime.date.today().isoformat()
    r = TypstReport(title="X", date=None)
    assert today in render(r)


def test_render_empty_title_omits_align_block():
    """
    Empty title omits the #align center block from the output.
    """
    r = TypstReport(title="")
    rendered = render(r)
    assert "#align(center)" not in rendered


def test_render_empty_date_omits_date_line():
    """Empty date string omits the italic date line."""
    r = TypstReport(title="T", author="A", date="")
    rendered = render(r)
    assert "italic" not in rendered


@pytest.mark.parametrize(
    "paper_size, expected",
    [
        ("a4", '"a4"'),
        ("letter", '"us-letter"'),
        ("b5", '"iso-b5"'),
    ],
)
def test_render_paper_size_in_preamble(paper_size, expected):
    """Correct Typst paper name appears in the preamble."""
    r = TypstReport(paper_size=paper_size)
    assert expected in render(r)


def test_render_invalid_paper_size_raises():
    """Unknown paper size raises ValueError with descriptive message."""
    with pytest.raises(ValueError, match="Unknown paper size"):
        TypstReport(paper_size="a3")


# ---------------------------------------------------------------------------
# Group B — add_paragraph
# ---------------------------------------------------------------------------


def test_add_paragraph_appears_in_render(report):
    """Added paragraph text is present in rendered output."""
    report.add_paragraph("Hello world.")
    assert "Hello world." in render(report)


def test_add_multiple_paragraphs_ordering():
    """Multiple paragraphs appear in insertion order."""
    r = TypstReport()
    r.add_paragraph("First")
    r.add_paragraph("Second")
    rendered = render(r)
    assert rendered.index("First") < rendered.index("Second")


# ---------------------------------------------------------------------------
# Group C — add_figures
# ---------------------------------------------------------------------------


def test_add_figures_single_column(tmp_path, report):
    """
    Integer columns=1 produces 'columns: 1' in rendered output.
    """
    p = tmp_path / "fig.pdf"
    p.touch()
    report.add_figures([str(p)], columns=1)
    assert "columns: 1," in render(report)


def test_add_figures_multiple_columns(tmp_path, report):
    """Integer columns=2 produces 'columns: 2' in rendered output."""
    p = tmp_path / "fig.pdf"
    p.touch()
    report.add_figures([str(p)], columns=2)
    assert "columns: 2," in render(report)


def test_add_figures_fractional_columns(tmp_path, report):
    """
    List columns produces a Typst tuple expression in rendered output.
    """
    p = tmp_path / "fig.pdf"
    p.touch()
    report.add_figures([str(p)], columns=["1fr", "2fr"])
    assert "columns: (1fr, 2fr)," in render(report)


def test_add_figures_path_resolved(tmp_path, report):
    """Figure path is resolved to an absolute POSIX path."""
    p = tmp_path / "fig.pdf"
    p.touch()
    report.add_figures([str(p)])
    rendered = render(report)
    assert p.resolve().as_posix() in rendered


def test_add_figures_with_caption(tmp_path, report):
    """Caption wraps grid in a Typst #figure block."""
    p = tmp_path / "fig.pdf"
    p.touch()
    report.add_figures([str(p)], caption="My Caption")
    rendered = render(report)
    assert "#figure(" in rendered
    assert "caption: [My Caption]" in rendered


def test_add_figures_without_caption(tmp_path, report):
    """No caption produces a bare #grid block without #figure."""
    p = tmp_path / "fig.pdf"
    p.touch()
    report.add_figures([str(p)])
    rendered = render(report)
    assert "#grid(" in rendered
    assert "#figure(" not in rendered


def test_add_figures_custom_gutter(tmp_path, report):
    """Custom gutter value appears in column-gutter field."""
    p = tmp_path / "fig.pdf"
    p.touch()
    report.add_figures([str(p)], gutter="5mm")
    assert "column-gutter: 5mm," in render(report)


def test_add_figures_empty_paths_raises(report):
    """Empty paths list raises ValueError."""
    with pytest.raises(ValueError, match="paths must be non-empty"):
        report.add_figures([])


def test_add_figures_zero_columns_raises(tmp_path, report):
    """columns=0 raises ValueError."""
    p = tmp_path / "fig.pdf"
    p.touch()
    with pytest.raises(ValueError, match="columns must be a positive"):
        report.add_figures([str(p)], columns=0)


def test_add_figures_negative_columns_raises(tmp_path, report):
    """Negative columns raises ValueError."""
    p = tmp_path / "fig.pdf"
    p.touch()
    with pytest.raises(ValueError, match="columns must be a positive"):
        report.add_figures([str(p)], columns=-1)


def test_add_figures_empty_columns_list_raises(tmp_path, report):
    """Empty columns list raises ValueError."""
    p = tmp_path / "fig.pdf"
    p.touch()
    with pytest.raises(ValueError, match="columns list must be non-empty"):
        report.add_figures([str(p)], columns=[])


def test_add_figures_subcaptions(tmp_path, report):
    """subcaptions wraps each image in its own figure() block."""
    p1 = tmp_path / "a.pdf"
    p2 = tmp_path / "b.pdf"
    p1.touch()
    p2.touch()
    report.add_figures(
        [str(p1), str(p2)],
        columns=2,
        subcaptions=["Cap A", "Cap B"],
    )
    rendered = render(report)
    assert "#grid(" in rendered
    assert "caption: [Cap A]" in rendered
    assert "caption: [Cap B]" in rendered
    # No outer #figure since caption is None
    assert "#figure(" not in rendered
    # Inner figure() calls (without #) should be present
    assert "figure(" in rendered


def test_add_figures_subcaptions_with_caption(tmp_path, report):
    """subcaptions + caption produces nested figure blocks."""
    p1 = tmp_path / "a.pdf"
    p2 = tmp_path / "b.pdf"
    p1.touch()
    p2.touch()
    report.add_figures(
        [str(p1), str(p2)],
        columns=2,
        caption="Overall",
        subcaptions=["Cap A", "Cap B"],
    )
    rendered = render(report)
    assert "#figure(" in rendered
    assert "caption: [Overall]" in rendered
    assert "caption: [Cap A]" in rendered
    assert "caption: [Cap B]" in rendered


def test_add_figures_subcaptions_length_mismatch_raises(tmp_path, report):
    """subcaptions length != paths length raises ValueError."""
    p = tmp_path / "fig.pdf"
    p.touch()
    with pytest.raises(ValueError, match="subcaptions length"):
        report.add_figures([str(p)], subcaptions=["A", "B"])


# ---------------------------------------------------------------------------
# Group D — write()
# ---------------------------------------------------------------------------


def test_write_creates_typ_file(tmp_path, report):
    """write() creates the .typ file on disk."""
    out = tmp_path / "out.typ"
    report.write(str(out))
    assert out.exists()


def test_write_returns_path(tmp_path, report):
    """write() returns the Path of the written file."""
    out = tmp_path / "out.typ"
    result = report.write(str(out))
    assert isinstance(result, Path)
    assert result == out


def test_write_enforces_typ_suffix(tmp_path, report):
    """write() enforces .typ extension regardless of input suffix."""
    out = tmp_path / "out.pdf"
    result = report.write(str(out))
    assert result.suffix == ".typ"
    assert result.exists()


def test_write_content_matches_render(tmp_path, report):
    """File content written by write() matches _render()."""
    out = tmp_path / "out.typ"
    report.write(str(out))
    assert out.read_text(encoding="utf-8") == render(report)


# ---------------------------------------------------------------------------
# Group E — compile() (subprocess mocked)
# ---------------------------------------------------------------------------


def test_compile_raises_when_typst_missing(tmp_path, monkeypatch, report):
    """
    FileNotFoundError from subprocess raises RuntimeError with hint.
    """

    def fake_run(*args, **kwargs):
        raise FileNotFoundError

    monkeypatch.setattr(subprocess, "run", fake_run)
    typ = tmp_path / "r.typ"
    typ.write_text("", encoding="utf-8")
    with pytest.raises(RuntimeError, match="typst CLI not found"):
        report.compile(str(typ))


def test_compile_raises_on_nonzero_returncode(tmp_path, monkeypatch, report):
    """Non-zero typst exit code raises RuntimeError with stderr."""

    def fake_run(*args, **kwargs):
        return subprocess.CompletedProcess(
            args=[], returncode=1, stdout="", stderr="syntax error"
        )

    monkeypatch.setattr(subprocess, "run", fake_run)
    typ = tmp_path / "r.typ"
    typ.write_text("", encoding="utf-8")
    with pytest.raises(RuntimeError, match="typst compile failed"):
        report.compile(str(typ))


def test_compile_default_pdf_path(tmp_path, monkeypatch, report):
    """Default pdf_path replaces .typ suffix with .pdf."""
    captured = {}

    def fake_run(cmd, **kwargs):
        captured["cmd"] = cmd
        return subprocess.CompletedProcess(
            args=[], returncode=0, stdout="", stderr=""
        )

    monkeypatch.setattr(subprocess, "run", fake_run)
    typ = tmp_path / "r.typ"
    typ.write_text("", encoding="utf-8")
    pdf = report.compile(str(typ))
    assert pdf.suffix == ".pdf"
    assert str(pdf) == captured["cmd"][-1]


# ---------------------------------------------------------------------------
# Group F — save() (write + compile)
# ---------------------------------------------------------------------------


def test_save_writes_typ_file(tmp_path, monkeypatch, report):
    """save() writes the .typ source file to disk."""

    def fake_run(*args, **kwargs):
        return subprocess.CompletedProcess(
            args=[], returncode=0, stdout="", stderr=""
        )

    monkeypatch.setattr(subprocess, "run", fake_run)
    stem = tmp_path / "report"
    report.save(str(stem))
    assert (tmp_path / "report.typ").exists()


def test_save_returns_pdf_path(tmp_path, monkeypatch, report):
    """save() returns a Path with .pdf suffix."""

    def fake_run(*args, **kwargs):
        return subprocess.CompletedProcess(
            args=[], returncode=0, stdout="", stderr=""
        )

    monkeypatch.setattr(subprocess, "run", fake_run)
    stem = tmp_path / "report"
    pdf = report.save(str(stem))
    assert pdf.suffix == ".pdf"


# ---------------------------------------------------------------------------
# Group G — caption font size
# ---------------------------------------------------------------------------


def test_caption_font_size_8pt(report):
    """Preamble sets figure captions to 8pt."""
    rendered = render(report)
    assert "#show figure.caption: set text(size: 8pt)" in rendered


# ---------------------------------------------------------------------------
# Group H — rows_per_page
# ---------------------------------------------------------------------------


def test_rows_per_page_splits_into_chunks(tmp_path, report):
    """rows_per_page splits figures across page breaks."""
    figs = []
    for i in range(6):
        p = tmp_path / f"fig{i}.pdf"
        p.touch()
        figs.append(str(p))

    report.add_figures(figs, columns=2, rows_per_page=2)
    rendered = render(report)
    # 6 figures, 2 columns, 2 rows per page → 2 chunks (4 + 2)
    assert rendered.count("#pagebreak()") == 1
    assert rendered.count("#grid(") == 2


def test_rows_per_page_caption_on_last_chunk(tmp_path, report):
    """Caption appears only on the last chunk."""
    figs = []
    for i in range(4):
        p = tmp_path / f"fig{i}.pdf"
        p.touch()
        figs.append(str(p))

    report.add_figures(figs, columns=2, caption="My Caption", rows_per_page=1)
    rendered = render(report)
    # Only 1 caption in total (on the last chunk)
    assert rendered.count("caption: [My Caption]") == 1
    # The last chunk is a #figure, earlier ones are bare #grid
    assert rendered.count("#figure(") == 1
    assert rendered.count("#grid(") == 1  # bare grid for first chunk


def test_rows_per_page_with_subcaptions(tmp_path, report):
    """Subcaptions travel with their respective images."""
    figs = []
    for i in range(4):
        p = tmp_path / f"fig{i}.pdf"
        p.touch()
        figs.append(str(p))

    report.add_figures(
        figs,
        columns=2,
        rows_per_page=1,
        subcaptions=["A", "B", "C", "D"],
    )
    rendered = render(report)
    assert "caption: [A]" in rendered
    assert "caption: [D]" in rendered
    assert rendered.count("#pagebreak()") == 1


def test_rows_per_page_no_split_when_fits(tmp_path, report):
    """No pagebreak when all figures fit in rows_per_page."""
    figs = []
    for i in range(4):
        p = tmp_path / f"fig{i}.pdf"
        p.touch()
        figs.append(str(p))

    report.add_figures(figs, columns=2, rows_per_page=5)
    rendered = render(report)
    assert "#pagebreak()" not in rendered
