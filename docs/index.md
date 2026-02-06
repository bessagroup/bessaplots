![Bessa Research Group](img/bessa_group_logo.png)

# Bessa Plots

| [**GitHub**](https://github.com/mpvanderschelling/bessaplots)
| [**Documentation**](https://bessaplots.readthedocs.io/en/latest/)

Plottting utilities for scientific papers within the Bessa Group

**First publication:** February 3, 2026

***

## Summary

<!-- Write here a longer description of the package, what it does, and why it is useful. -->

## Statement of need

<!-- Write here the statement of need for this package -->

## Authorship

**Authors**:
- Martin van der Schelling ([m.p.vanderschelling@tudelft.nl](mailto:m.p.vanderschelling@tudelft.nl))

**Authors afilliation:**
- Delft University of Technology (Bessa Research Group)

**Maintainer:**
- Martin van der Schelling ([m.p.vanderschelling@tudelft.nl](mailto:m.p.vanderschelling@tudelft.nl))

**Maintainer afilliation:**
- Delft University of Technology (Bessa Research Group)


## Getting started

<!-- Write here how users should get started with this package -->

## Usage

Here is a minimal example of how to use `savefig` to generate publication-ready figures:

```python
import matplotlib.pyplot as plt
import bessaplots
from bessaplots.savefig import savefig

# Use the specific bessaplots style
plt.style.use('bessaplots')

# Create a plot
fig, ax = plt.subplots()
ax.plot([1, 2, 3], [1, 4, 9])
ax.set_xlabel("Time [s]")
ax.set_ylabel("Displacement [mm]")

# Save the figure specifying the paper size
# This will save 'my_figure.pdf' optimized for A4 paper
savefig(fig, "my_figure", paper_size="a4")
```

## Credits

- This package heavily inspired by [SciencePlots](https://github.com/garrettj403/SciencePlots).

## Community Support

If you find any **issues, bugs or problems** with this package, please use the [GitHub issue tracker](https://github.com/mpvanderschelling/bessaplots/issues) to report them.

## License

Copyright (c) 2026, Martin van der Schelling

All rights reserved.

This project is licensed under the BSD 3-Clause License. See [LICENSE](license.md) for the full license text.

