# Quantitative Lee rearrangement on $\mathbb Z^d$: research specification

Status: approved design, 11 August 2026.  This document is the implementation
contract for the geometry-first revision now targeted to DCG.

## 1. Understanding summary

- The paper is a quantitative theory of fixed-shell Lee rearrangement on
  $\mathbb Z^d$,
  not a cryptographic manuscript with a geometric lemma.
- Theorem 5.3 is the starting order theorem.  The revision must add an exact
  local transfer law, strictness/equality classification, and a quantitative
  stability result on the majorization lattice.
- Computational work is a discovery and falsification engine.  Only formulas
  that receive exact proofs become theorems; fitted patterns remain explicitly
  labelled conjectures.
- The first two pages of the Introduction discuss only lattice
  cross-covariograms, Lee geometry,
  translation composition, majorization, stability, and equality.
- The main text contains a single cryptographic application section of about
  one to two pages.  QROM, rank-PGF, ACVP, and full oracle details remain
  available as an appendix or Online Resource.
- There is no invented page cap.  The main PDF remains as short as the complete
  geometric argument permits.

## 2. Assumptions and non-functional requirements

- All discovery calculations use exact integer or rational arithmetic.
- Every new counter, chamber classifier, and graph construction receives an
  independent small-parameter direct-enumeration oracle.
- Training ranges used to infer a formula and holdout ranges used to challenge
  it are recorded separately.
- No Monte Carlo evidence is used to promote a statement to theorem status.
- The existing reproducibility workflow, SHA-256 manifest, editable Draw.io
  sources, and Windows/POSIX runners remain supported.
- Complexity claims are output-sensitive and parameterized honestly.  No
  polynomial-time claim in variable dimension is permitted without proof.
- No stronger ML-DSA, SHAKE, QROM, extraction, or unforgeability claim is
  introduced.

## 3. Mathematical deliverables

### 3.1 Exact balancing calculus

For

\[
 \mathcal L_{p,q}^{(2)}(a,b)
 =|\{(x,y)\in\mathbb Z^2:
     |x|+|y|\le p,
     |x+a|+|y+b|\le q\}|,
\]

write `R=a+b`, `D=a-b`, and let

\[
 n_\varepsilon(p,q;c)
 =|[-p,p]\cap[-c-q,-c+q]\cap(2\mathbb Z+\varepsilon)|.
\]

The first required theorem is the exact nonnegative increment

\[
 \Delta_{p,q}(R,D)
 =\mathcal L_{p,q}^{(2)}(a-1,b+1)
  -\mathcal L_{p,q}^{(2)}(a,b)
 =\sum_{\varepsilon=0}^1 n_\varepsilon(p,q;R)
   \bigl(n_\varepsilon(p,q;D-2)-n_\varepsilon(p,q;D)\bigr).
\]

The bracketed differences are to be proved to lie in `{0,1}`.  Endpoint
switches and parity residues yield a piecewise quasi-polynomial chamber
description and an if-and-only-if local zero-increment criterion.

### 3.2 High-dimensional transfer law

For a transfer in coordinates `i,j`, the remaining coordinates define an
exact bivariate residual-norm histogram.  The high-dimensional increment is
the convolution of that histogram with the two-dimensional transfer kernel.
This is the discrete rearrangement differential law behind global
Schur-concavity.

### 3.3 Equality and stability on the majorization lattice

At fixed Lee weight, partitions are vertices and Robin Hood transfers are
directed edges weighted by the exact lens increment.  The revision must
determine:

- the zero-weight edge set `E` and its equality components;
- the minimum positive shell increment `kappa_{d,t,s}`;
- the majorization distance `d_M`, including its relation to half the sorted
  `l1` distance;
- a proved stability inequality in the active equal-radius regime;
- exact or proved lower-bound formulas for `kappa`, separated by parity where
  necessary.

The always-valid integer bound `J_t(v)-J_t(u) >= d_M(u,v)` is an acceptable
baseline only after all hypotheses are stated.  The main target is a sharper
shell-dependent constant derived from the transfer calculus.  For unequal
radii, stability must explicitly account for zero-gap chambers rather than
asserting an impossible universal positive constant.

### 3.4 Lee-radial rearrangement and equality theory

Using

\[
 K_H(u)=\sum_{p,q}\Delta_{12}H(p,q)J_{p,q}(u),
\]

with nonnegative mixed differences, prove an equality criterion: equality of
two comparable shifts holds exactly when every positively weighted lens term
lies in its corresponding equality chamber.  Product-profile corollaries must
state how flat active shells create degeneracy.  This is the final main-text
geometry theorem; general norms and arbitrary lattices are not required.

## 4. Computational discovery and falsification

The paper presents three discovery layers, not five independent projects.

### Experiment A: computational classification of transfer chambers

- Enumerate `(p,q,R,D,epsilon)` using exact parity intervals.
- Record endpoint switches, parity cells, zero increments, and positive
  increments.
- Compare the kernel with an independent direct two-dimensional lens oracle.
- Produce a compact chamber table or schematic; raw scans remain in the
  artifact.

### Experiment B: global stability discovery

