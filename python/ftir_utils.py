# -*- coding: utf-8 -*-
"""ftir_utils.py — loaders / preprocessing / style for the coffee FTIR course.

Dataset: instant-coffee MIR-DRIFT FTIR (Briandet et al.), 56 freeze-dried coffees,
286 wavenumbers 810-1911 cm-1, Arabica (29) vs Robusta (27).
Source: Mendeley Data frrv2yd9rg (FTIR_Spectra_instant_coffee.csv), public.
"""
import os, io, sys
import numpy as np
import pandas as pd

if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data")
FIGDIR = os.path.join(HERE, "figures"); os.makedirs(FIGDIR, exist_ok=True)

INK="#1A1A1A"; TEAL="#0E7C7B"; CORAL="#E36414"; GOLD="#C8941F"; SLATE="#6C757D"
VARIETY_COLORS = {"Arabica": TEAL, "Robusta": CORAL}

RAW = os.path.join(DATA, "coffee_ftir.csv")
CLEAN_CSV = os.path.join(DATA, "coffee_ftir_clean.csv")
ORANGE_TAB = os.path.join(DATA, "coffee_orange.tab")
META_COLS = ["sample_id", "variety"]


def _isnum(x):
    try: float(x); return True
    except Exception: return False


def load(verbose=False):
    """Return (meta_df, X_df, wavenumbers). Parses the transposed raw CSV on first call."""
    if not os.path.exists(CLEAN_CSV):
        raw = pd.read_csv(RAW, header=None, dtype=str)
        col0 = raw.iloc[:, 0].astype(str)
        grow = col0.str.contains("Group", case=False, na=False).idxmax()
        groups = raw.iloc[grow, 1:].dropna().astype(float).astype(int).values
        mask = col0.map(_isnum)
        wav = raw.loc[mask, 0].astype(float).values
        X = raw.loc[mask].iloc[:, 1:].apply(pd.to_numeric, errors="coerce").values.T
        variety = np.where(groups == 1, "Arabica", "Robusta")
        cols = [f"w{int(round(w))}" for w in wav]
        df = pd.DataFrame(X, columns=cols)
        df.insert(0, "variety", variety)
        df.insert(0, "sample_id", [f"C{i+1:02d}" for i in range(X.shape[0])])
        df.to_csv(CLEAN_CSV, index=False, encoding="utf-8")
        np.save(os.path.join(DATA, "wavenumbers.npy"), wav)
        _write_orange_tab(df, cols)
        if verbose:
            print(f"[load] wrote {CLEAN_CSV} shape={df.shape}; variety:",
                  dict(pd.Series(variety).value_counts()))
    df = pd.read_csv(CLEAN_CSV)
    wav = np.load(os.path.join(DATA, "wavenumbers.npy"))
    feat = [c for c in df.columns if c not in META_COLS]
    return df[META_COLS].copy(), df[feat].copy(), wav


def _write_orange_tab(df, feat_cols):
    names = ["sample_id"] + list(feat_cols) + ["variety"]
    types = ["string"] + ["continuous"] * len(feat_cols) + ["discrete"]
    flags = ["meta"] + [""] * len(feat_cols) + ["class"]
    lines = ["\t".join(names), "\t".join(types), "\t".join(flags)]
    for _, r in df.iterrows():
        lines.append("\t".join([str(r["sample_id"])] +
                     [f"{r[c]:.6g}" for c in feat_cols] + [str(r["variety"])]))
    with open(ORANGE_TAB, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def snv(X):
    """Standard Normal Variate — per-spectrum scatter correction (standard for IR/DRIFT)."""
    Xv = np.asarray(X, float)
    mu = Xv.mean(axis=1, keepdims=True)
    sd = Xv.std(axis=1, ddof=1, keepdims=True); sd[sd == 0] = 1.0
    return (Xv - mu) / sd


def variety_palette(vs): return [VARIETY_COLORS.get(v, SLATE) for v in vs]


def apply_style():
    import matplotlib as mpl
    mpl.rcParams.update({
        "figure.facecolor": "white", "axes.facecolor": "white", "savefig.facecolor": "white",
        "axes.edgecolor": "#C2CBC9", "axes.labelcolor": INK, "text.color": INK,
        "xtick.color": INK, "ytick.color": INK, "axes.grid": True, "grid.color": "#E9E9E9",
        "grid.linewidth": 0.8, "font.size": 13, "axes.titlesize": 16,
        "axes.titleweight": "bold", "figure.dpi": 130,
    })


if __name__ == "__main__":
    load(verbose=True)
