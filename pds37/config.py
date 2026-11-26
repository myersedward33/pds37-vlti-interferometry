"""Paths, file lists and constants shared by every notebook.

All paths are resolved relative to the repository root. Data files are
discovered from the folders under ``data/`` (see ``data/README.md``), so no
file names or observation details live in the code.
"""
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = REPO_ROOT / "data"

GRAVITY_DIR = DATA_DIR / "gravity"
MATISSE_LBAND_DIR = DATA_DIR / "matisse" / "lband"
PIONIER_DIR = DATA_DIR / "pionier"
GRAVITY_SELECTION_FILE = DATA_DIR / "gravity_good_files.txt"

# GRAVITY science-channel instrument name used by PMOIRED
GRAVITY_INSNAME = "GRAVITY_SC"

# Wavelength windows (microns)
K_BAND = (2.00, 2.325)           # usable K-band continuum
BRG_WL0 = 2.166                  # Brackett-gamma (H I 7-4) rest wavelength
BRG_WINDOW = (BRG_WL0 - 0.025, BRG_WL0 + 0.025)
CO_BANDHEAD_WINDOW = (2.30, 2.40)


def _fits_in(folder):
    files = sorted(folder.glob("*.fits"))
    if not files:
        raise FileNotFoundError(f"No .fits files in {folder} (see data/README.md).")
    return files


def gravity_files():
    """All GRAVITY OIFITS files in data/gravity, sorted by name."""
    return _fits_in(GRAVITY_DIR)


def gravity_path(name):
    """Full path of one GRAVITY file, with a helpful error if it is missing."""
    path = GRAVITY_DIR / name
    if not path.exists():
        raise FileNotFoundError(f"{path} not found (see data/README.md).")
    return path


def gravity_good_files():
    """Exposures clean enough to fit on their own.

    Read from data/gravity_good_files.txt (one file name per line; kept out of
    git with the data). Falls back to every GRAVITY file if the list is absent.
    """
    if not GRAVITY_SELECTION_FILE.exists():
        return gravity_files()
    names = [line.strip() for line in GRAVITY_SELECTION_FILE.read_text().splitlines()
             if line.strip() and not line.startswith("#")]
    return [gravity_path(n) for n in names]


def pionier_file():
    """The combined PIONIER OIFITS file in data/pionier."""
    return _fits_in(PIONIER_DIR)[0]
