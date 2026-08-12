# Verification independence matrix

The word "independent" is used only for implementations that do not share the
mathematical shortcut being checked. Exact arithmetic alone does not make two
checks independent.

| Claim or output | Primary route | Cross-check route | Shared component | Independence level |
|---|---|---|---|---|
| Cube overlap | closed coordinate product | point-by-point membership enumeration | Python integer arithmetic only | strong |
| Cross-polytope overlap | truncated bivariate dynamic program | direct enumeration of all points and both norm predicates | Python integer arithmetic only | strong |
| Arbitrary cross generating-function formula | sparse numerator plus binomial extraction | bivariate DP and, at smaller parameters, direct enumeration | public count definition only | two independent routes plus oracle |
| Hexagon counts | polynomial `3t^2+3t+1` and specialized block product | generic rational H-polytope enumerator with normals `(1,0),(0,1),(1,1)` | equivalent inequalities but different code paths | moderate/strong |
| Unequal-radius Lee majorization | two-coordinate parity-rectangle proof plus integer transfer theorem | exact bivariate DP checks 10,476 comparable partition/radius cases in dimensions 2--4, plus 137,214 parity-endpoint transitions across an expanded extreme-radius range | lens definition only | symbolic theorem plus exhaustive finite audit |
| Lee-radial convolution order | lower-orthant layer-cake theorem | finite-profile correlation routine checked against direct point summation; strict non-indicator profiles checked across partition classes | unequal-lens counter is shared in the layer-cake route | theorem-backed with an independent small direct oracle |
| Endogenous-challenge Lee envelope | radial majorization plus fresh-query coupling | componentwise audits of the radial order and the real/ideal coupling on finite examples | the combined corollary composes the two proved bounds | symbolic composition with independently tested components |
| Fixed-weight Lee extrema | majorization theorem, strict transfer slice, and midpoint closed formula | all partitions through dimension 6 and shift weight 10 | exact ball count | symbolic equality classification plus exhaustive finite audit |
| Maximal common subdistribution | pointwise-minimum optimization proof | exact nonuniform, translated-uniform, and disjoint-law examples | rational arithmetic only | theorem-backed examples |
| Classical-ROM freshness interface | lazy-sampling coupling and exact conditioning inequality | explicit small random-oracle table enumeration checks the accepted joint-law `eta/a` bound | total-variation definition | theorem plus independent finite-law audit |
| Adaptive-transcript fiber bound | conditional fiber union bound followed by expectation | exact rational weighted-case test | fixed-table fiber helper | theorem-backed exact arithmetic check |
| Adaptive restart composition | first-disagreement coupling weighted by ideal geometric survival | exact finite truncations, stationary closed form, growing-table series, and output-mixture tests | total-variation/coupling definitions only | symbolic theorem plus independent exact-series checks |
| Independent-source QROM freshness/retry | GHHM21 Theorem 1, equation (2), with one adaptive reprogramming plus a complete-instrument trace hybrid | rank--bucket min-entropy, classical finite-oracle checks, and a direct long-series upper-bound audit | the cited information-theoretic theorem fixes the exact constant and side-information interface | exact theorem specialization plus proved restart composition |
| General rank--bucket fiber theorem | row-rank basis, scalar bucket bound, and rank--nullity | exhaustive fibers of a small full-rank quantized map | finite-field map and quantizer definition only | symbolic theorem plus independent finite oracle |
| Common-core erosion | facet support-function evaluation | explicit intersection over all small `l1` shifts followed by set construction | shape predicate | moderate |
| Tilted `h*` erosion identity | binomial-basis substitution and stochastic-order proof | recovery of named-family `h*` vectors from Ehrhart values; exact ratio checks and Reeve-family likelihood-ratio tests | binomial arithmetic | theorem-backed identities across independent representations |
| Truncated-l1 count | sliding-window coefficient DP | exhaustive coordinate tuples for small parameters | set definition only | strong |
| Rank/unrank sampler | recursive completion counts | complete enumeration and inverse-rank round trips on small sets | rank and unrank share the completion counter | theorem-backed bijection; round trip is consistency, not fully independent |
| ML-DSA `z`-target factor | literal FIPS interval endpoints and Cartesian powering | endpoint-size tests and independently stored exact fractions | standardized parameter table | exact arithmetic and endpoint audit; not a full-loop probability |
| ML-DSA public-matrix fiber | full rectangular NTT-lane ranks and rank--bucket theorem | finite-field rank counts partition all small rectangular matrices; exceptional HighBits bucket is exhaustively checked | standardized `q`, `gamma1`, and `gamma2` | deterministic per-key theorem plus exact ideal-XOF rank PGF |
| NIST ACVP public-key audit | replay FIPS 204 `ExpandA`/`RejNTTPoly` from each encoded `rho` and row-reduce every NTT lane | first vector's `rho` is independently derived from its official seed by the FIPS key-generation SHAKE call; source JSON files are SHA-256 pinned | FIPS expansion specification | deterministic external-vector audit; not a probabilistic proof for all keys |
| Quasi-polynomial rows | Newton interpolation by residue class and holdout values | separate symbolic theorem where listed in the evidence column | counter supplies the data | finite fits are explicitly not proofs |
| First feasible scale | exhaustive integer scan with exact `Fraction` comparison | tests verify every prior failure and selected-scale success | family counter | moderate |

The 27 cross-shift classes for dimension four and `||u||_1<=6` are all
partitions of the integers 0 through 6 into at most four positive parts. The
counts are `1+1+2+3+5+6+9=27`. `results/cross_arbitrary.md` lists every
representative; signed coordinate permutations map every shift to one of them.
