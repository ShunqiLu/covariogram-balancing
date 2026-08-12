# Quantitative Lee rearrangement regression audit

All entries are exact integer computations. The local increment law, the majorization-distance stability bound, and the radial equality criterion and the closed sharp shell constant have mathematical proofs in the manuscript. The computations below independently reconstruct their integer values and are not used as proof.

## A. Local transfer chambers

Parameters: `0 <= p,q <= 8` and `2 <= high <= 12`.

| exact comparisons | zero increments | positive increments | activated parity endpoints | near-equal checks | gap-two boundaries |
|---:|---:|---:|---:|---:|---:|
| 5346 | 4337 | 1009 | 5172 | 1650 | 176 |

Every parity endpoint difference was in `{0,1}`. Every total increment agreed with the independent before/after lens counts. For `p=q=t`, every checked increment equaled `max(0, 2*t-high-low+1)`. For `|p-q|=1`, the same linear value holds except at transfer gap `high-low=2`, where the active value is exactly half; the parity numerator is necessarily even.

## B. Global shell stability

Parameters: `2 <= d <= 6` and `1 <= t <= 8`, all active shells `2 <= s <= 2*t`.

| shells | weighted edges | zero edges | sharp-formula mismatches |
|---:|---:|---:|---:|
| 320 | 11215 | 0 | 0 |

Minimum edge increments at the independent test radius `t=8` (shells `s=2,...,2t`):

| d | exact minima by shell |
|---:|---|
| 2 | `15 14 13 12 11 10 9 8 7 6 5 4 3 2 1` |
| 3 | `113 56 13 12 11 10 9 8 7 6 5 4 3 2 1` |
| 4 | `575 280 85 72 61 50 41 32 25 18 13 8 5 2 1` |
| 5 | `2241 1064 377 292 231 170 129 88 63 38 25 12 7 2 1` |
| 6 | `7183 3304 1289 912 681 450 321 192 129 66 41 16 9 2 1` |

The zero-edge set is empty throughout this equal-radius active region, in agreement with the strict theorem.

## C. Equality and finite-quotient boundary

| unequal-radius weighted edges | zero-gap edges | q-ary preboundary comparisons |
|---:|---:|---:|
| 7154 | 4375 | 344 |

The unequal-radius zero edges are equality chambers, not theorem failures. For a radial kernel, equality is certified exactly when every positive mixed-difference coefficient is supported on these zero-gap chambers.

The infinite-lattice order does not extend naively through wrap-around. The first reversal in the deterministic lexicographic scan used here is

`q=6, d=2, p=1, q_radius=3, (3, 1) majorizes (2, 2)`, but the lens counts are `3 > 2`.

This q-ary computation is a falsification boundary only; no finite-quotient rearrangement theorem is claimed.
