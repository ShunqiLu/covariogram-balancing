# ML-DSA public-matrix commitment-fiber certificate

For the full public matrix, `delta(A)` is the sum of its 256 NTT-lane column-rank deficiencies.  FIPS 204 HighBits has maximum bucket size `B=2*gamma2+1`.  The deterministic certificate is

`M_A <= min((2*gamma1)^D, B^(D-delta)*q^delta)` and `h_A >= max(0, D*log2(2*gamma1/B)-delta*log2(q/B))`.

The table uses `q_H <= 2^64` and target accepted-law distance `2^-128`.  The global-XOF columns additionally use `q_R <= 2^64` and the source-hit bound `zeta <= q_R*(2^-256+2^-512)`.  The last probability is over independent uniform NTT entries for the full rectangular matrix (the ideal-XOF model for ExpandA).

| set | B | h at delta=0 | TV exponent at delta=0 | max delta | endpoint exponent | source exponent | one-trial combined | retry combined | Pr[random delta > max] | Pr[delta=0] |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| ML-DSA-44 | 190465 | 471.894 | 471.009 | 51 | 128.578 | 191.115 | 128.578 | 128.578 | < 2^-1013.539 | 0.999969453055 |
| ML-DSA-65 | 523777 | 1281.801 | 1281.108 | 272 | 129.109 | 191.308 | 129.109 | 129.109 | < 2^-13252.304 | 0.999999999996 |
| ML-DSA-87 | 523777 | 1794.521 | 1793.927 | 400 | 129.928 | 191.406 | 129.928 | 129.928 | < 2^-24866.042 | 0.999999999996 |

## Independent-mask-source QROM certificate

Geometrically summing the exact adaptive-reprogramming errors `sqrt((q0+i)*2^-h)+(q0+i)*2^-h/2`, the next table uses an atomic signing invocation, `q0 <= 2^64`, and the same `2^-128` final restart-state target.  It does not include the single-global-XOF source restriction.

| set | zero-defect exponent | max delta | endpoint exponent | Pr[random delta > max] |
|---|---:|---:|---:|---:|
| ML-DSA-44 | 203.062 | 27 | 129.360 | < 2^-520.116 |
| ML-DSA-65 | 608.208 | 240 | 128.208 | < 2^-11006.174 |
| ML-DSA-87 | 864.666 | 368 | 128.667 | < 2^-21921.500 |
