import matplotlib
import matplotlib.pyplot as plt
import pytest

from bessaplots.constants import PAPER_SIZES
from bessaplots.save_figure import _FRAME_PAD, FigureGrid

matplotlib.use("Agg")


# ── Construction / validation ─────────────────────────────────────────


def test_default_construction():
    grid = FigureGrid(n_figures=3)
    assert grid.n_figures == 3
    assert grid.paper_size == "letter"
    assert grid.span_columns is False
    assert grid.sharey is True
    assert grid.sharex is False
    assert grid.gutter == 0.06


def test_invalid_paper_size():
    with pytest.raises(ValueError, match="Unknown paper size"):
        FigureGrid(n_figures=2, paper_size="tabloid")


def test_n_figures_zero_raises():
    with pytest.raises(ValueError, match="n_figures must be >= 1"):
        FigureGrid(n_figures=0)


def test_ylabel_margin_too_large_raises():
    with pytest.raises(ValueError, match="ylabel_margin.*too large"):
        FigureGrid(n_figures=4, ylabel_margin=5.0)


def test_paper_size_case_insensitive():
    grid = FigureGrid(n_figures=2, paper_size="B5")
    assert grid.paper_size == "b5"


# ── Width math (sharey=True) ─────────────────────────────────────────


@pytest.mark.parametrize("paper_size", ["letter", "a4", "b5"])
@pytest.mark.parametrize("span_columns", [True, False])
def test_widths_plus_gutters_equal_textwidth(paper_size, span_columns):
    """first_width + (n-1)*rest_width + (n-1)*gutter == textwidth."""
    grid = FigureGrid(
        n_figures=3,
        paper_size=paper_size,
        span_columns=span_columns,
    )
    col = "double_col_width" if span_columns else "single_col_width"
    textwidth = PAPER_SIZES[paper_size][col]
    n = grid.n_figures
    computed = (
        grid.first_width + (n - 1) * grid.rest_width + (n - 1) * grid.gutter
    )
    assert computed == pytest.approx(textwidth, abs=1e-10)


def test_first_wider_than_rest():
    grid = FigureGrid(n_figures=3)
    assert grid.first_width > grid.rest_width


def test_width_difference_equals_effective_ylabel_margin():
    """first - rest equals ylabel_margin minus xtick_overhang.

    The first column's left edge is covered by ``ylabel_margin``,
    which absorbs the first x-tick label's overhang.  The rest of
    the columns pay for their own overhang on both sides, so the
    "extra" width the first column gets is the ylabel margin minus
    the overhang.
    """
    grid = FigureGrid(n_figures=3, ylabel_margin=0.45, xtick_overhang=0.1)
    diff = grid.first_width - grid.rest_width
    assert diff == pytest.approx(0.45 - 0.1, abs=1e-10)


@pytest.mark.parametrize("paper_size", ["letter", "a4", "b5"])
@pytest.mark.parametrize("span_columns", [True, False])
def test_axes_width_positive(paper_size, span_columns):
    grid = FigureGrid(
        n_figures=4,
        paper_size=paper_size,
        span_columns=span_columns,
    )
    assert grid.axes_width > 0


def test_axes_width_uses_frame_pad_and_xtick_overhang():
    grid = FigureGrid(n_figures=2)
    assert grid.axes_width == pytest.approx(
        grid.rest_width - 2 * (_FRAME_PAD + grid.xtick_overhang),
        abs=1e-10,
    )


def test_single_figure_degenerate():
    """n_figures=1: first and rest widths are equal, no gutter."""
    grid = FigureGrid(n_figures=1)
    assert grid.first_width == grid.rest_width


def test_custom_gutter():
    grid = FigureGrid(n_figures=3, gutter=0.10)
    assert grid.gutter == 0.10
    col = "single_col_width"
    textwidth = PAPER_SIZES["letter"][col]
    n = grid.n_figures
    computed = (
        grid.first_width + (n - 1) * grid.rest_width + (n - 1) * grid.gutter
    )
    assert computed == pytest.approx(textwidth, abs=1e-10)


# ── Height ────────────────────────────────────────────────────────────


def test_fig_height_reflects_aspect_ratio():
    grid = FigureGrid(n_figures=2, height=1.0)
    expected = grid.top_pad + grid.axes_width * 1.0 + grid.bottom_pad
    assert grid.fig_height == pytest.approx(expected, abs=1e-10)


