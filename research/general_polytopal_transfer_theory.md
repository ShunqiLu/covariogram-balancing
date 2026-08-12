# General polytopal transfer theory: proof memorandum

Date: 2026-08-11

This memorandum isolates the part of the Lee argument that does **not** depend
on Lee balls.  The main conclusion is stronger than the initially proposed
"sign phase transition": inside the class of permutation-invariant convex
bodies the sign cannot change at all.  The cross-polytope, every symmetric
gauge polytope, Euclidean balls, capped Lee balls, and the cube all have the
same balancing direction.  What changes across the class is the size and the
strictness/equality pattern of the increment.  A genuine sign reversal first
appears when diagonal convexity or coordinate symmetry is lost.

## 1. The geometric condition

For a finite set `A \subseteq Z^d`, coordinates `i != j`, residual coordinate
vector `z \in Z^{d-2}`, and coordinate sum `r \in Z`, define the difference
fiber

\[
 I_A^{ij}(z,r)=\left\{\delta\in r+2\mathbb Z:
 \left(z_1,\ldots,\frac{r+\delta}{2},\ldots,
 \frac{r-\delta}{2},\ldots,z_{d-2}\right)\in A\right\}.
\]

Call `A` **exchange-fiber convex** if every such fiber is empty or a centered
interval in the parity lattice `r+2Z`.

This is a verifiable geometric condition, not a restatement of the desired
cross-covariogram inequality.  If `K \subset R^d` is convex and invariant under
coordinate permutations, then `A=K\cap Z^d` is exchange-fiber convex: fixing
the residual coordinates and `x_i+x_j=r` cuts `K` in a real interval, and the
transposition `i <-> j` maps `delta` to `-delta`, so that interval is centered.
No rationality or lattice-vertex assumption is needed.

For a signed-composition statement, assume in addition that `K` is
unconditional.  Equivalently, it is invariant under the full hyperoctahedral
group.  Then its lattice cross-covariogram depends only on the signed
permutation orbit of the shift.

## 2. Atomic interval lemma

Let `I` and `J` be finite centered intervals in parity lattices, and suppose
that `J-D` lies in the same parity lattice as `I`.  For every integer `D>=2`,

\[
 \epsilon_{I,J}(D)
 =|I\cap(J-(D-2))|-|I\cap(J-D)|\in\{0,1\}.
\]

Proof: scale the common step-two lattice to `Z`.  The second interval moves one
lattice unit toward the center of the first and does not pass it.  An interval
intersection can gain at most its new right endpoint.  If its moving left
endpoint causes the loss of one point, centeredness and the order of the two
centers force the right endpoint to be active as well, so that a new point is
gained simultaneously.  Hence the net change is zero or one, never negative.
The argument is unchanged when either real fiber endpoint is nonintegral:
flooring to the appropriate parity lattice still produces an integer interval.

The following endpoint proof is useful in a referee-facing version.  Write the
two intervals, after scaling, as integer intervals `[A_-,A_+]` and
`[B_-,B_+]`, with the center of the second weakly left of the first.  Replacing
`B` by `B+1` changes

\[
 \min(A_+,B_+)-\max(A_-,B_-)+1
\]

after truncation at zero.  The upper minimum can rise by at most one and the
lower maximum can rise by at most one.  Whenever the latter rises, symmetry
and the center ordering imply that the former also rises; therefore the net
change is `0` or `1`.  Empty and singleton intervals are included.

There is also a one-line exact exposure criterion.  Write the nonempty
physical parity intervals as

\[
 I=\{-A,-A+2,\ldots,A\},\qquad
 J=\{-B,-B+2,\ldots,B\},
\]

where the parities satisfy `A=B+D (mod 2)`.  Translation by two deletes only
the old left endpoint `-B-D` and adds only the new right endpoint `B-D+2`.
Consequently

\[
 \epsilon_{I,J}(D)
 =\mathbf 1\{|B-D+2|\le A<B+D\}.                 \tag{A}
\]

Formula (A) proves `{0,1}` and gives the exact zero-exposure/equality chamber
without any generic-position assumption.

## 3. Exact transfer theorem for general convex bodies

Let `K,L \subset R^d` be bounded convex sets invariant under all coordinate
permutations, and put

\[
 G_{K,L}(u)=\bigl|\{x\in Z^d:x\in K,\ x+u\in L\}\bigr|.
\]

Fix `u=(a,b,w)` with `a>=b+2`, and set

\[
 u'=(a-1,b+1,w),\qquad R=a+b,\qquad D=a-b.
\]

Then the exact atomic decomposition is

