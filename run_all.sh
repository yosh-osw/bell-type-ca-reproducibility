#!/usr/bin/env bash
set -euo pipefail

export MPLCONFIGDIR="${PWD}/.mplconfig"
export XDG_CACHE_HOME="${PWD}/.cache"
mkdir -p "${MPLCONFIGDIR}" "${XDG_CACHE_HOME}"

python3 analyze_spectral_1f_stats.py --workbook exponent.xlsx --outdir spectral_1f_stats
python3 make_manuscript_figures.py
python3 make_dynamic_range_figure.py
