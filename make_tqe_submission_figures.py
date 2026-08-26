from pathlib import Path

import os
os.environ.setdefault("MPLCONFIGDIR", str(Path(".mplconfig").resolve()))
os.environ.setdefault("XDG_CACHE_HOME", str(Path(".cache").resolve()))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

plt.rcParams.update(
    {
        "font.family": "DejaVu Sans",
        "font.size": 10,
        "axes.titlesize": 11,
        "axes.labelsize": 10,
        "xtick.labelsize": 9,
        "ytick.labelsize": 9,
        "legend.fontsize": 9,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
    }
)


ROOT = Path(__file__).resolve().parent
STATS = ROOT / "spectral_1f_stats"
FIGURES = ROOT / "figures"


COLORS = {
    "quantum": "#D55E00",
    "classic": "#009E73",
    "ECA": "#666666",
}
LABELS = {
    "quantum": "Nonclassical",
    "classic": "Classical",
    "ECA": "ECA",
}


def style_axes(ax):
    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_linewidth(0.8)
    ax.grid(False)
    ax.tick_params(axis="both", which="both", direction="in", top=False, right=False, width=0.8)
    ax.tick_params(axis="both", which="major", length=3.5)
    ax.tick_params(axis="both", which="minor", length=2.0)
    ax.set_xlim(0, 0.2)
    ax.set_ylim(0, 0.75)
    ax.set_xticks([0, 0.05, 0.10, 0.15, 0.20])
    ax.set_xticklabels(["0", "0.05", "0.10", "0.15", "0.20"])
    ax.set_yticks([0.1, 0.3, 0.5, 0.7])
    ax.set_xlabel(r"$p_{\mathrm{noise}}$")
    ax.set_ylabel(r"Proportion of $1/f$ spectra")


def style_boxed_axes(ax):
    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_linewidth(0.8)
    ax.grid(False)
    ax.tick_params(axis="both", which="both", direction="in", top=False, right=False, width=0.8)
    ax.tick_params(axis="both", which="major", length=3.5)
    ax.tick_params(axis="both", which="minor", length=2.0)


def plot_occurrence_ci():
    df = pd.read_csv(STATS / "spectral_1f_proportions_ci_from_existing_svg.csv")
    fig, axes = plt.subplots(1, 2, figsize=(7.8, 3.6), sharey=True)

    for ax, observable, title in zip(axes, ["local", "global"], ["Local", "Global"]):
        sub = df[df["observable"] == observable]
        for cls in ["classic", "quantum", "ECA"]:
            g = sub[sub["class"] == cls].sort_values("noise")
            if g.empty:
                continue
            x = g["noise"].to_numpy(float)
            y = g["proportion_rounded"].to_numpy(float)
            lo = g["ci95_low"].to_numpy(float)
            hi = g["ci95_high"].to_numpy(float)
            color = COLORS[cls]
            linestyle = "--" if cls == "ECA" else "-"
            ax.plot(x, y, color=color, lw=1.35, ls=linestyle, label=LABELS[cls], zorder=3)
            if cls != "ECA":
                ax.fill_between(x, lo, hi, color=color, alpha=0.18, linewidth=0, zorder=2)
        ax.set_title(title)
        style_axes(ax)

    axes[1].set_ylabel("")
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", ncol=3, frameon=False, bbox_to_anchor=(0.5, 1.04))
    fig.subplots_adjust(left=0.08, right=0.995, bottom=0.16, top=0.84, wspace=0.14)
    fig.savefig(FIGURES / "occurrence_ci_local_global.pdf", bbox_inches="tight")
    plt.close(fig)


def plot_matched_chsh_ci():
    df = pd.read_csv(STATS / "spectral_1f_proportions_ci.csv")
    df = df[df["dataset"] == "matched_chsh"]
    fig, axes = plt.subplots(1, 2, figsize=(7.8, 3.6), sharey=True)

    for ax, observable, title in zip(axes, ["local", "global"], ["Local", "Global"]):
        sub = df[df["observable"] == observable]
        for cls in ["classic", "quantum"]:
            g = sub[sub["class"] == cls].sort_values("noise")
            x = g["noise"].to_numpy(float)
            y = g["proportion_1f"].to_numpy(float)
            lo = g["ci95_low"].to_numpy(float)
            hi = g["ci95_high"].to_numpy(float)
            color = COLORS[cls]
            ax.plot(x, y, color=color, lw=1.35, label=LABELS[cls], zorder=3)
            ax.fill_between(x, lo, hi, color=color, alpha=0.18, linewidth=0, zorder=2)
        ax.set_title(title)
        style_axes(ax)

    axes[1].set_ylabel("")
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", ncol=2, frameon=False, bbox_to_anchor=(0.5, 1.04))
    fig.subplots_adjust(left=0.08, right=0.995, bottom=0.16, top=0.84, wspace=0.14)
    fig.savefig(FIGURES / "occurrence_ci_matched_chsh.pdf", bbox_inches="tight")
    plt.close(fig)


def plot_interaction_or():
    df = pd.read_csv(STATS / "spectral_1f_logistic_regression.csv")
    df = df[df["term"] == "noise_scaled:is_quantum"].copy()
    df["label"] = df["dataset"].map({"main_like": "Full set", "matched_chsh": "Matched CHSH"}) + "\n" + df[
        "observable"
    ].map({"local": "local", "global": "global"})
    order = [
        ("main_like", "local"),
        ("main_like", "global"),
        ("matched_chsh", "local"),
        ("matched_chsh", "global"),
    ]
    df["order"] = df.apply(lambda r: order.index((r["dataset"], r["observable"])), axis=1)
    df = df.sort_values("order")

    fig, ax = plt.subplots(figsize=(4.6, 2.15))
    y = np.arange(len(df))
    x = df["odds_ratio"].to_numpy(float)
    lo = df["ci95_low_odds_ratio"].to_numpy(float)
    hi = df["ci95_high_odds_ratio"].to_numpy(float)
    xerr = np.vstack([x - lo, hi - x])
    ax.errorbar(x, y, xerr=xerr, fmt="o", color="#0072B2", ecolor="#0072B2", elinewidth=1.8, capsize=3)
    ax.axvline(1, color="#555555", lw=1, ls="--")
    ax.set_xscale("log")
    ax.set_yticks(y)
    ax.set_yticklabels(df["label"])
    ax.invert_yaxis()
    ax.set_ylim(len(df) - 0.25, -0.75)
    ax.set_xlabel("Odds ratio for noise x nonclassical interaction")
    style_boxed_axes(ax)
    fig.tight_layout()
    fig.savefig(FIGURES / "logistic_noise_class_interaction.pdf", bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    plot_occurrence_ci()
    plot_matched_chsh_ci()
    plot_interaction_or()
