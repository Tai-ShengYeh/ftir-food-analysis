# -*- coding: utf-8 -*-
"""03_plsda.py — PLS-DA on coffee FTIR: Arabica vs Robusta."""
import os
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cross_decomposition import PLSRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, FunctionTransformer
from sklearn.model_selection import StratifiedKFold, cross_val_predict
import ftir_utils as U

U.apply_style()
meta, X, wav = U.load()
Xraw = X.values
y = (meta["variety"].values == "Arabica").astype(int)   # 1=Arabica, 0=Robusta
n1, n0 = int(y.sum()), int((y == 0).sum())


def pipe(k):
    return Pipeline([("snv", FunctionTransformer(U.snv)),
                     ("center", StandardScaler(with_std=False)),
                     ("pls", PLSRegression(n_components=k))])


ks = range(1, 13)
cv = StratifiedKFold(5, shuffle=True, random_state=42)
acc = []
for k in ks:
    yh = cross_val_predict(pipe(k), Xraw, y.astype(float), cv=cv).ravel()
    acc.append(((yh >= 0.5).astype(int) == y).mean() * 100)
acc = np.array(acc); best_k = int(list(ks)[acc.argmax()]); best = float(acc.max())

fig, ax = plt.subplots(figsize=(8.4, 4.6))
ax.plot(list(ks), acc, "-o", color=U.TEAL, lw=2.4)
ax.scatter([best_k], [best], s=160, color=U.CORAL, zorder=5, label=f"best: {best_k} LV, {best:.0f}%")
ax.set_xlabel("Number of latent variables (LV)"); ax.set_ylabel("5-fold CV accuracy (%)")
ax.set_title("Choosing model complexity"); ax.legend(frameon=False)
fig.tight_layout(); fig.savefig(os.path.join(U.FIGDIR, "ft07_plsda_cv.png")); plt.close(fig)

# final model for scores + coef/VIP
pp = pipe(best_k).fit(Xraw, y.astype(float)); pls = pp.named_steps["pls"]
T = pls.x_scores_
fig, ax = plt.subplots(figsize=(8.0, 5.6))
for lab, val, col in [("Arabica", 1, U.TEAL), ("Robusta", 0, U.CORAL)]:
    m = y == val
    ax.scatter(T[m, 0], T[m, 1], s=85, alpha=.85, color=col, edgecolor="white",
               linewidth=.6, label=f"{lab} (n={m.sum()})")
ax.set_xlabel("PLS LV1"); ax.set_ylabel("PLS LV2")
ax.set_title("PLS-DA scores — supervised split of the two species")
ax.legend(frameon=False); ax.axhline(0, color="#ccc", lw=.8); ax.axvline(0, color="#ccc", lw=.8)
fig.tight_layout(); fig.savefig(os.path.join(U.FIGDIR, "ft06_plsda_scores.png")); plt.close(fig)

# CV confusion at best_k
yh = (cross_val_predict(pipe(best_k), Xraw, y.astype(float), cv=cv).ravel() >= 0.5).astype(int)
cm = np.zeros((2, 2), int)
for t, p in zip(y, yh): cm[1 - t, 1 - p] += 1
labels = ["Arabica", "Robusta"]
fig, ax = plt.subplots(figsize=(5.6, 5.0))
ax.imshow(cm, cmap="BuGn")
for i in range(2):
    for j in range(2):
        ax.text(j, i, cm[i, j], ha="center", va="center", fontsize=22, fontweight="bold",
                color="white" if cm[i, j] > cm.max() * .6 else U.INK)
ax.set_xticks([0, 1]); ax.set_xticklabels(labels); ax.set_yticks([0, 1])
ax.set_yticklabels(labels, rotation=90, va="center"); ax.set_xlabel("Predicted"); ax.set_ylabel("Actual")
ax.set_title(f"Cross-validated confusion ({best_k} LV)"); ax.grid(False)
fig.tight_layout(); fig.savefig(os.path.join(U.FIGDIR, "ft08_plsda_confusion.png")); plt.close(fig)

# discriminating bands: regression coefficient vs wavenumber
coef = pls.coef_.ravel()
fig, ax = plt.subplots(figsize=(9, 4.8))
ax.plot(wav, coef, color=U.CORAL, lw=1.6); ax.axhline(0, color="#bbb", lw=.8); ax.invert_xaxis()
top = np.argsort(-np.abs(coef))[:4]
for j in top:
    ax.annotate(f"{int(round(wav[j]))}", (wav[j], coef[j]), color=U.INK, fontsize=10,
                xytext=(0, 6 if coef[j] >= 0 else -14), textcoords="offset points",
                ha="center", fontweight="bold")
ax.set_xlabel("Wavenumber (cm$^{-1}$)"); ax.set_ylabel("PLS-DA coefficient")
ax.set_title("Which IR bands separate Arabica from Robusta?")
fig.tight_layout(); fig.savefig(os.path.join(U.FIGDIR, "ft09_plsda_coef.png")); plt.close(fig)

sens = cm[0, 0] / cm[0].sum() * 100; spec = cm[1, 1] / cm[1].sum() * 100
with open(os.path.join(U.DATA, "metrics_plsda.txt"), "w", encoding="utf-8") as f:
    f.write(f"n_arabica={n1}\nn_robusta={n0}\nbest_LV={best_k}\nbest_cv_acc={best:.1f}%\n")
    f.write(f"acc_1LV={acc[0]:.1f}%\narabica_recall={sens:.1f}%\nrobusta_recall={spec:.1f}%\n")
    f.write(f"confusion=[[{cm[0,0]},{cm[0,1]}],[{cm[1,0]},{cm[1,1]}]]\n")
    f.write("top_bands_cm-1=" + ", ".join(str(int(round(wav[j]))) for j in top) + "\n")
print(f"[03_plsda] {n1} Arabica vs {n0} Robusta | best {best_k} LV -> {best:.1f}% CV acc")
