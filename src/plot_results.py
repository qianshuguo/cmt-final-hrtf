"""
Results visualisation for rear-elevation perception experiment.
Generates a single multi-panel figure saved to outputs/figures/.
"""

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec

ROOT    = Path(__file__).resolve().parent.parent
DATA    = ROOT.parent / "outputs" / "all_results.csv"
OUT_DIR = DATA.parent / "figures"
OUT_DIR.mkdir(parents=True, exist_ok=True)

CHANCE   = 100 / 3          # 33.33 % for 3-AFC
PALETTE  = {"CIPIC Human": "#4878d0", "CIPIC KEMAR": "#ee854a"}
EL_ORDER = [-51, 0, 51]
EL_LABEL = {-51: "Below\n(−51°)", 0: "Middle\n(0°)", 51: "Above\n(+51°)"}

df = pd.read_csv(DATA)
df["correct_pct"] = df["correct"].astype(float) * 100


# ── helpers ───────────────────────────────────────────────────────────────────
def mean_ci(series):
    """Return (mean, 95 % CI half-width) for a boolean/float series."""
    n  = len(series)
    m  = series.mean()
    se = series.std(ddof=1) / np.sqrt(n)
    return m, 1.96 * se


def bar_group(ax, groups, values, errors, colors, labels,
              group_labels, width=0.35, ylabel="Accuracy (%)", ylim=(0, 100)):
    x    = np.arange(len(groups))
    n    = len(labels)
    offsets = np.linspace(-(n - 1) * width / 2, (n - 1) * width / 2, n)
    for i, (label, color, offset) in enumerate(zip(labels, colors, offsets)):
        ax.bar(x + offset, values[i], width, color=color, label=label,
               yerr=errors[i], capsize=4, alpha=0.88, edgecolor="white", linewidth=0.5)
    ax.axhline(CHANCE, color="grey", linestyle="--", linewidth=1.2, label="Chance (33.3 %)")
    ax.set_xticks(x)
    ax.set_xticklabels(group_labels)
    ax.set_ylim(*ylim)
    ax.set_ylabel(ylabel, fontsize=10)
    ax.spines[["top", "right"]].set_visible(False)


# ── compute summary stats ─────────────────────────────────────────────────────
datasets = ["CIPIC Human", "CIPIC KEMAR"]

# (A) overall + per-dataset bar
overall_m,  overall_ci  = mean_ci(df["correct"])
ds_stats = {
    ds: mean_ci(df.loc[df["dataset"] == ds, "correct"])
    for ds in datasets
}

# (B) per-participant scatter (pivot already computed)
pivot = pd.read_csv(DATA.parent / "summary_pivot.csv")


# (C) accuracy by elevation × dataset
el_stats = {}
for ds in datasets:
    sub = df[df["dataset"] == ds]
    el_stats[ds] = {
        el: mean_ci(sub.loc[sub["elevation_deg"] == el, "correct"])
        for el in EL_ORDER
    }

# (D) accuracy by source × dataset
sources = ["electric_guitar", "solo_violin"]
src_stats = {}
for ds in datasets:
    sub = df[df["dataset"] == ds]
    src_stats[ds] = {
        src: mean_ci(sub.loc[sub["source"] == src, "correct"])
        for src in sources
    }


# ── figure layout ─────────────────────────────────────────────────────────────
fig = plt.figure(figsize=(14, 10), dpi=150)
fig.suptitle("Rear-Elevation Perception: Experiment Results", fontsize=14, fontweight="bold", y=0.98)
gs = GridSpec(2, 3, figure=fig, hspace=0.45, wspace=0.38)

ax_a = fig.add_subplot(gs[0, 0])       # overall + dataset
ax_b = fig.add_subplot(gs[0, 1:])      # per-participant
ax_c = fig.add_subplot(gs[1, :2])      # elevation × dataset
ax_d = fig.add_subplot(gs[1, 2])       # source × dataset


# ── (A) Overall & per-dataset ─────────────────────────────────────────────────
bars_val = [overall_m * 100, ds_stats["CIPIC Human"][0] * 100, ds_stats["CIPIC KEMAR"][0] * 100]
bars_err = [overall_ci * 100,  ds_stats["CIPIC Human"][1] * 100, ds_stats["CIPIC KEMAR"][1] * 100]
colors_a = ["#6a6a6a", PALETTE["CIPIC Human"], PALETTE["CIPIC KEMAR"]]

ax_a.bar([0, 1, 2], bars_val, color=colors_a,
         yerr=bars_err, capsize=5, alpha=0.88, edgecolor="white", linewidth=0.5)
