# -*- coding: utf-8 -*-
"""01_explore.py — coffee FTIR: raw + SNV spectra by variety."""
import os
import numpy as np
import matplotlib.pyplot as plt
import ftir_utils as U

U.apply_style()
meta, X, wav = U.load(verbose=True)
Xv = X.values


def spectra_plot(M, title, fname, ylab):
    fig, ax = plt.subplots(figsize=(9, 4.6))
    for var, col in U.VARIETY_COLORS.items():
        for i in meta.index[meta["variety"].eq(var)]:
            ax.plot(wav, M[i], color=col, lw=0.7, alpha=0.45)
    for var, col in U.VARIETY_COLORS.items():
        ax.plot([], [], color=col, lw=2.4, label=var)
    ax.invert_xaxis()
    ax.set_xlabel("Wavenumber (cm$^{-1}$)"); ax.set_ylabel(ylab)
    ax.set_title(title); ax.legend(frameon=False)
    fig.tight_layout(); fig.savefig(os.path.join(U.FIGDIR, fname)); plt.close(fig)


spectra_plot(Xv, "Instant-coffee FTIR — each coffee = a 286-point spectrum",
             "ft01_raw_spectra.png", "DRIFT absorbance")
spectra_plot(U.snv(X), "After SNV — baseline aligned, chemistry stands out",
             "ft02_snv_spectra.png", "SNV absorbance")

with open(os.path.join(U.DATA, "metrics_explore.txt"), "w", encoding="utf-8") as f:
    f.write(f"n_samples={Xv.shape[0]}\nn_wavenumbers={Xv.shape[1]}\n")
    f.write(f"wav_min={wav.min():.1f}\nwav_max={wav.max():.1f}\n")
    f.write("variety=" + ", ".join(f"{k}:{v}" for k, v in meta['variety'].value_counts().items()) + "\n")
print("[01_explore] ft01, ft02 written")