def test_fig_height_is_scalar():
    grid = FigureGrid(n_figures=3)
    assert isinstance(grid.fig_height, float)


# ── apply() with sharey ─────────────────────────────────────────────


def test_apply_first_column_keeps_ylabel():
    grid = FigureGrid(n_figures=2)
    fig, ax = plt.subplots()
    ax.set_ylabel("My Label")
    ax.plot([0, 1], [0, 1])
    grid.apply(fig, first_column=True)

    assert ax.get_ylabel() == "My Label"
    w, h = fig.get_size_inches()
    assert w == pytest.approx(grid.first_width, abs=1e-6)
    assert h == pytest.approx(grid.fig_height, abs=1e-6)
    plt.close(fig)


def test_apply_non_first_column_strips_ylabel():
    grid = FigureGrid(n_figures=2)
    fig, ax = plt.subplots()
    ax.set_ylabel("My Label")
    ax.plot([0, 1], [0, 1])
    grid.apply(fig, first_column=False)

    assert ax.get_ylabel() == ""
    w, h = fig.get_size_inches()
    assert w == pytest.approx(grid.rest_width, abs=1e-6)
    assert h == pytest.approx(grid.fig_height, abs=1e-6)
    plt.close(fig)


def test_apply_strips_y_tick_labels():
    grid = FigureGrid(n_figures=2)
    fig, ax = plt.subplots()
    ax.plot([0, 1], [0, 1])
    grid.apply(fig, first_column=False)

    params = ax.yaxis.get_tick_params()
    assert params["labelleft"] is False
    plt.close(fig)


def test_apply_sets_subplots_adjust():
    """Axes left edge matches expected fraction."""
    grid = FigureGrid(n_figures=2)
    fig, ax = plt.subplots()
    ax.plot([0, 1], [0, 1])
    grid.apply(fig, first_column=True)

    pos = ax.get_position()
    expected_left = (grid.ylabel_margin + _FRAME_PAD) / grid.first_width
    assert pos.x0 == pytest.approx(expected_left, abs=0.01)
    plt.close(fig)


def test_axes_width_equal_across_columns():
    """The actual axes rectangle is the same width for all columns."""
    grid = FigureGrid(n_figures=3)
    widths = []
    for fc in [True, False, False]:
        fig, ax = plt.subplots()
        ax.plot([0, 1], [0, 1])
        ax.set_ylabel("Label")
        grid.apply(fig, first_column=fc)
        bbox = ax.get_position()
        widths.append(fig.get_size_inches()[0] * bbox.width)
        plt.close(fig)

    for w in widths[1:]:
        assert w == pytest.approx(widths[0], abs=1e-6)


# ── save() ────────────────────────────────────────────────────────────


def test_save_creates_file_first_column(tmp_path):
    grid = FigureGrid(n_figures=2)
    fig, ax = plt.subplots()
    ax.plot([0, 1], [0, 1])
    grid.save(fig, str(tmp_path / "fig0"), first_column=True, format="pdf")
    assert (tmp_path / "fig0.pdf").exists()
    plt.close(fig)


def test_save_creates_file_non_first_column(tmp_path):
    grid = FigureGrid(n_figures=2)
    fig, ax = plt.subplots()
    ax.plot([0, 1], [0, 1])
    grid.save(fig, str(tmp_path / "fig1"), first_column=False, format="pdf")
    assert (tmp_path / "fig1.pdf").exists()
    plt.close(fig)


# ── textwidth_fractions ──────────────────────────────────────────────


def test_textwidth_fractions_length():
    grid = FigureGrid(n_figures=3)
    assert len(grid.textwidth_fractions) == 3


def test_textwidth_fractions_sum_less_than_one():
    """Fractions sum to < 1; the remainder is gutter space."""
    grid = FigureGrid(n_figures=3)
    total = sum(grid.textwidth_fractions)
    assert total < 1.0
    col = "single_col_width"
    textwidth = PAPER_SIZES["letter"][col]
    expected_remainder = (grid.n_figures - 1) * grid.gutter / textwidth
    assert 1.0 - total == pytest.approx(expected_remainder, abs=1e-10)


def test_textwidth_fractions_first_larger():
    grid = FigureGrid(n_figures=3)
    fracs = grid.textwidth_fractions
    assert fracs[0] > fracs[1]
    assert fracs[1] == pytest.approx(fracs[2], abs=1e-10)


