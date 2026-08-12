# First exact findings

These statements separate experimentally certified identities from the
cryptographic interpretation. The implementation was first checked against
point-by-point brute force in dimensions at most three. The identities below
are then checked over the parameter ranges stated in the test suite.

## Radius-two shift classes

Write

\[
L_d(t)=|\{x\in\mathbb Z^d:\|x\|_1\le t\}|
=\sum_{j=0}^{\min(d,t)}2^j\binom dj\binom tj.
\]

For the integer cross-polytope and `t >= 1`, the experiments identify

\[
N_d(t,2e_1)=L_d(t-1),
\]

and, for `d >= 2`,

\[
N_d(t,e_1)=N_d(t,e_1+e_2)=L_d(t)-L_{d-1}(t).
\]

The first identity has a short exact explanation: after translating the first
coordinate by one, the two inequalities reduce to
`|x_1| + sum_{i>1}|x_i| <= t-1`. The second follows by slicing; a unit shift
removes exactly the slice counted by `L_{d-1}(t)`, and the two-dimensional
`(1,1)` slice has the same overlap as the `(1,0)` slice.

Consequently, among every integer shift with `||u||_1 <= 2`, the concentrated
shift `2e_1` is the worst observed class, giving the exact candidate

\[
\min_{\|u\|_1\le2} A_{\ell_1}(t,u)=\frac{L_d(t-1)}{L_d(t)}.
\]

The test suite verifies these identities for `1 <= d <= 6`, `1 <= t <= 10`,
and verifies the minimum over all shifts for `1 <= d <= 6`, `1 <= t <= 8`.

For the hexagonal block

\[
H_t=\{(x,y)\in\mathbb Z^2:
\max(|x|,|y|,|x+y|)\le t\},\qquad |H_t|=3t^2+3t+1,
\]

the direction-sensitive formulas detected and checked for `1 <= t < 30` are

\[
\begin{aligned}
N_H(t,(2,0))&=3t^2-t-1,\\
N_H(t,(1,1))&=3t^2-t,\\
N_H(t,(1,0))=N_H(t,(1,-1))&=3t^2+t.
\end{aligned}
\]

For every tested Cartesian power, concentrating the shift as `(2,0)` in one
block is again worse than distributing two unit shifts. Hence the block
product's radius-two worst-case acceptance candidate is independent of the
number of blocks:

\[
\min_{\|u\|_1\le2} A_{H^m}(t,u)
=\frac{3t^2-t-1}{3t^2+3t+1}.
\]

## Baseline comparison

Under a common upper bound on `||z||_2` and worst case over
`||u||_1 <= 2`, the cube has the highest geometric acceptance in all 27
generated rows (`n in {2,4,8}`, norm budget in `{8,12,16}`); hexagonal blocks
are second and cross-polytopes third. This is evidence against the naive idea
that a smaller `l1`-shaped response region automatically improves rejection
behavior.

The conclusion is deliberately narrow. It does not yet compare concrete
encodings or samplers, and simple intersection conditioning does not replace
the randomized acceptance rule required by a full Fiat--Shamir-with-Aborts
security argument.

## Next mathematical target

Turn the slicing arguments into formal all-dimension proofs, then generalize
from shift radius two to arbitrary fixed integer shifts. The computational
representation already supplies exact bivariate generating functions and can
test any proposed formula before proof writing.

