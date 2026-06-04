# -*- coding: utf-8 -*-
"""02_pca.py — PCA on SNV-corrected coffee FTIR spectra."""
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
from sklearn.decomposition import PCA
from scipy.stats import chi2
import ftir_utils as U

U.apply_style()
meta, X, wav = U.load()
Xs = U.snv(X)
Xc = Xs - Xs.mean(0)                 # mean-center for PCA
pca = PCA(n_components=8).fit(Xc); T = pca.transform(Xc)
evr = pca.explained_variance_ratio_ * 100; cum = np.cumsum(evr)

# scree
fig, ax = plt.subplots(figsize=(8.4, 4.6))
xs = np.arange(1, 9)
ax.bar(xs, evr, color=U.TEAL, alpha=.9)
ax.set_xlabel("Principal component"); ax.set_ylabel("Variance explained (%)")
ax.set_title("Scree plot — a smooth spectrum compresses to a few PCs")
ax2 = ax.twinx(); ax2.plot(xs, cum, "-o", color=U.CORAL, lw=2.4); ax2.set_ylim(0, 105)
ax2.set_ylabel("Cumulative (%)", color=U.CORAL); ax2.grid(False)
for x, c in zip(xs[:3], cum[:3]):
    ax2.annotate(f"{c:.0f}%", (x, c), textcoords="offset points", xytext=(0, 9),
                 color=U.CORAL, fontweight="bold", ha="center")
fig.tight_layout(); fig.savefig(os.path.join(U.FIGDIR, "ft03_pca_scree.png")); plt.close(fig)

# scores
fig, ax = plt.subplots(figsize=(8.4, 6.0))
for var, col in U.VARIETY_COLORS.items():
    m = meta["variety"].eq(var).values
    ax.scatter(T[m, 0], T[m, 1], s=80, alpha=.85, color=col, edgecolor="white",
               linewidth=.6, label=f"{var} (n={m.sum()})")
cov = np.cov(T[:, :2].T); vals, vecs = np.linalg.eigh(cov); o = vals.argsort()[::-1]
vals, vecs = vals[o], vecs[:, o]; ang = np.degrees(np.arctan2(vecs[1, 0], vecs[0, 0]))
w, h = 2 * np.sqrt(vals * chi2.ppf(.95, 2))
ax.add_patch(Ellipse(T[:, :2].mean(0), w, h, angle=ang, fill=False, ls="--", ec=U.INK, lw=1.3, alpha=.6))
ax.set_xlabel(f"PC1 ({evr[0]:.1f}%)"); ax.set_ylabel(f"PC2 ({evr[1]:.1f}%)")
ax.set_title("PCA scores — coffees split by species")
ax.legend(frameon=False); ax.axhline(0, color="#ccc", lw=.8); ax.axvline(0, color="#ccc", lw=.8)
fig.tight_layout(); fig.savefig(os.path.join(U.FIGDIR, "ft04_pca_scores.png")); plt.close(fig)

# loadings as spectra
P = pca.components_
fig, ax = plt.subplots(figsize=(9, 4.8))
ax.plot(wav, P[0], color=U.TEAL, lw=1.8, label=f"PC1 ({evr[0]:.0f}%)")
ax.plot(wav, P[1], color=U.CORAL, lw=1.4, alpha=.8, label=f"PC2 ({evr[1]:.0f}%)")
ax.axhline(0, color="#bbb", lw=.8); ax.invert_xaxis()
top = np.argsort(-np.abs(P[0]))[:3]
for j in top:
    ax.annotate(f"{int(round(wav[j]))}", (wav[j], P[0, j]), color=U.INK, fontsize=10,
                xytext=(0, 6), textcoords="offset points", ha="center", fontweight="bold")
ax.set_xlabel("Wavenumber (cm$^{-1}$)"); ax.set_ylabel("Loading")
ax.set_title("Loadings — which IR bands drive the axes")
ax.legend(frameon=False)
fig.tight_layout(); fig.savefig(os.path.join(U.FIGDIR, "ft05_pca_loadings.png")); plt.close(fig)

with open(os.path.join(U.DATA, "metrics_pca.txt"), "w", encoding="utf-8") as f:
    f.write("# PCA (SNV + center)\n")
    for i in range(4): f.write(f"PC{i+1}_var={evr[i]:.2f}%  cum={cum[i]:.2f}%\n")
    f.write("top_PC1_bands_cm-1=" + ", ".join(str(int(round(wav[j]))) for j in top) + "\n")
print("[02_pca] PC1=%.1f%% PC2=%.1f%% cum2=%.1f%%" % (evr[0], evr[1], cum[1]))
