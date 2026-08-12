# Exact fresh-challenge ML-DSA z-norm interface factors

Scope: the exact powers below are the ideal z-target acceptances and the denominators that amplify the prequery-hit error in the paper's classical-ROM freshness theorem. The companion `mldsa_fiber.*` outputs certify the needed commitment min-entropy from the public matrix rank defect. These values are not complete-loop rejection probabilities; the FIPS average repetition factors use all signing checks. The full reduced fractions are in `mldsa_case.csv`.

| set | d=256 ell | beta | gamma1 | maximal common factor | 1/G | FIPS symmetric-z factor | 1/G | FIPS PDF loop reps. | potential-update loop reps. |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| ML-DSA-44 | 1024 | 78 | 131072 | `((131072-78)/131072)^1024` = 0.543591958807 | 1.839615 | `((2*(131072-78)-1)/(2*131072))^1024` = 0.541471431117 | 1.846820 | 4.25 | 4.36 |
| ML-DSA-65 | 1280 | 196 | 524288 | `((524288-196)/524288)^1280` = 0.619647140293 | 1.613822 | `((2*(524288-196)-1)/(2*524288))^1280` = 0.618890913682 | 1.615794 | 5.10 | 5.14 |
| ML-DSA-87 | 1792 | 120 | 524288 | `((524288-120)/524288)^1792` = 0.663515412878 | 1.507124 | `((2*(524288-120)-1)/(2*524288))^1792` = 0.662382184100 | 1.509702 | 3.85 | 3.91 |

For one coefficient the source interval is `[-gamma1+1, gamma1]`.  Its maximal common target over every integer offset in `[-beta,beta]` is `[-gamma1+1+beta, gamma1-beta]`, with `2(gamma1-beta)` points. The strict symmetric FIPS check uses one fewer point. The final two columns distinguish the complete-loop values printed in the 2024 FIPS 204 PDF from NIST's potential-updates spreadsheet retrieved on 2026-08-02 (spreadsheet last updated 2026-07-31).
