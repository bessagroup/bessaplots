# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install with all extras (use uv)
pip install -e ".[dev,tests,docs]"

# Build
make build          # python -m build → dist/

# Test
make test           # pytest (all tests)
pytest tests/test_savefig.py                          # single file
pytest tests/test_savefig.py::test_set_size_letter    # single test
pytest --cov=bessaplots --cov-report=html             # with coverage

# Lint & format
make lint           # ruff check
ruff format         # auto-format
pre-commit run --all-files  # full pre-commit suite (ruff + toml-sort)

# Docs
make docs           # mkdocs build → site/
mkdocs serve        # live preview at localhost:8000
```

## Architecture

**bessaplots** is a matplotlib utility library for publication-ready scientific figures (IEEE paper formats). It uses a `src/` layout.

### Core modules (`src/bessaplots/`)

| File | Purpose |
|------|---------|
| `__init__.py` | Auto-discovers and registers `.mplstyle` files with `plt.style.library`; exports public API |
| `save_figure.py` | `set_size()` and `savefig()` — core functions for IEEE-compliant figure sizing and PDF export; `FigureSaver` class for load/store |
| `constants.py` | `PAPER_SIZES` dict with single/double column widths for `letter`, `a4`, `b5`; legacy top-level constants for backward compatibility |
| `styles_discovery.py` | `read_styles_in_folders()` — recursively finds all `.mplstyle` files and returns a dict for matplotlib's style library |
| `styles/bessaplots.mplstyle` | Matplotlib style: Times serif, 8pt font, 600 DPI, inward ticks, no legend frame |

### Key design decisions

- **Width calculation:** `PAPER_SIZES[paper_size]["single/double_col_width"] × 0.98 / n_side_by_side`. The 0.98 factor prevents LaTeX line breaks.
- **Style registration:** Happens automatically on `import bessaplots` — no explicit `plt.style.use()` setup required by library code.
- **savefig output:** Always PDF, 300 DPI, transparent background, tight bbox with 0.01" padding.
- **Ruff config:** Line length 79, checks E/W/F/I/B/UP, numpy docstring convention; `__init__.py` exempt from F401/E402.

### CI (`.github/workflows/pull_request.yml`)

Three jobs run on every PR against Python 3.11/ubuntu-latest:
1. `pytest` — all tests must pass
2. `mkdocs build` — strict mode, warnings are errors
3. `pre-commit run --all-files` — ruff format/check + toml-sort