\[
 G_{K,L}(u')-G_{K,L}(u)
 =\sum_{z\in Z^{d-2}}\sum_{r\in Z}
 \epsilon_{I_K(z,r),\,I_L(z+w,r+R)}(D),
\]

where a shifted interval is interpreted in the common parity lattice.  Every
summand belongs to `{0,1}`.  Consequently

\[
 G_{K,L}(u')\ge G_{K,L}(u).
\]

### Proof

Fix the residual lattice point `z` and put

\[
 r=x_i+x_j,\qquad \delta=x_i-x_j.
\]

The map `(x_i,x_j) -> (r,delta)` is a bijection from `Z^2` to
`{(r,delta):r=delta (mod 2)}`.  Membership of `x` in `K` says
`delta in I_K(z,r)`.  Membership of `x+u` in `L` says

\[
 \delta+D\in I_L(z+w,r+R),
\]

because the translated coordinate sum and difference are `r+R` and
`delta+D`.  Thus this slice contributes

\[
 |I_K(z,r)\cap(I_L(z+w,r+R)-D)|.
\]

The balancing transfer fixes `R`, replaces `D` by `D-2`, and changes no
residual coordinate.  Subtracting and applying the atomic interval lemma gives
the displayed formula and its sign.

### Scope checks

* `K` and `L` may be different.  Hence unequal Lee radii are already covered
  by `K=pC_d` and `L=qC_d`; no equal-radius assumption enters the proof.
* Compact convex bodies are the clean standard statement.  More generally,
  bounded convex sets suffice.  Closedness, nonempty interior, rational facets,
  and lattice vertices are not used.  Boundedness is what makes the count
  finite.  Lower-dimensional and empty fibers cause no problem.
* Boundary points are handled exactly by intersection with the appropriate
  parity lattice.  Open or half-open bounded convex sets also work if desired,
  but compact bodies avoid irrelevant conventions.
* Only transposition invariance is needed for the positive-orthant local move.
  Hyperoctahedral invariance is needed to identify arbitrary signed shifts with
  their absolute coordinate compositions.

## 4. Global majorization, equality, and stability

Let `K,L` be hyperoctahedrally invariant compact convex sets.  If
`|u|^downarrow` majorizes `|v|^downarrow` and `||u||_1=||v||_1`, then

\[
 G_{K,L}(u)\le G_{K,L}(v).
\]

Indeed, signed permutations reduce to nonnegative decreasing shifts, and every
integer majorization is a chain of unit Robin Hood transfers.  The local
theorem applies to every edge.

The atomic formula also gives a complete equality test.  A transfer edge has
zero weight if and only if every residual/sum fiber has zero interval exposure.
For comparable `u,v`, equality holds if and only if every edge on a (hence on
every) monotone transfer chain between them is a zero-exposure edge.

On a shell on which all nontrivial transfer edges are strict, define

\[
 \kappa_{K,L,s}=\min_e\bigl(G_{K,L}(e^+)-G_{K,L}(e^-)\bigr).
\]

It is a positive integer, and

\[
 G_{K,L}(v)-G_{K,L}(u)
 \ge \kappa_{K,L,s}\,d_M(u,v).
\]

Thus the universal theorem supplies the exact order and equality mechanism.
The evaluation of the sharp constant is a third, family-specific layer.  For
Lee balls that layer is the central residual box plus signed-face extremality;
for cubes it is a product-compression argument, given next.

## 5. Cube: exact kernel and sharp shell constant

Let `Q_c=[-c,c]^d`, `c>=1`, and put `H=2c+1`.  For a nonnegative integer shift
`u` with every `u_i<=2c`,

\[
 G_{Q_c,Q_c}(u)=\prod_{i=1}^d(H-u_i).
\]

For a transfer on coordinates `(a,b)` with `D=a-b>=2`,

\[
 G(u')-G(u)
 =(D-1)\prod_{k\ne i,j}(H-u_k).
\]

This follows from

\[
 (H-a+1)(H-b-1)-(H-a)(H-b)=a-b-1.
\]

Consequently every nontrivial edge is strict on every fully active shell
`2<=s<=2c`.  Let `kappa^square_{d,c,s}` be the minimum edge increment there.
Then

\[
 \kappa^\square_{2,c,s}=
 \begin{cases}
 1,&s\ \text{even},\\
 2,&s\ \text{odd},
 \end{cases}
\]

and, for `d>=3`,

\[
 \boxed{\ \kappa^\square_{d,c,s}
 =H^{d-3}(H-s+2).\ }
\]

### Proof of sharpness for `d>=3`

Write `R=a+b` and let the untouched coordinates have sum `q=s-R`.  Since
`s<=H-1`, also `q<=H-1`.  Repeatedly using

\[
 (H-x)(H-y)\ge H(H-x-y)
\]

concentrates the untouched mass and gives

\[
 \prod_{k\ne i,j}(H-u_k)
 \ge H^{d-3}(H-q)=H^{d-3}(H-s+R).
\]

Since `R>=D>=2`,

\[
 (D-1)(H-s+R)\ge H-s+2.
\]

Equality requires `D=R=2` and concentration of the residual mass.  It is
attained by the coordinate-labelled edge

\[
 (2,0,s-2,0^{d-3})\longrightarrow(1,1,s-2,0^{d-3}),
\]

or, after sorting,

\[
 \operatorname{sort}(s-2,2,0^{d-2})
 \longrightarrow
 \operatorname{sort}(s-2,1,1,0^{d-3}).
\]

For `d=2`, there is no residual product.  Since `D` has the same parity as
`s`, the smallest admissible `D` is `2` for even `s` and `3` for odd `s`,
giving `1` and `2`.  Shells `s=0,1` contain no nontrivial transfer edge, so a
positive edge minimum is undefined and the stability assertion is vacuous.
For `s>2c`, the whole shell is no longer coordinatewise active; zero-overlap
chambers appear, and the boxed formula is not asserted.

The cube therefore supplies a fully explicit non-Lee sharp stability theorem,
with the same axial residual extremizer but a different constant.

## 6. Cross-polytope-to-cube interpolation: no sign transition, but an exact kink

Consider the capped Lee polytopes

\[
 P_{t,c}^{(d)}=\{x\in R^d:\|x\|_1\le t,\ \|x\|_\infty\le c\}.
\]

They are hyperoctahedrally invariant and convex.  They equal the cross-polytope
when `t<=c`, and equal the cube when `t>=dc`.  Hence the general theorem proves
that every transfer increment is nonnegative throughout the entire
interpolation.  A sign phase transition is impossible in this convex symmetric
class.

There is nevertheless an exact **magnitude crossover**.  In dimension two, for
`1<=t<=2c`, let `A=P_{t,c}^{(2)}\cap Z^2`.  For the atomic edge
`(2,0)->(1,1)`,

\[
 |A\cap(A-(1,1))|-|A\cap(A-(2,0))|
 =\min\{2t-1,\ 4c-2t+1\}.
\]

Under `(x,y)->(r,w)=(x+y,x-y)`, the body becomes

\[
 [-t,t]^2\cap\{|r|+|w|\le2c\}
\]

on the parity lattice.  For fixed `r`, its effective vertical radius is the
largest integer not exceeding `min(t,2c-|r|)` with parity `r`.  The `D=2` to
`D=0` move contributes one exactly when the effective radii at `r` and `r+2`
coincide.  There are `2t-1` such fibers in the uncapped Lee regime and
`4c-2t+1` in the cap-controlled regime.  This proves the formula.

The profile is tent-shaped: it is governed first by the Lee boundary and then
by the cube cap, with a combinatorial kink between the two branches, but it
never changes sign.  This is a precise replacement for an unsupported "phase
transition" claim.

## 7. Why the hypotheses are real

1. **Lose diagonal convexity:** the unconditional, permutation-invariant finite
   set

   \[
   A=\{(0,0),(\pm1,0),(\pm2,0),(0,\pm1),(0,\pm2)\}
   \]

   is a nonconvex coordinate cross.  Direct counting gives

   \[
   |A\cap(A-(2,0))|=3,
   \qquad |A\cap(A-(1,1))|=2.
   \]

   Thus balancing reverses the desired sign.  Its difference fibers have gaps.

2. **Lose permutation symmetry:** for the convex unconditional rectangle
   `[-5,5] x [-1,1]`, the same transfer gives

   \[
   G(2,0)=9\cdot3=27,
   \qquad G(1,1)=10\cdot2=20.
   \]

   Hence convexity alone does not determine the sign.

These examples locate the genuine structural boundary: centered interval
fibers, not the particular Lee gauge.

## 8. Relation to prior work and safe novelty language

Marshall and Olkin proved in 1974 that convolution preserves Schur-concavity
for suitable functions on `R^d`:

* A. W. Marshall and I. Olkin, *Majorization in Multivariate Distributions*,
  Ann. Statist. 2 (1974), 1189--1200,
  DOI: 10.1214/aos/1176342873.

For continuous permutation-invariant convex bodies, Schur-concavity also
follows from standard concavity properties of cross-covariograms.  Therefore
the broad order statement should **not** be advertised as if no continuous or
functional antecedent existed.

The defensible contribution is the parity-exact lattice mechanism:

* an exact finite sum of `{0,1}` exchange-fiber exposures for each unit
  transfer;
* exact zero-exposure equality conditions;
* integer transfer-graph stability;
* family-specific sharp evaluation (Lee central sections and, independently,
  the cube product theorem);
* the exact capped-Lee crossover and explicit counterexamples at the geometric
  boundary.

A safe positioning sentence is:

> The order component is a parity-resolved lattice analogue of convolution
> preservation for Schur-concave functions; the new content is the exact
> atomic exposure formula, its equality and stability consequences, and the
> sharp evaluation of the resulting transfer weights for concrete polytope
> families.
