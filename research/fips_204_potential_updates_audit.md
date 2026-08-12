# FIPS 204 potential-updates audit

Retrieved: 2026-08-02 (Asia/Shanghai)

Official source: <https://csrc.nist.gov/files/pubs/fips/204/final/docs/fips-204-potential-updates.xlsx>

Archived source file: `research/sources/fips-204-potential-updates-2026-08-02.xlsx`

SHA-256: `5bc93ce63bc647e6d1d456cb2d3a171426c15aca4a7a0e0edd40d08b7a34c793`

The workbook identifies itself as "Potential Updates (Errata)," was last
updated 2026-07-31, and states that the potential corrections are not official
changes and do not introduce new technical requirements. We checked all 12
listed issue rows (workbook rows 16--27) against the quantities used in the
ML-DSA case study.

## Result relevant to this paper

- No listed item changes the ML-DSA parameter values `ell`, `tau`, `eta`,
  `beta`, or `gamma1` used by the case study.
- No listed item changes the `ExpandMask` source interval or the strict
  endpoint convention in the `z`-norm rejection used by the case study.
- Workbook row 27 (the twelfth issue row, dated 2026-07-31 and located at
  "Sec. 4 and App. C") changes the full signing-loop repetition values used
  only as an external comparison: 4.25, 5.10, and 3.85 in the 2024 PDF become
  4.36, 5.14, and 3.91 in the potential correction. The code, raw results, and
  paper therefore preserve both sets and label the latter as a potential
  update rather than an official amendment.

## Disposition of all issue rows

The other rows concern NTT notation; message-variable notation; broken links
and typography; an ordering typo in the challenge hash input; failure-symbol
notation; polynomial-vector wording and function names; references to internal
algorithms; the Montgomery-reduction appendix; a Boolean return value; and a
tighter `UseHint` output bound. None enters the isolated interval-product
calculation.
