# Reproducibility Package

This repository contains the code and data associated with the revised manuscript:

**Noise-Induced Spectral Organization in Stochastic Cellular Automata Driven by Bell-Type Probability Structures**

submitted to IEEE Transactions on Quantum Engineering.

This package is intended to support reproducibility of the main statistical analyses and figures in the revised/resubmitted version of the manuscript. It includes the scripts and data used for the spectral analyses, Wilson confidence intervals, logistic-regression analysis, CHSH-based classification of probability tables, and the auxiliary dynamic-range analysis reported in the Supplementary Material.

## Contents

- `analyze_spectral_1f_stats.py`: reconstructs the 1/f occurrence labels from `exponent.xlsx`, computes Wilson 95% confidence intervals, and fits logistic-regression models.
- `make_tqe_submission_figures.py`: regenerates the main manuscript figures based on the statistics CSV files.
- `make_dynamic_range_figure.py`: regenerates the auxiliary dynamic-range figure reported in the Supplementary Material.
- `exponent.xlsx`: source workbook containing fitted spectral exponents used to identify 1/f-type spectra.
- `table_*.txt`: probability tables used to compute CHSH values and define classical/nonclassical groups.
- `spectral_1f_stats/`: CSV outputs used in the manuscript, including proportions, individual reconstructed labels, and logistic-regression results.
- `dynamic_range_data/`: summary CSV files used for the exploratory dynamic-range figure.
- `figures/`: regenerated PDF figures used in the manuscript.
- `dynamic_range_figures/`: dynamic-range figure files included for reference.

## Requirements

Install the Python dependencies with:

```bash
pip install -r requirements.txt
```

The scripts were prepared for Python 3.10 or later.

## Reproducing the Analysis

From this directory, run:

```bash
bash run_all.sh
```

This command:

1. Recomputes the individual 1/f labels and summary statistics from `exponent.xlsx`.
2. Recomputes Wilson confidence intervals and logistic-regression results.
3. Regenerates the manuscript figures in `figures/`.
4. Regenerates the auxiliary dynamic-range figure used in the Supplementary Material.

The main generated files are:

- `spectral_1f_stats/spectral_1f_individual_data.csv`
- `spectral_1f_stats/spectral_1f_proportions_ci.csv`
- `spectral_1f_stats/spectral_1f_logistic_regression.csv`
- `figures/occurrence_ci_local_global.pdf`
- `figures/occurrence_ci_matched_chsh.pdf`
- `figures/logistic_noise_class_interaction.pdf`
- `dynamic_range_figures/dynamic_range_exploratory.pdf`

## Notes

The label "1/f-type spectrum" is reconstructed as a detected power-law spectrum with exponent `0.9 <= alpha < 1.1`, matching the manuscript analysis.

The model class labels in some scripts and source filenames use `quantum` for the nonclassical/Bell-type probability-table condition and `classic` for the classical probability-table condition. In the revised manuscript, these conditions are described as `nonclassical` and `classical`, respectively.

The dynamic-range analysis is included as an auxiliary analysis supporting the discussion of noise-broadened responsiveness. It should not be interpreted as a task-level benchmark or as evidence for a universal optimal noise level.