# ── sharey=False ─────────────────────────────────────────────────────


def test_sharey_false_equal_widths():
    grid = FigureGrid(n_figures=3, sharey=False)
    assert grid.first_width == pytest.approx(grid.rest_width, abs=1e-10)


def test_sharey_false_no_ylabel_stripping():
    grid = FigureGrid(n_figures=2, sharey=False)
    fig, ax = plt.subplots()
    ax.set_ylabel("Keep me")
    ax.plot([0, 1], [0, 1])
    grid.apply(fig, first_column=False)

    assert ax.get_ylabel() == "Keep me"
    plt.close(fig)


def test_sharey_false_textwidth_fractions_equal():
    grid = FigureGrid(n_figures=3, sharey=False)
    fracs = grid.textwidth_fractions
    assert fracs[0] == pytest.approx(fracs[1], abs=1e-10)


# ── sharex ───────────────────────────────────────────────────────────


def test_sharex_disabled_heights_equal():
    grid = FigureGrid(n_figures=2, sharex=False)
    assert grid.fig_height == pytest.approx(grid.inner_row_height, abs=1e-10)


def test_sharex_inner_row_shorter():
    grid = FigureGrid(n_figures=2, sharex=True)
    assert grid.inner_row_height < grid.fig_height


def test_sharex_height_diff_equals_xlabel_margin():
    grid = FigureGrid(n_figures=2, sharex=True, xlabel_margin=0.33)
    diff = grid.fig_height - grid.inner_row_height
    assert diff == pytest.approx(0.33, abs=1e-10)


def test_sharex_last_row_keeps_xlabel():
    grid = FigureGrid(n_figures=2, sharex=True)
    fig, ax = plt.subplots()
    ax.set_xlabel("X label")
    ax.plot([0, 1], [0, 1])
    grid.apply(fig, last_row=True)

    assert ax.get_xlabel() == "X label"
    _, h = fig.get_size_inches()
    assert h == pytest.approx(grid.fig_height, abs=1e-6)
    plt.close(fig)


def test_sharex_inner_row_strips_xlabel():
    grid = FigureGrid(n_figures=2, sharex=True)
    fig, ax = plt.subplots()
    ax.set_xlabel("X label")
    ax.plot([0, 1], [0, 1])
    grid.apply(fig, last_row=False)

    assert ax.get_xlabel() == ""
    _, h = fig.get_size_inches()
    assert h == pytest.approx(grid.inner_row_height, abs=1e-6)
    plt.close(fig)


def test_sharex_inner_row_strips_tick_labels():
    grid = FigureGrid(n_figures=2, sharex=True)
    fig, ax = plt.subplots()
    ax.plot([0, 1], [0, 1])
    grid.apply(fig, last_row=False)

    params = ax.xaxis.get_tick_params()
    assert params["labelbottom"] is False
    plt.close(fig)


def test_sharex_axes_height_same_across_rows():
    """The actual axes rectangle height is the same for all rows."""
    grid = FigureGrid(n_figures=2, sharex=True)
    heights = []
    for lr in [True, False]:
        fig, ax = plt.subplots()
        ax.plot([0, 1], [0, 1])
        grid.apply(fig, first_column=True, last_row=lr)
        bbox = ax.get_position()
        heights.append(fig.get_size_inches()[1] * bbox.height)
        plt.close(fig)

    assert heights[0] == pytest.approx(heights[1], abs=1e-6)


def test_sharex_xlabel_margin_too_large_raises():
    with pytest.raises(ValueError, match="xlabel_margin.*exceeds"):
        FigureGrid(
            n_figures=2,
            sharex=True,
            xlabel_margin=0.5,
            bottom_pad=0.38,
        )


def test_save_with_last_row_false(tmp_path):
    grid = FigureGrid(n_figures=2, sharex=True)
    fig, ax = plt.subplots()
    ax.plot([0, 1], [0, 1])
    grid.save(
        fig,
        str(tmp_path / "inner"),
        first_column=True,
        last_row=False,
        format="pdf",
    )
    assert (tmp_path / "inner.pdf").exists()
    plt.close(fig)


# ── Combined sharex + sharey ─────────────────────────────────────────


def test_sharex_sharey_combined_strips_both():
    grid = FigureGrid(n_figures=2, sharey=True, sharex=True)
    fig, ax = plt.subplots()
    ax.set_ylabel("Y")
    ax.set_xlabel("X")
    ax.plot([0, 1], [0, 1])
    grid.apply(fig, first_column=False, last_row=False)

    assert ax.get_ylabel() == ""
    assert ax.get_xlabel() == ""
    plt.close(fig)