ax_a.axhline(CHANCE, color="grey", linestyle="--", linewidth=1.2, label="Chance (33.3 %)")
ax_a.set_xticks([0, 1, 2])
ax_a.set_xticklabels(["Overall", "Human\nHRTF", "KEMAR\nHRTF"], fontsize=9)
ax_a.set_ylim(0, 80)
ax_a.set_ylabel("Accuracy (%)", fontsize=10)
ax_a.set_title("(A) Overall & Dataset Accuracy", fontsize=10, fontweight="bold")
ax_a.legend(fontsize=8, frameon=False)
ax_a.spines[["top", "right"]].set_visible(False)

# annotate values
for i, (v, e) in enumerate(zip(bars_val, bars_err)):
    ax_a.text(i, v + e + 1.5, f"{v:.1f}%", ha="center", va="bottom", fontsize=8)


# ── (B) Per-participant accuracy ──────────────────────────────────────────────
participants = pivot["participant"].tolist()
x_p = np.arange(len(participants))
w   = 0.35

for i, (ds, color) in enumerate(PALETTE.items()):
    vals = pivot[ds].values
    ax_b.bar(x_p + (i - 0.5) * w, vals, w, color=color, label=ds,
             alpha=0.88, edgecolor="white", linewidth=0.5)

ax_b.axhline(CHANCE, color="grey", linestyle="--", linewidth=1.2, label="Chance")
ax_b.set_xticks(x_p)
ax_b.set_xticklabels(participants, fontsize=8, rotation=30)
ax_b.set_ylim(0, 100)
ax_b.set_ylabel("Accuracy (%)", fontsize=10)
ax_b.set_title("(B) Accuracy per Participant × Dataset", fontsize=10, fontweight="bold")
ax_b.legend(fontsize=8, frameon=False, ncol=3)
ax_b.spines[["top", "right"]].set_visible(False)


# ── (C) Elevation × dataset ───────────────────────────────────────────────────
x_e = np.arange(len(EL_ORDER))
for i, (ds, color) in enumerate(PALETTE.items()):
    vals = [el_stats[ds][el][0] * 100 for el in EL_ORDER]
    errs = [el_stats[ds][el][1] * 100 for el in EL_ORDER]
    offset = (i - 0.5) * 0.35
    ax_c.bar(x_e + offset, vals, 0.35, color=color, label=ds,
             yerr=errs, capsize=4, alpha=0.88, edgecolor="white", linewidth=0.5)
    ax_c.plot(x_e + offset, vals, "o-", color=color, markersize=5, linewidth=1.2)

ax_c.axhline(CHANCE, color="grey", linestyle="--", linewidth=1.2, label="Chance")
ax_c.set_xticks(x_e)
ax_c.set_xticklabels([EL_LABEL[e] for e in EL_ORDER], fontsize=9)
ax_c.set_ylim(0, 85)
ax_c.set_ylabel("Accuracy (%)", fontsize=10)
ax_c.set_title("(C) Accuracy by Rear Elevation × Dataset", fontsize=10, fontweight="bold")
ax_c.legend(fontsize=8, frameon=False, ncol=3)
ax_c.spines[["top", "right"]].set_visible(False)


# ── (D) Source × dataset ──────────────────────────────────────────────────────
x_s    = np.arange(len(sources))
labels_s = ["Electric\nGuitar", "Solo\nViolin"]

for i, (ds, color) in enumerate(PALETTE.items()):
    vals = [src_stats[ds][s][0] * 100 for s in sources]
    errs = [src_stats[ds][s][1] * 100 for s in sources]
    offset = (i - 0.5) * 0.35
    ax_d.bar(x_s + offset, vals, 0.35, color=color, label=ds,
             yerr=errs, capsize=4, alpha=0.88, edgecolor="white", linewidth=0.5)

ax_d.axhline(CHANCE, color="grey", linestyle="--", linewidth=1.2, label="Chance")
ax_d.set_xticks(x_s)
ax_d.set_xticklabels(labels_s, fontsize=9)
ax_d.set_ylim(0, 80)
ax_d.set_ylabel("Accuracy (%)", fontsize=10)
ax_d.set_title("(D) Accuracy by\nSource × Dataset", fontsize=10, fontweight="bold")
ax_d.legend(fontsize=8, frameon=False)
ax_d.spines[["top", "right"]].set_visible(False)


# ── save ──────────────────────────────────────────────────────────────────────
out_path = OUT_DIR / "results_summary.png"
fig.savefig(out_path, bbox_inches="tight")
print(f"Saved: {out_path}")
