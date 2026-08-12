# Published protocol baseline (not independently regenerated)

Last checked: 2026-08-02.

This ledger prevents geometric response-set measurements from being confused
with complete signature sizes.  The byte counts below are transcribed from the
authors' CRYPTO 2024 presentation; this repository did **not** regenerate the
complete protocol encodings or security estimates.

| Security target (bits) | HAETAE signature (bytes) | PATRONUS signature (bytes) | Dilithium signature (bytes) | PATRONUS expected rejects |
|---:|---:|---:|---:|---:|
| 120 | 1,463 | 2,070 | 2,420 | 3 |
| 180 | 2,337 | 2,575 | 3,293 | 4.250 |
| 260 | 2,908 | 3,721 | 4,595 | 3 |

The same presentation reports PATRONUS verification keys of 832, 1,152, and
1,632 bytes for the three targets.  These values are useful context, but they
are not directly comparable to `ideal_bits` or `fixed_bits` in
`common_core.csv`: those columns encode only a sampled response set, whereas a
signature also contains challenges, seeds, hints, auxiliary commitments, and
scheme-specific framing.

An earlier CWI slide deck labelled a tentative variant “PATRONUS2” and listed
1,869/2,398/3,459-byte signatures.  Because its slide explicitly said that
parameters could still vary, it is recorded here only as superseded
pre-publication evidence and is not used as the baseline.

Sources:

- [CRYPTO 2024 presentation, slide 21](https://iacr.org/submit/files/slides/2024/crypto/crypto2024/529/slides.pdf)
- [Earlier CWI slide deck, slide 38](https://hbambury.github.io/CWI_slides.pdf)
- [CRYPTO 2024 paper](https://eprint.iacr.org/2024/411.pdf)

## Reproduction status

| Quantity | Status in this repository |
|---|---|
| Complete scheme signature bytes | Published baseline only |
| Complete ROM/QROM security reduction | Out of scope |
| Exact finite-dimensional set cardinality | Independently computed |
| Exact pairwise overlap | Independently computed |
| Exact common-core acceptance | Independently computed |
| Expected geometric retries | Independently computed as reciprocal acceptance |
| Maximum response norm for implemented families | Independently computed/certified |
| Ideal enumerative and fixed-width response bits | Independently computed |

