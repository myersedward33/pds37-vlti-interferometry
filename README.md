# Modelling VLTI interferometry of the young massive star PDS 37

Python pipeline for analysing near- and mid-infrared interferometric data of **PDS 37**, an
early-type Herbig Be star / massive young stellar object reported as a close binary in the
literature ([Koumpia et al. 2019](https://doi.org/10.1051/0004-6361/201834624)). It handles data
from three instruments at ESO's Very Large Telescope Interferometer (GRAVITY, MATISSE and PIONIER)
and fits geometric models to measure component sizes, flux ratios, companion position, and where
the hydrogen Brackett-γ emission comes from.

Interferometers do not produce images directly: they measure Fourier components of the sky
brightness (visibilities and closure phases). The approach here is **model fitting**:
geometric models (disks, Gaussians, binaries, emission lines) are compared with the data by
least squares, using global grid searches to avoid local minima and bootstrap resampling for
uncertainties.

> **No data or results are included.** The notebooks are published without outputs, and the
> data folder is excluded from version control. See [data/README.md](data/README.md) to run them
> on your own OIFITS files.

## Notebooks

| # | Notebook | What it does |
|---|---|---|
| 01 | [GRAVITY data overview](notebooks/01_gravity_data_overview.ipynb) | Inventories K-band exposures from their headers, applies telluric correction, plots visibilities, closure phases and spectra in the continuum, Brγ and CO regions |
| 02 | [GRAVITY model exploration](notebooks/02_gravity_model_exploration.ipynb) | On one exposure, steps from a single star to a binary, limb-darkened disks with Brγ lines, and azimuthally modulated disks, comparing χ² |
| 03 | [GRAVITY binary fits by epoch](notebooks/03_gravity_binary_fits_by_epoch.ipynb) | Grid search → least-squares → bootstrap → Brγ fit for each exposure in a loop; tabulates and plots the companion position over time |
| 04 | [GRAVITY joint fit](notebooks/04_gravity_joint_fit_all_epochs.ipynb) | Fits all epochs together; compares uniform-disk and Gaussian binaries |
| 05 | [MATISSE L-band fit](notebooks/05_matisse_lband_binary_fit.ipynb) | Binary grid search and fit to MATISSE L-band data |
| 06 | [PIONIER H-band overview](notebooks/06_pionier_hband_data_overview.ipynb) | Custom OIFITS reader (astropy + pandas) for files PMOIRED can't load; uv coverage, V², closure phases, Gaussian size fit with SciPy |

## Code layout

```
pds37/
├── config.py     data discovery, wavelength windows and constants shared by all notebooks
├── binary.py     grid search, Brγ model builder, separation/PA conversion, result tables
└── oifits.py     astropy/pandas readers for OIFITS tables and file summaries
scripts/
└── unflag_matisse_flux.py   command-line tool to clear MATISSE flux flags (writes copies)
notebooks/        analysis, numbered in reading order
data/             local only, never committed (see data/README.md)
```

## Running it

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
# put OIFITS files in data/ as described in data/README.md
jupyter lab notebooks/
```

The grid searches and 500-sample bootstraps in notebooks 03 and 04 take tens of minutes each
on a laptop; PMOIRED parallelises them over all CPU cores.

## Tools

[PMOIRED](https://github.com/amerand/PMOIRED) (interferometric model fitting) ·
Astropy · NumPy · SciPy · pandas · Matplotlib · Jupyter

## Acknowledgements

Model fitting uses PMOIRED by A. Mérand
([how to cite](https://github.com/amerand/PMOIRED#using-and-quoting-pmoired)).
