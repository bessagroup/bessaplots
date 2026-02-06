import matplotlib.pyplot as plt
import pytest

from bessaplots.constants import PAPER_SIZES
from bessaplots.save_figure import set_size


@pytest.mark.parametrize("paper_size", ["letter", "a4", "b5"])
@pytest.mark.parametrize("span_columns", [False, True])
def test_set_size_dimensions(paper_size, span_columns):
    """Test that set_size sets the correct figure dimensions from constants."""
    fig = plt.figure()

    # Defaults: n_side_by_side=1, height=0.8
    fig = set_size(fig, span_columns=span_columns, paper_size=paper_size)

    width, height = fig.get_size_inches()

    expected_width_base = (
        PAPER_SIZES[paper_size]["double_col_width"]
        if span_columns
        else PAPER_SIZES[paper_size]["single_col_width"]
    )

    # set_size logic: target_width = total_width * (0.98 / n_side_by_side)
    expected_width = expected_width_base * 0.98
    expected_height = expected_width * 0.8

    assert width == pytest.approx(expected_width, abs=0.01)
    assert height == pytest.approx(expected_height, abs=0.01)

    plt.close(fig)


@pytest.mark.parametrize("n_side_by_side", [1, 2, 3])
def test_set_size_side_by_side(n_side_by_side):
    """Test that n_side_by_side scales the width correctly."""
    fig = plt.figure()
    paper_size = "letter"
    fig = set_size(fig, n_side_by_side=n_side_by_side, paper_size=paper_size)

    width, _ = fig.get_size_inches()

    base_width = PAPER_SIZES[paper_size]["single_col_width"]
    expected_width = base_width * (0.98 / n_side_by_side)

    assert width == pytest.approx(expected_width, abs=0.01)
    plt.close(fig)


def test_set_size_invalid_paper_size():
    """Test that invalid paper size raises ValueError."""
    fig = plt.figure()
    with pytest.raises(ValueError, match="Unknown paper size"):
        set_size(fig, paper_size="invalid_size")
    plt.close(fig)


def test_set_size_case_insensitive():
    """Test that paper_size is case-insensitive."""
    fig = plt.figure()
    fig = set_size(fig, paper_size="LETTER")
    width, _ = fig.get_size_inches()

    expected_width = PAPER_SIZES["letter"]["single_col_width"] * 0.98
    assert width == pytest.approx(expected_width, abs=0.01)
    plt.close(fig)
