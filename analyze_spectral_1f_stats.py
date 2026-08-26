import argparse
import os
from pathlib import Path

import numpy as np
import pandas as pd

OUTDIR_DEFAULT = Path("TQE/spectral_1f_stats")
os.environ.setdefault("MPLCONFIGDIR", str(OUTDIR_DEFAULT / "_mplconfig"))
os.environ.setdefault("XDG_CACHE_HOME", str(OUTDIR_DEFAULT / "_cache"))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import statsmodels.formula.api as smf


NOISE_VALUES = np.arange(21) / 100.0

SHEET_SETS = {
    "matched_chsh": [
        ("quantum_pos", "quantum", "table_quantum<2>0_1_shuffle.txt", "quantum<2>0_1"),
        ("quantum_neg", "quantum", "table_quantum<0>-2_1_shuffle.txt", "quantum<0>-2_1"),
        ("classic_pos", "classic", "table_classic>0_1_shuffle.txt", "classic>0_1"),
        ("classic_neg", "classic", "table_classic<0_1_shuffle.txt", "classic<0_1"),
    ],
    "main_like": [
        ("quantum_low_abs", "quantum", "table_quantum<2_1_shuffle.txt", "quantum<2_1"),
        ("quantum_high_abs", "quantum", "table_quantum>2_1_shuffle.txt", "quantum>2_1"),
        ("classic_pos", "classic", "table_classic>0_1_shuffle.txt", "classic>0_1"),
        ("classic_neg", "classic", "table_classic<0_1_shuffle.txt", "classic<0_1"),
    ],
}


def compute_chsh(values):
    table = np.asarray(values, dtype=float).reshape(4, 4)

    def corr(i, j):
        r = 2 * i
        c = 2 * j
        return table[r, c] - table[r, c + 1] - table[r + 1, c] + table[r + 1, c + 1]

    return corr(0, 0) + corr(0, 1) + corr(1, 0) - corr(1, 1)


def load_chsh(path):
    rows = []
    with open(path) as f:
        for line in f:
            vals = [float(x) for x in line.strip().split()]
            if len(vals) != 16:
                continue
            rows.append(compute_chsh(vals))
    return np.asarray(rows, dtype=float)


def numeric_or_nan(value):
    return pd.to_numeric(pd.Series([value]), errors="coerce").iloc[0]


def load_sheet_records(workbook, observable, group_name, class_label, table_file, sheet_suffix, dataset_name):
    sheet = f"{observable}_{sheet_suffix}"
    df = pd.read_excel(workbook, sheet_name=sheet, header=None)
    chsh_values = load_chsh(table_file)
    n_tables = min(100, df.shape[0] - 1, len(chsh_values))
    records = []
    for table_idx in range(n_tables):
        row_idx = table_idx + 1
        for noise_idx, noise in enumerate(NOISE_VALUES):
            col = 2 + 4 * noise_idx
            alpha = numeric_or_nan(df.iat[row_idx, col])
            is_powerlaw = bool(pd.notna(alpha))
            is_1f = bool(is_powerlaw and 0.9 <= alpha < 1.1)
            records.append({
                "dataset": dataset_name,
                "observable": "local" if observable == "mean" else "global",
                "group": group_name,
                "class": class_label,
                "is_quantum": 1 if class_label == "quantum" else 0,
                "table": table_idx,
                "noise": noise,
                "noise_scaled": noise / 0.20,
                "chsh": chsh_values[table_idx],
                "abs_chsh": abs(chsh_values[table_idx]),
                "alpha": alpha,
                "is_powerlaw": int(is_powerlaw),
                "is_1f": int(is_1f),
            })
    return records


def load_dataset(workbook, dataset_name):
    records = []
    for observable in ["mean", "weightedsum"]:
        for group_name, class_label, table_file, sheet_suffix in SHEET_SETS[dataset_name]:
            records.extend(load_sheet_records(
                workbook=workbook,
                observable=observable,
                group_name=group_name,
                class_label=class_label,
                table_file=table_file,
                sheet_suffix=sheet_suffix,
                dataset_name=dataset_name,
            ))
    data = pd.DataFrame(records)
    data["chsh_scaled"] = (data["chsh"] - data["chsh"].mean()) / data["chsh"].std(ddof=0)
    return data


def wilson_ci(k, n, z=1.959963984540054):
    if n == 0:
        return np.nan, np.nan
    phat = k / n
    denom = 1 + z * z / n
    center = (phat + z * z / (2 * n)) / denom
    half = z * np.sqrt((phat * (1 - phat) + z * z / (4 * n)) / n) / denom
    return center - half, center + half


def make_proportion_table(data):
    rows = []
    for keys, g in data.groupby(["dataset", "observable", "class", "noise"]):
        dataset, observable, class_label, noise = keys
        k = int(g["is_1f"].sum())
        n = int(len(g))
        lo, hi = wilson_ci(k, n)
        rows.append({
            "dataset": dataset,
            "observable": observable,
            "class": class_label,
            "noise": noise,
            "n": n,
            "count_1f": k,
            "proportion_1f": k / n if n else np.nan,
            "ci95_low": lo,
            "ci95_high": hi,
        })
    return pd.DataFrame(rows)