# ── xtick_overhang ───────────────────────────────────────────────────


def test_xtick_overhang_default():
    grid = FigureGrid(n_figures=2)
    assert grid.xtick_overhang == 0.1


def test_xtick_overhang_negative_raises():
    with pytest.raises(ValueError, match="xtick_overhang must be >= 0"):
        FigureGrid(n_figures=2, xtick_overhang=-0.01)


def test_xtick_overhang_larger_than_ylabel_margin_raises():
    with pytest.raises(ValueError, match=r"ylabel_margin.*>= xtick_overhang"):
        FigureGrid(n_figures=2, ylabel_margin=0.2, xtick_overhang=0.3)


def test_xtick_overhang_zero_matches_legacy_widths():
    """xtick_overhang=0 preserves the pre-feature width math."""
    grid = FigureGrid(n_figures=3, xtick_overhang=0.0)
    assert grid.first_width - grid.rest_width == pytest.approx(
        grid.ylabel_margin, abs=1e-10
    )
    assert grid.axes_width == pytest.approx(
        grid.rest_width - 2 * _FRAME_PAD, abs=1e-10
    )


@pytest.mark.parametrize("xtick_overhang", [0.0, 0.05, 0.1, 0.2])
def test_xtick_overhang_preserves_textwidth(xtick_overhang):
    grid = FigureGrid(n_figures=3, xtick_overhang=xtick_overhang)
    n = grid.n_figures
    textwidth = PAPER_SIZES["letter"]["single_col_width"]
    computed = (
        grid.first_width + (n - 1) * grid.rest_width + (n - 1) * grid.gutter
    )
    assert computed == pytest.approx(textwidth, abs=1e-10)


def test_xtick_overhang_axes_width_equal_across_columns():
    """Absolute axes rectangle width stays identical with non-zero overhang."""
    grid = FigureGrid(n_figures=3, xtick_overhang=0.15)
    widths = []
    for fc in [True, False, False]:
        fig, ax = plt.subplots()
        ax.plot([0, 1], [0, 1])
        ax.set_ylabel("Label")
        grid.apply(fig, first_column=fc)
        bbox = ax.get_position()
        widths.append(fig.get_size_inches()[0] * bbox.width)
        plt.close(fig)

    for w in widths[1:]:
        assert w == pytest.approx(widths[0], abs=1e-6)


def test_xtick_overhang_right_margin_reserved():
    """Right edge of axes leaves xtick_overhang + FRAME_PAD inside figure."""
    grid = FigureGrid(n_figures=2, xtick_overhang=0.12)
    fig, ax = plt.subplots()
    ax.plot([0, 1], [0, 1])
    grid.apply(fig, first_column=True)

    pos = ax.get_position()
    w = fig.get_size_inches()[0]
    expected_right = 1.0 - (_FRAME_PAD + grid.xtick_overhang) / w
    assert pos.x1 == pytest.approx(expected_right, abs=1e-6)
    plt.close(fig)


def test_xtick_overhang_non_first_column_left_margin():
    """Non-first columns leave xtick_overhang + FRAME_PAD on the left."""
    grid = FigureGrid(n_figures=2, xtick_overhang=0.12)
    fig, ax = plt.subplots()
    ax.plot([0, 1], [0, 1])
    grid.apply(fig, first_column=False)

    pos = ax.get_position()
    w = fig.get_size_inches()[0]
    expected_left = (_FRAME_PAD + grid.xtick_overhang) / w
    assert pos.x0 == pytest.approx(expected_left, abs=1e-6)
    plt.close(fig)


def test_neither_shared_equal_sizes():
    grid = FigureGrid(n_figures=2, sharey=False, sharex=False)
    assert grid.first_width == pytest.approx(grid.rest_width, abs=1e-10)
    assert grid.fig_height == pytest.approx(grid.inner_row_height, abs=1e-10)

    fig, ax = plt.subplots()
    ax.set_ylabel("Y")
    ax.set_xlabel("X")
    ax.plot([0, 1], [0, 1])
    grid.apply(fig, first_column=False, last_row=False)
    assert ax.get_ylabel() == "Y"
    assert ax.get_xlabel() == "X"
    plt.close(fig)
