"""Lightweight OIFITS readers and header summaries built on astropy.

PMOIRED does the heavy lifting for GRAVITY and MATISSE, but it cannot load
PIONIER files where every spectral channel is stored under its own INSNAME
(one wavelength per OI_WAVELENGTH table). These helpers read the tables
directly into pandas DataFrames instead.
"""
from pathlib import Path

import numpy as np
import pandas as pd
from astropy.io import fits
from astropy.time import Time


def summarize_files(paths):
    """One row per OIFITS file: observing date, exposures, telescopes used."""
    rows = []
    for path in map(Path, paths):
        with fits.open(path) as hdul:
            array = next(h for h in hdul if h.name == "OI_ARRAY").data
            sta_names = dict(zip(array["STA_INDEX"], array["STA_NAME"]))
            vis = [h.data for h in hdul if h.name in ("OI_VIS2", "OI_VIS")]
            mjd = np.concatenate([d["MJD"] for d in vis])
            used = sorted({sta_names[i] for d in vis for i in np.ravel(d["STA_INDEX"])})
            rows.append({
                "file": path.name,
                "date_obs (UT)": Time(mjd.min(), format="mjd").iso[:16],
                "mjd_start": round(float(mjd.min()), 4),
                "n_exposures": len(np.unique(np.round(mjd, 4))),
                "stations": "-".join(used),
                "telluric_corrected": "TELLURICS" in hdul,
            })
    return pd.DataFrame(rows)


def _wavelength_tables(hdul):
    """Map INSNAME -> array of effective wavelengths (m)."""
    return {
        h.header["INSNAME"]: np.atleast_1d(h.data["EFF_WAVE"])
        for h in hdul if h.name == "OI_WAVELENGTH"
    }


def _channel(data, col, j):
    """Column ``col`` for spectral channel ``j`` (handles 1-channel tables)."""
    return np.asarray(data[col]).reshape(len(data), -1)[:, j]


def read_vis2(path):
    """Squared visibilities as a tidy DataFrame (one row per baseline per channel)."""
    frames = []
    with fits.open(path) as hdul:
        wl_tables = _wavelength_tables(hdul)
        for h in hdul:
            if h.name != "OI_VIS2":
                continue
            d = h.data
            for j, wl in enumerate(wl_tables[h.header["INSNAME"]]):
                frames.append(pd.DataFrame({
                    "mjd": d["MJD"], "u": d["UCOORD"], "v": d["VCOORD"], "wl": wl,
                    "vis2": _channel(d, "VIS2DATA", j),
                    "vis2_err": _channel(d, "VIS2ERR", j),
                    "flag": _channel(d, "FLAG", j),
                }))
    df = pd.concat(frames, ignore_index=True)
    df["baseline_m"] = np.hypot(df.u, df.v)
    df["spatial_freq"] = df.baseline_m / df.wl / 1e6          # mega-lambda
    df["night"] = _night(df.mjd)
    return df[~df.flag].reset_index(drop=True)


def read_t3(path):
    """Closure phases as a tidy DataFrame (one row per triangle per channel)."""
    frames = []
    with fits.open(path) as hdul:
        wl_tables = _wavelength_tables(hdul)
        for h in hdul:
            if h.name != "OI_T3":
                continue
            d = h.data
            u1, v1, u2, v2 = d["U1COORD"], d["V1COORD"], d["U2COORD"], d["V2COORD"]
            bmax = np.max([np.hypot(u1, v1), np.hypot(u2, v2),
                           np.hypot(u1 + u2, v1 + v2)], axis=0)
            for j, wl in enumerate(wl_tables[h.header["INSNAME"]]):
                frames.append(pd.DataFrame({
                    "mjd": d["MJD"], "wl": wl, "bmax_m": bmax,
                    "t3phi": _channel(d, "T3PHI", j),
                    "t3phi_err": _channel(d, "T3PHIERR", j),
                    "flag": _channel(d, "FLAG", j),
                }))
    df = pd.concat(frames, ignore_index=True)
    df["spatial_freq_max"] = df.bmax_m / df.wl / 1e6
    df["night"] = _night(df.mjd)
    return df[~df.flag].reset_index(drop=True)


def _night(mjd):
    """Calendar date of the start of the observing night (Chile, ~UT-4h..-12h)."""
    return Time(np.asarray(mjd) - 0.5, format="mjd").to_value("iso", subfmt="date")
