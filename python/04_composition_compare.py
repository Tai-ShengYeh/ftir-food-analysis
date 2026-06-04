# -*- coding: utf-8 -*-
"""04_composition_compare.py — PCA + PLS-DA on the pgmm `coffee` dataset
(directly-measured chemical constituents) to cross-check the FTIR spectral result.
Shows that Arabica vs Robusta separate on real composition too, and which
constituents drive it — so the FTIR discriminating bands map to real chemistry.
"""
import os, sys, io
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cross_decomposition import PLSRegression
from sklearn.model_selection import LeaveOneOut

if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8","utf8"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
FIGDIR = os.path.join(HERE, "figures"); DATA = os.path.join(ROOT, "data")
TEAL, CORAL, INK, GOLD = "#0E7C7B", "#E36414", "#1A1A1A", "#C8941F"
plt.rcParams.update({"figure.facecolor":"white","axes.facecolor":"white","savefig.facecolor":"white",
    "axes.edgecolor":"#C2CBC9","axes.labelcolor":INK,"text.color":INK,"xtick.color":INK,"ytick.color":INK,
    "axes.grid":True,"grid.color":"#E9E9E9","grid.linewidth":0.8,"font.size":13,"axes.titlesize":15,
    "axes.titleweight":"bold","figure.dpi":130})

df = pd.read_csv(os.path.join(DATA, "pgmm_coffee.csv"))
CHEM = ["Water","Bean Weight","Extract Yield","ph Value","Free Acid","Mineral Content","Fat",
        "Caffine","Trigonelline","Chlorogenic Acid","Neochlorogenic Acid","Isochlorogenic Acid"]
variety = df["Variety"].values.astype(int)           # 1=Arabica, 2=Robusta
is_arab = variety == 1
X = df[CHEM].values.astype(float)
Xs = StandardScaler().fit_transform(X)
print(f"n_arabica={is_arab.sum()}  n_robusta={(~is_arab).sum()}")

# ---- PCA on measured composition ----
pca = PCA(n_components=5).fit(Xs); T = pca.transform(Xs)
evr = pca.explained_variance_ratio_*100
print("PCA evr(%):", np.round(evr,1), " cum:", np.round(np.cumsum(evr),1))
fig, ax = plt.subplots(figsize=(7.8,5.6))
ax.scatter(T[is_arab,0], T[is_arab,1], s=95, color=TEAL, edgecolor="white", lw=.6, label=f"Arabica (n={is_arab.sum()})")
ax.scatter(T[~is_arab,0], T[~is_arab,1], s=95, color=CORAL, edgecolor="white", lw=.6, label=f"Robusta (n={(~is_arab).sum()})")
ax.set_xlabel(f"PC1 ({evr[0]:.1f}%)"); ax.set_ylabel(f"PC2 ({evr[1]:.1f}%)")
ax.set_title("Measured composition also splits Arabica vs Robusta"); ax.legend(frameon=False)
ax.axhline(0,color="#ccc",lw=.8); ax.axvline(0,color="#ccc",lw=.8)
fig.tight_layout(); fig.savefig(os.path.join(FIGDIR,"ftc01_comp_pca.png"), bbox_inches="tight"); plt.close(fig)

# ---- which constituents differ most (standardized Arabica - Robusta mean diff) ----
diff = Xs[is_arab].mean(0) - Xs[~is_arab].mean(0)          # +: higher in Arabica
order = np.argsort(diff)
print("\nStandardized mean diff (Arabica - Robusta), sorted:")
for j in order[::-1]:
    print(f"  {CHEM[j]:>20s}: {diff[j]:+.2f}  (Arabica {X[is_arab,j].mean():.2f} vs Robusta {X[~is_arab,j].mean():.2f})")

# ---- PLS-DA (regression on 0/1) + leave-one-out CV ----
y = is_arab.astype(float)
loo = LeaveOneOut(); yhat = np.zeros(len(y))
for tr, te in loo.split(Xs):
    m = PLSRegression(n_components=2).fit(Xs[tr], y[tr])
    yhat[te] = m.predict(Xs[te]).ravel()
acc = ((yhat>=0.5).astype(int) == y.astype(int)).mean()*100
print(f"\nPLS-DA LOO-CV accuracy = {acc:.1f}%")
pls = PLSRegression(n_components=2).fit(Xs, y); coef = pls.coef_.ravel()

# ---- drivers bar coloured by direction (teal=higher in Arabica, coral=higher in Robusta) ----
o2 = np.argsort(np.abs(diff))
fig, ax = plt.subplots(figsize=(8.6,5.6))
cols = [TEAL if diff[j]>0 else CORAL for j in o2]
ax.barh(range(len(o2)), [diff[j] for j in o2], color=cols, alpha=.92)
ax.set_yticks(range(len(o2))); ax.set_yticklabels([CHEM[j] for j in o2])
ax.axvline(0,color="#888",lw=1)
ax.set_xlabel("Standardized mean difference  (←Robusta higher    Arabica higher→)")
ax.set_title("Which constituents separate the species (measured chemistry)")
fig.tight_layout(); fig.savefig(os.path.join(FIGDIR,"ftc02_comp_drivers.png"), bbox_inches="tight"); plt.close(fig)
print("\n[saved] ftc01_comp_pca.png, ftc02_comp_drivers.png")
