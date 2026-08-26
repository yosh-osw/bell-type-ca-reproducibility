# Spectral 1/f Occurrence Statistics

The 1/f label was reconstructed from `exponent.xlsx` as power-law spectra with `0.9 <= alpha < 1.1`.
Wilson intervals are reported as 95% binomial confidence intervals.

## Peak Proportions

- main_like, global, classic: peak=0.530 at noise=0.03, 95% CI [0.461, 0.598], n=200.
- main_like, global, quantum: peak=0.480 at noise=0.11, 95% CI [0.412, 0.549], n=200.
- main_like, local, classic: peak=0.615 at noise=0.07, 95% CI [0.546, 0.680], n=200.
- main_like, local, quantum: peak=0.545 at noise=0.10, 95% CI [0.476, 0.613], n=200.
- matched_chsh, global, classic: peak=0.530 at noise=0.03, 95% CI [0.461, 0.598], n=200.
- matched_chsh, global, quantum: peak=0.365 at noise=0.14, 95% CI [0.301, 0.434], n=200.
- matched_chsh, local, classic: peak=0.615 at noise=0.07, 95% CI [0.546, 0.680], n=200.
- matched_chsh, local, quantum: peak=0.440 at noise=0.13, 95% CI [0.373, 0.509], n=200.

## Logistic Regression Terms with p < 0.05

- main_like, global, noise_scaled: OR=0.115, p=2.35e-74.
- main_like, global, noise_scaled:is_quantum: OR=3.66, p=1.69e-15.
- main_like, global, is_quantum: OR=0.509, p=1.84e-14.
- main_like, global, Intercept: OR=1.4, p=4.78e-08.
- main_like, global, noise_scaled:chsh_scaled: OR=0.814, p=0.0101.
- main_like, local, noise_scaled: OR=0.092, p=2.46e-88.
- main_like, local, is_quantum: OR=0.409, p=7.33e-24.
- main_like, local, noise_scaled:is_quantum: OR=5.15, p=1.48e-23.
- main_like, local, Intercept: OR=1.62, p=9.7e-15.
- main_like, local, noise_scaled:chsh_scaled: OR=1.83, p=6.08e-14.
- main_like, local, chsh_scaled: OR=0.825, p=0.0045.
- matched_chsh, global, noise_scaled: OR=0.114, p=6.8e-75.
- matched_chsh, global, is_quantum: OR=0.235, p=1.14e-55.
- matched_chsh, global, noise_scaled:is_quantum: OR=11.3, p=4.46e-49.
- matched_chsh, global, Intercept: OR=1.41, p=4.37e-08.
- matched_chsh, local, noise_scaled: OR=0.096, p=7.08e-86.
- matched_chsh, local, is_quantum: OR=0.193, p=3.93e-71.
- matched_chsh, local, noise_scaled:is_quantum: OR=18.5, p=1.53e-70.
- matched_chsh, local, Intercept: OR=1.6, p=4.1e-14.