- Enumerate partition shells and weighted majorization edges.
- Report the pair `(kappa,E)`, not `kappa` alone.
- Infer candidate formulas in binomial/Lee-ball bases on a declared discovery
  range, then challenge them on disjoint holdouts.
- Build small equality graphs whose zero-weight components visually expose
  the classification.

### Experiment C: functional equality and boundary tests

- Test mixed-difference supports and radial profiles with deliberately flat
  shells against the proposed equality criterion.
- Use q-ary Lee spaces only as a falsification boundary for wrap-around.
  Unless a short uniform theorem emerges, q-ary data stays in the appendix or
  limitations and does not become a new main line.

New explanatory diagrams must have an editable source under version control:
main-text figures are generated by `paper/makefigs.py`, and the Online Resource
diagram keeps its Draw.io XML.  Data-heavy
evidence should use tables rather than screenshots or decorative plots.

## 5. Symbolic chamber algorithm

The algorithm is a supporting mathematical tool, not a coequal main-text
theme.  It belongs in an appendix or a short methods subsection and must:

- evaluate the parity-kernel formula exactly;
- enumerate endpoint/residue chambers;
- construct weighted majorization graphs at fixed shell;
- emit machine-readable formulas, zero-edge data, and holdout audits.

Permitted complexity claims include fixed-dimension and output-sensitive
enumeration, and evaluation polynomial in `log p` and `log q` when a sparse
numerator/chamber is already supplied.  The existing pseudopolynomial DP
remains the independent computational route.

## 6. Approved main-text architecture

1. **Introduction.**  Two geometry-only pages: Lee-ball cross-covariograms, same-shell
   non-orbit translations, majorization, quantitative deficit, and equality.
2. **Related geometric work.**  Lee codes, discrete covariograms,
   Schwarz/Riesz rearrangement, and majorization stability.
3. **Lee-ball lenses and exact enumeration.**  Definitions, lattice-point shapes,
   and the exact generating formula.
4. **Exact balancing calculus.**  Transfer kernel, parity chambers, and local
   equality classification, with Experiment A integrated as discovery
   evidence.
5. **Global majorization, stability, and equality.**  Strengthened Theorem
   5.3, `(kappa,E)`, equality graphs, and Experiment B.
6. **Lee-radial rearrangement and equality theory.**  Functional equality
   theorem and concise boundary statement.  The symbolic chamber algorithm
   is not part of the section title.
7. **Finite rejection application.**  At most five pages: geometry-to-
   optimization translation, a compact classical freshness/retry interface,
   one combined ML-DSA strict-z certificate table, and scope boundary.
8. **Conclusion.**  Quantitative rearrangement outcomes first; application
   second.

Appendices contain the symbolic chamber algorithm, full transfer tables and
proof details not needed for the main chain, QROM, rank-PGF, ACVP audit, full
oracle conventions, and reproducibility metadata.

## 7. Falsification gates

- A fitted stability formula that fails a holdout is not patched silently; it
  is replaced by the correct chamber split or a proved lower bound.
- If the only uniform shell constant is 1, the paper emphasizes the exact
  path calculus and equality classification rather than overstating
  stability strength.
- If radial equality has cancellation outside the nonnegative mixed-
  difference cone, the theorem remains restricted to that cone.
- If q-ary wrap-around produces irregular counterexamples, only the first
  obstruction and no-wrap boundary are reported.
- A general unconditional-norm theorem is included only after at least one
  non-Lee family satisfies a non-tautological transfer criterion with proof.

## 8. Decision log

1. **Paper identity:** quantitative rearrangement of Lee-ball
   cross-covariograms on $\mathbb Z^d$, with rejection sampling as a final
   application.  This is the identity used for DCG.
2. **Novelty criterion:** at least one new proved quantitative theorem or
   complete equality classification; additional numerical examples alone are
   insufficient.
3. **Primary route:** exact transfer kernel, global stability/equality, and
   radial equality.  q-ary and general-norm extensions are conditional.
4. **Experiment organization:** local structure, global stability, then
   equality/boundary.  Raw scanning is artifact material, not the paper's
   narrative.
5. **Crypto budget:** one main-text application section of about one to two
   pages.  Detailed cryptographic machinery is retained in an appendix or
   Online Resource.
6. **Algorithm positioning:** supporting appendix tool with fixed-dimension,
   output-sensitive claims; no unsupported variable-dimension polynomial
   claim.
7. **Section 6 title:** `Lee-radial rearrangement and equality theory`.
   `Symbolic chambers` was removed from the title to keep mathematical and
   computational contributions conceptually distinct.

## 9. Implementation order

1. Build independent local-kernel and direct-enumeration audits.
2. Derive and prove the local chamber/equality theorem.
3. Build weighted partition graphs and infer falsifiable stability formulas.
4. Prove the strongest surviving stability theorem and equality structure.
5. Prove and audit the radial equality theorem.
6. Rewrite the manuscript geometry-first and compress crypto to the approved
   budget.
7. Add or revise Draw.io diagrams, regenerate the artifact, compile, and run
   the complete verification suite.
