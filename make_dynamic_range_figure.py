import os
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent
OUTDIR = ROOT / "dynamic_range_figures"
os.environ.setdefault("MPLCONFIGDIR", str(Path("/private/tmp/mplconfig_dynamic_range")))
os.environ.setdefault("XDG_CACHE_HOME", str(Path("/private/tmp/mplcache_dynamic_range")))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


INPUTS = [
    ("Classical", ROOT / "dynamic_range_data" / "classical_facilitation_summary.csv"),
    ("Nonclassical", ROOT / "dynamic_range_data" / "nonclassical_facilitation_summary.csv"),
]
COLORS = {100: "#4c78a8", 200: "#f58518", 400: "#54a24b"}


def load_data():
    frames = []
    for label, path in INPUTS:
        df = pd.read_csv(path)
        df["class_label"] = label
        frames.append(df)
    return pd.concat(frames, ignore_index=True)


def main():
    OUTDIR.mkdir(exist_ok=True)
    df = load_data()

    plt.rcParams.update({
        "font.family": "Arial",
        "font.size": 8,
        "axes.linewidth": 0.8,
        "xtick.direction": "in",
        "ytick.direction": "in",
        "xtick.top": False,
        "ytick.right": False,
        "legend.frameon": False,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
    })

    fig, axes = plt.subplots(1, 2, figsize=(7.2, 2.7), sharey=True)
    for ax, label in zip(axes, ["Classical", "Nonclassical"]):
        sub = df[df["class_label"] == label]
        for L in [100, 200, 400]:
            g = sub[sub["L"] == L]
            agg = g.groupby("noise")["dynamic_range"].agg(["mean", "sem"]).reset_index()
            ax.plot(
                agg["noise"],
                agg["mean"],
                marker="o",
                linewidth=1.15,
                markersize=3.0,
                color=COLORS[L],
                label=f"L={L}",
            )
            ax.fill_between(
                agg["noise"],
                agg["mean"] - agg["sem"],
                agg["mean"] + agg["sem"],
                color=COLORS[L],
                alpha=0.18,
                linewidth=0,
            )
        ax.set_title(label, pad=5)
        ax.set_xlabel(r"$p_{\mathrm{noise}}$")
        ax.set_xlim(-0.005, 0.205)
        ax.set_xticks([0.00, 0.05, 0.10, 0.15, 0.20])
        ax.set_xticklabels(["0", "0.05", "0.10", "0.15", "0.20"])
        ax.spines["top"].set_visible(True)
        ax.spines["right"].set_visible(True)
        ax.tick_params(top=False, right=False, length=3)
    axes[0].set_ylabel("Dynamic range [dB]")
    axes[1].legend(loc="upper left", handlelength=1.8)
    fig.subplots_adjust(left=0.08, right=0.99, bottom=0.20, top=0.86, wspace=0.10)

    fig.savefig(OUTDIR / "dynamic_range_exploratory.pdf")
    fig.savefig(OUTDIR / "dynamic_range_exploratory.png", dpi=300)
    print("saved", OUTDIR / "dynamic_range_exploratory.pdf")


if __name__ == "__main__":
    main()
