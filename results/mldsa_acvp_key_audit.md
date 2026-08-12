# Official NIST ACVP public-key rank-defect audit

Source: `usnistgov/ACVP-Server`, `ML-DSA-keyGen-FIPS204`, retrieved 2026-08-10.  The archive contains the exact prompt and expected-results JSON files.

- prompt SHA-256: `43e81ad820e495dbcad086fe27c1008393a8c32100bbbff77c558c3f06dcefef`
- expected-results SHA-256: `361f47ca19d592adcc66ff2cb591686ad785fea157b295648738bed6921a68df`

For every public key, the audit parses the first 32 bytes as `rho`, runs FIPS 204 `ExpandA`/`RejNTTPoly`, forms all 256 rectangular NTT lanes, and sums their column-rank deficiencies.

| set | vectors | min defect | max defect | classical budget | QROM budget | pass/pass |
|---|---:|---:|---:|---:|---:|---:|
| ML-DSA-44 | 25 | 0 | 0 | 51 | 27 | 25/25 |
| ML-DSA-65 | 25 | 0 | 0 | 272 | 240 | 25/25 |
| ML-DSA-87 | 25 | 0 | 0 | 400 | 368 | 25/25 |

This is an audit of the deterministic rank certificate on a fixed official corpus, not a statistical proof about all ML-DSA keys.  The per-key rows, including a hash of each `rho`, are in the companion CSV.
