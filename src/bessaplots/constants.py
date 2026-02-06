# 1. Base widths from your IEEEtran.cls / Logs

# 2. Paper sizes and their column widths (in inches)
PAPER_SIZES = {
    "letter": {
        "single_col_width": 252.0 / 72.27,  # ~3.486 inches
        "double_col_width": 516.0 / 72.27,  # ~7.139 inches
    },
    "a4": {
        "single_col_width": 252.0 / 72.27,  # ~3.48 inches (IEEE A4)
        "double_col_width": 516.0 / 72.27,  # ~7.16 inches (IEEE A4)
    },
    "b5": {
        "single_col_width": 185.0 / 72.27,  # ~2.56 inches (Estimated)
        "double_col_width": 387.0 / 72.27,  # ~5.35 inches (Estimated)
    },
}

# Legacy constants (defaults to letter)
SINGLE_COL_WIDTH = PAPER_SIZES["letter"]["single_col_width"]
DOUBLE_COL_WIDTH = PAPER_SIZES["letter"]["double_col_width"]
GOLDEN_RATIO = (5**0.5 - 1) / 2
