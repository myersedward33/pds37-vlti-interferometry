"""Clear the pipeline flags on the OI_FLUX table of MATISSE OIFITS files.

The MATISSE pipeline flags a sizeable fraction of the L-band total-flux
spectrum. This writes copies of the input files with every OI_FLUX flag set
to False so the full spectrum can be inspected. Visibility and closure-phase
flags are left untouched. The originals are never modified.

Usage:
    python scripts/unflag_matisse_flux.py data/matisse/lband data/matisse/lband_unflagged
"""
import argparse
from pathlib import Path

import numpy as np
from astropy.io import fits


def unflag_flux(src: Path, dst: Path) -> float:
    """Copy ``src`` to ``dst`` with OI_FLUX flags cleared. Returns the fraction unflagged."""
    with fits.open(src) as hdul:
        flags = hdul["OI_FLUX"].data["FLAG"]
        fraction = float(np.mean(flags))
        flags[:] = False
        hdul.writeto(dst, overwrite=True)
    return fraction


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("input_dir", type=Path, help="folder of MATISSE .fits files")
    parser.add_argument("output_dir", type=Path, help="where to write the unflagged copies")
    args = parser.parse_args()

    files = sorted(args.input_dir.glob("*.fits"))
    if not files:
        parser.error(f"no .fits files found in {args.input_dir}")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    for src in files:
        dst = args.output_dir / src.name
        fraction = unflag_flux(src, dst)
        print(f"{src.name}: cleared {fraction:.0%} flagged flux points -> {dst}")


if __name__ == "__main__":
    main()
