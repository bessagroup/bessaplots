from bessaplots.constants import (
    DOUBLE_COL_WIDTH,
    PAPER_SIZES,
    SINGLE_COL_WIDTH,
)


def test_paper_sizes_keys():
    """Verify that all expected paper sizes are present."""
    expected_keys = {"letter", "a4", "b5"}
    assert set(PAPER_SIZES.keys()) == expected_keys


def test_paper_sizes_dimensions():
    """Verify that dimensions are floats and positive."""
    for _size, dims in PAPER_SIZES.items():
        assert "single_col_width" in dims
        assert "double_col_width" in dims
        assert isinstance(dims["single_col_width"], float)
        assert isinstance(dims["double_col_width"], float)
        assert dims["single_col_width"] > 0
        assert dims["double_col_width"] > 0
        assert dims["double_col_width"] > dims["single_col_width"]


def test_legacy_constants_match_letter():
    """Verify that legacy constants match the letter size definition."""
    assert SINGLE_COL_WIDTH == PAPER_SIZES["letter"]["single_col_width"]
    assert DOUBLE_COL_WIDTH == PAPER_SIZES["letter"]["double_col_width"]