def fit_logistic_models(data):
    rows = []
    terms = "noise_scaled * is_quantum + noise_scaled * chsh_scaled + is_quantum * chsh_scaled"
    formula = f"is_1f ~ {terms}"
    for (dataset, observable), g in data.groupby(["dataset", "observable"]):
        fit = smf.logit(formula, data=g).fit(disp=False, maxiter=200)
        conf = fit.conf_int()
        for term in fit.params.index:
            rows.append({
                "dataset": dataset,
                "observable": observable,
                "term": term,
                "coef_log_odds": fit.params[term],
                "odds_ratio": np.exp(fit.params[term]),
                "ci95_low_log_odds": conf.loc[term, 0],
                "ci95_high_log_odds": conf.loc[term, 1],
                "ci95_low_odds_ratio": np.exp(conf.loc[term, 0]),
                "ci95_high_odds_ratio": np.exp(conf.loc[term, 1]),
                "p_value": fit.pvalues[term],
                "n": int(fit.nobs),
                "aic": fit.aic,
                "pseudo_r2_mcfadden": fit.prsquared,
                "formula": formula,
            })
    return pd.DataFrame(rows)


def plot_ci(prop, outdir):
    colors = {"classic": "#E0542C", "quantum": "#00A978"}
    for (dataset, observable), g in prop.groupby(["dataset", "observable"]):
        fig, ax = plt.subplots(figsize=(6.2, 4.2))
        for class_label, gc in g.groupby("class"):
            gc = gc.sort_values("noise")
            yerr = np.vstack([
                gc["proportion_1f"] - gc["ci95_low"],
                gc["ci95_high"] - gc["proportion_1f"],
            ])
            yerr = np.maximum(yerr, 0)
            ax.errorbar(
                gc["noise"], gc["proportion_1f"],
                yerr=yerr,
                marker="o",
                capsize=3,
                lw=1.5,
                color=colors.get(class_label),
                label=class_label,
            )
        ax.set_xlabel(r"$p_{\mathrm{noise}}$")
        ax.set_ylabel("Proportion of 1/f spectra")
        ax.set_xlim(-0.002, 0.202)
        ax.set_ylim(0, max(0.7, min(1.0, g["ci95_high"].max() + 0.05)))
        ax.grid(True, alpha=0.25)
        ax.legend(frameon=False)
        fig.tight_layout()
        fig.savefig(outdir / f"proportion_1f_ci_{dataset}_{observable}.png", dpi=220)
        plt.close(fig)


def write_report(prop, regression, outdir):
    lines = [
        "# Spectral 1/f Occurrence Statistics",
        "",
        "The 1/f label was reconstructed from `exponent.xlsx` as power-law spectra with `0.9 <= alpha < 1.1`.",
        "Wilson intervals are reported as 95% binomial confidence intervals.",
        "",
        "## Peak Proportions",
        "",
    ]
    for (dataset, observable, class_label), g in prop.groupby(["dataset", "observable", "class"]):
        peak = g.loc[g["proportion_1f"].idxmax()]
        lines.append(
            f"- {dataset}, {observable}, {class_label}: peak={peak['proportion_1f']:.3f} "
            f"at noise={peak['noise']:.2f}, 95% CI [{peak['ci95_low']:.3f}, {peak['ci95_high']:.3f}], n={int(peak['n'])}."
        )
    lines.extend(["", "## Logistic Regression Terms with p < 0.05", ""])
    sig = regression[regression["p_value"] < 0.05].copy()
    if sig.empty:
        lines.append("- No terms reached p < 0.05.")
    else:
        for _, r in sig.sort_values(["dataset", "observable", "p_value"]).iterrows():
            lines.append(
                f"- {r['dataset']}, {r['observable']}, {r['term']}: "
                f"OR={r['odds_ratio']:.3g}, p={r['p_value']:.3g}."
            )
    (outdir / "spectral_1f_stats_report.md").write_text("\n".join(lines), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--workbook", default="exponent.xlsx")
    parser.add_argument("--outdir", default=str(OUTDIR_DEFAULT))
    args = parser.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    data = pd.concat([load_dataset(args.workbook, name) for name in SHEET_SETS], ignore_index=True)
    data.to_csv(outdir / "spectral_1f_individual_data.csv", index=False)

    prop = make_proportion_table(data)
    prop.to_csv(outdir / "spectral_1f_proportions_ci.csv", index=False)

    regression = fit_logistic_models(data)
    regression.to_csv(outdir / "spectral_1f_logistic_regression.csv", index=False)

    plot_ci(prop, outdir)
    write_report(prop, regression, outdir)

    print("saved:", outdir)
    print("peak proportions:")
    print(prop.loc[prop.groupby(["dataset", "observable", "class"])["proportion_1f"].idxmax()][
        ["dataset", "observable", "class", "noise", "proportion_1f", "ci95_low", "ci95_high", "n"]
    ].to_string(index=False))
    print("\nlogistic regression p<0.05:")
    sig = regression[regression["p_value"] < 0.05]
    print(sig[["dataset", "observable", "term", "coef_log_odds", "odds_ratio", "p_value"]].to_string(index=False))


if __name__ == "__main__":
    main()
