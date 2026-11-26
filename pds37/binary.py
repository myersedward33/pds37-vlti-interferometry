"""Helpers for fitting binary-star models to interferometric data with PMOIRED.

Conventions (same as PMOIRED): component ``A`` is the primary, fixed at the
phase centre; ``B`` is the companion at offset (``B,x``, ``B,y``) in
milliarcseconds, with x pointing East and y pointing North. Fluxes are
relative to the primary (``A,f`` = 1).
"""
import numpy as np
import pandas as pd

# Companion must be fainter than the primary
FLUX_RATIO_PRIOR = [("B,f", "<", 1)]

# Keep the Brackett-gamma line widths (Lorentzian FWHM, nm) in a physical range
# so the line fit converges instead of running off to zero or very broad lines.
BRG_LINE_PRIORS = [
    ("A,line_brg_lorentzian", ">", 0.5),
    ("A,line_brg_lorentzian", "<", 3),
    ("B,line_brg_lorentzian", ">", 0.5),
    ("B,line_brg_lorentzian", "<", 3),
]


def binary_grid_search(oi, max_sep, step, model=None, do_not_fit=("A,ud", "B,ud"),
                       verbose=1):
    """Find the companion position by fitting from a grid of starting points.

    A least-squares fit is started from every (B,x, B,y) on a square grid of
    half-width ``max_sep`` mas and spacing ``step`` mas; grid points closer
    than one step or farther than ``max_sep`` from the primary are skipped.
    A step of about 0.5 * lambda_min / B_max avoids missing the global minimum.

    Returns the best-fit parameter dictionary (also stored in ``oi.bestfit``).
    """
    start = {"A,ud": 0.1, "B,ud": 0.1, "B,f": 0.15, "B,x": 0.0, "B,y": 0.0}
    start.update(model or {})
    explore = {"grid": {"B,x": (-max_sep, max_sep, step),
                        "B,y": (-max_sep, max_sep, step)}}
    within_search_area = [("np.sqrt(B,x**2+B,y**2)", ">", step),
                          ("np.sqrt(B,x**2+B,y**2)", "<", max_sep)]
    oi.gridFit(explore, model=start, doNotFit=list(do_not_fit),
               prior=FLUX_RATIO_PRIOR, constrain=within_search_area, verbose=verbose)
    return dict(oi.bestfit["best"])


def with_brg_lines(continuum_model):
    """Add a Lorentzian Brackett-gamma line to both components of a model."""
    model = dict(continuum_model)
    for comp, f0 in (("A", -0.5), ("B", -0.3)):
        model.update({f"{comp},line_brg_wl0": 2.166,
                      f"{comp},line_brg_f": f0,
                      f"{comp},line_brg_lorentzian": 1.0})
    return model


def image_window(best, margin=1.6, minimum=10):
    """Image field of view and centre that frame both stars of a binary fit."""
    sep = float(np.hypot(best["B,x"], best["B,y"]))
    return {"imFov": max(minimum, margin * sep),
            "imX": best["B,x"] / 2, "imY": best["B,y"] / 2}


def separation_and_pa(x, y, x_err=0.0, y_err=0.0):
    """Convert companion offsets to separation (mas) and position angle (deg E of N).

    Uncertainties are propagated to first order, ignoring the x-y covariance.
    """
    sep = np.hypot(x, y)
    pa = np.degrees(np.arctan2(x, y)) % 360
    sep_err = np.hypot(x * x_err, y * y_err) / sep
    pa_err = np.degrees(np.hypot(y * x_err, x * y_err) / sep**2)
    return sep, sep_err, pa, pa_err


def format_value(value, err=0.0):
    """'value ± err' rounded to the error's 2 significant figures (e.g. 1.2345 ± 0.0012)."""
    if not err or not np.isfinite(err):
        return f"{value:.4g}"
    decimals = max(0, 1 - int(np.floor(np.log10(abs(err)))))
    return f"{value:.{decimals}f} ± {err:.{decimals}f}"


def fit_table(fits, keys):
    """Tabulate several PMOIRED fit results as 'value ± error' strings.

    ``fits`` maps a row label to a dict with 'best' and 'uncer' entries
    (e.g. ``oi.bestfit`` or ``oi.boot``). Parameters a fit does not have are left blank.
    """
    rows = {
        label: {k: format_value(fit["best"][k], fit["uncer"].get(k, 0))
                for k in keys if k in fit["best"]}
        for label, fit in fits.items()
    }
    return pd.DataFrame(rows).T.reindex(columns=keys).fillna("")
