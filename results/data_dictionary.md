# Result-file data dictionary

All `*_exact` fields are reduced integer fractions written as `p/q`. Decimal
columns are display aids and are never used for feasibility decisions.

- `baseline.csv`: pairwise overlap counts and acceptance for named fixed shifts.
- `common_core.csv`: exhaustive first-feasible-scale search. `source_count` and
  `target_count` are literal integers; `acceptance_exact=target_count/source_count`;
  `reciprocal_acceptance_exact` is its geometric reciprocal, not a protocol
  retry count. `target_support_log_cardinality` is
  `ceil(log2(target_count))`, the optimal fixed-length response-component
  payload attained by public rank/unrank. `target_coordinate_box_upper_bound`
  is a fixed-width coordinate payload. Neither includes the other signature
  fields.
- `common_core_sensitivity.csv`: 72 exact same-scale comparisons at dimensions
  8, 16, and 32 and cube-anchored thresholds 1/2, 3/4, 9/10, and 99/100. The
  three-objective Pareto flag maximizes exact acceptance and minimizes exact
  squared maximum norm and optimal fixed-length rank payload.
- `cross_arbitrary.json`: all 27 signed-permutation representatives in
  dimension four through `l1` radius six, with exact values at every tested scale.
- `distribution_distance.csv`: exact pairwise/common-target probabilities and
  finite-set total variation distances.
- `mldsa_case.csv`: exact ideal fresh-challenge acceptances for the isolated
  ML-DSA `z`-norm layer. They are the denominators in the paper's classical-ROM
  freshness bound, not total ML-DSA signing probabilities.
- `mldsa_fiber.csv`: full-public-matrix rank--bucket certificates for that
  layer. `highbits_max_bucket` is `2*gamma2+1`; the zero-defect entropy and TV
  exponent are in bits; the defect budget assumes `q_H<=2^64` and target
  accepted-law distance `2^-128`. The classical-retry exponent includes the
  exact growing-table correction. The QROM fields use the independent-mask
  source O2H/restart bound with `q_0<=2^64`; they are not a global-XOF or full-signature
  QROM reduction. `random_matrix_bad_probability_log2` is the
  exact rectangular-rank PGF tail evaluated in the log domain under the
  independent-uniform NTT (ideal-XOF) model. Actual public keys use their
  directly computed NTT column-rank defect and require no such distributional
  assumption.
- `mldsa_acvp_key_audit.csv`: deterministic per-key audit of the official NIST
  ACVP FIPS 204 key-generation corpus. `rank_defect` is the sum of 256
  rectangular NTT-lane column defects after replaying `ExpandA` from the `rho`
  encoded in each public key; the pass columns compare it with the classical
  and QROM budgets in `mldsa_fiber.csv`.
- `block_asymptotic.csv`: literal fixed-block Ehrhart ratios and their powers.
- `performance.csv`: deterministic wall time and peak Python heap (`tracemalloc`),
  not process RSS.
- `sampler_benchmark.csv`: fixed-seed reference sampler timings; there is no
  constant-time claim.
- `manifest.json`: SHA-256 hashes of inputs and generated results, excluding
  the manifest itself.

The only randomized experiment is the sampler benchmark, with fixed seed
`20260802`. All mathematical tables are deterministic exact computations.
