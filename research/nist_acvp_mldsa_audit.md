# NIST ACVP ML-DSA key audit source record

Retrieved 2026-08-10 from the official NIST `usnistgov/ACVP-Server`
repository, directory `gen-val/json-files/ML-DSA-keyGen-FIPS204`.

- Prompt URL: <https://raw.githubusercontent.com/usnistgov/ACVP-Server/master/gen-val/json-files/ML-DSA-keyGen-FIPS204/prompt.json>
- Expected-results URL: <https://raw.githubusercontent.com/usnistgov/ACVP-Server/master/gen-val/json-files/ML-DSA-keyGen-FIPS204/expectedResults.json>
- Local prompt: `research/sources/nist-acvp-mldsa-keygen-prompt.json`
- Prompt SHA-256: `43e81ad820e495dbcad086fe27c1008393a8c32100bbbff77c558c3f06dcefef`
- Local expected results: `research/sources/nist-acvp-mldsa-keygen-expected.json`
- Expected-results SHA-256: `361f47ca19d592adcc66ff2cb591686ad785fea157b295648738bed6921a68df`

The executable audit parses `rho` from every public key, follows FIPS 204
`ExpandA` and `RejNTTPoly`, forms the 256 rectangular NTT lanes, and computes
the deterministic total column-rank defect. It does not use the secret keys.
The result table and all per-key `rho` hashes are stored in
`results/mldsa_acvp_key_audit.md` and `.csv`.
