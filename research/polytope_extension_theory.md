# A transfer theory beyond Lee balls

This note records a proof-level extension suggested by the exact scans in
`polytope_transfer_phase_scan.py`.  It is deliberately kept outside the main
manuscript until its terminology and literature context have been audited.

## 1. The combinatorial hypothesis actually used by balancing

Let (A\subset\mathbb Z^d) be finite.  Fix two coordinates (i<j), a
residual vector (z\in\mathbb Z^{d-2}), and an integer (r).  Define its
diagonal fiber

\[
 W_A(i,j;z,r)
 =\{x_i-x_j:x\in A,\ x_{-\{i,j\}}=z,\ x_i+x_j=r\}.
\]

Call (A) **centered-diagonal-interval (CDI)** if it is invariant under signed
coordinate permutations and every nonempty such fiber is

\[
 \{-m,-m+2,\ldots,m-2,m\}
 \qquad (m\equiv r\pmod2).
\]

This is the exact discrete property needed by a Robin Hood transfer.  It is
weaker than asking that (A) be the lattice points of a convex body.

### Proposition 1 (convex hyperoctahedral bodies are CDI)

If (P\subset\mathbb R^d) is convex and invariant under signed coordinate
permutations, then (P\cap\mathbb Z^d) is CDI.

**Proof.**  After fixing (z) and (x_i+x_j=r), convexity makes the remaining
intersection with that affine line an interval.  Swapping coordinates (i,j)
maps (w=x_i-x_j) to (-w), so the interval is centered.  The integer points
on the line have (w\equiv r\pmod2) and spacing two.  Hence they are precisely
one centered parity interval.  □

Thus the class includes, with no change in the proof:

- cross-polytopes and cubes;
- capped cross-polytopes
  \(\{\|x\|_1\le T,\ \|x\|_\infty\le R\}\);
- Minkowski sums (aB_1+bB_\infty);
- lattice points in (\ell_p)-balls, (1\le p\le\infty);
- ordered-weight (\ell_1) balls and intersections of symmetric-gauge balls;
- any pair of different convex hyperoctahedral bodies, not merely two scales
  of one body.

## 2. Universal exact transfer kernel

For finite sets (A,B\subset\mathbb Z^d), write

\[
 g_{A,B}(u)=|A\cap(B-u)|
 =|\{x\in A:x+u\in B\}|.
\]

Take (u_i=a\ge b+2=u_j+2), put (R=a+b), (D=a-b), and set

\[
 u'=u-e_i+e_j.
\]

For a residual vector (z=x_{-\{i,j\}}), the right-hand slice has residual
(z+u_{-\{i,j\}}).  Directly from the definitions,

\[
\begin{aligned}
g_{A,B}(u')-g_{A,B}(u)
=\sum_{z,r}\Big(&
|W_A(z,r)\cap(W_B(z+u_{-ij},r+R)-(D-2))|\\
&-|W_A(z,r)\cap(W_B(z+u_{-ij},r+R)-D)|\Big).
\end{aligned}
\tag{UF}
\]

Here (S-c=\{w-c:w\in S\}).  When (A,B) are CDI, both sets inside each
intersection are intervals in the same coset of (2\mathbb Z).  Moving the
center of the second interval from (-D) to (-(D-2)), one lattice step toward
zero, cannot reduce its overlap with the interval centered at zero.  It can
add at most one lattice point.  Consequently every bracket in (UF) belongs to
(\{0,1\}).

More explicitly, if the two nonempty physical fibers are

\[
 I=\{-A,-A+2,\ldots,A\},\qquad
 J=\{-B,-B+2,\ldots,B\},
\]

with the parity needed for (J-D) and (I) to lie in the same coset, then
the bracket is exactly

\[
 \mathbf 1\{|B-D+2|\le A<B+D\}.
\tag{Exposure}
\]

Indeed, translating (J-D) by two deletes only its old left endpoint and
adds only its new right endpoint; centeredness makes a possible deletion
occur only when the new endpoint is also admitted.  Formula (Exposure) is a
closed equality criterion for every atomic fiber.

### Theorem 2 (hyperoctahedral lattice cross-covariogram majorization)

If (A,B\subset\mathbb Z^d) are CDI, then

\[
 u\succeq v,\qquad \|u\|_1=\|v\|_1
 \quad\Longrightarrow\quad
 g_{A,B}(u)\le g_{A,B}(v),
\]

where the comparison is between the sorted absolute translation
compositions.  For one transfer, equality holds exactly when every fiber
bracket in (UF) is zero.

**Proof.**  Formula (UF) and the centered-interval observation prove one
Robin Hood step.  Signed-permutation invariance makes the cross-covariogram a
function of the sorted absolute composition.  The integer transfer theorem
for majorization then gives the global statement.  The equality assertion is
termwise because all brackets are nonnegative.  □

This is the proposed general theorem.  The Lee calculation is not needed for
the sign.  What is special to Lee balls is the closed evaluation of the sum of
active brackets, and especially of its minimum over a shell.

## 3. Sign theorem versus sharp-constant phase

For a CDI pair define the edge weight by the left side of (UF).  If all edges
on a fixed shell are positive, define

\[
 \kappa_{A,B}(s)=\min_{\lambda\to\mu}
 \bigl(g_{A,B}(\mu)-g_{A,B}(\lambda)\bigr).
\]

Theorem 2 fixes the sign throughout the whole convex hyperoctahedral class.
It does **not** fix which fibers are active, which edge minimizes their number,
or the value of (\kappa).  Those data can change when a facet or a diagonal
fiber endpoint crosses a lattice threshold.  This is the genuine phase
mechanism:

1. **sign layer:** CDI implies nonnegative transfer increments;
2. **strictness layer:** a transfer is strict iff at least one diagonal fiber
   bracket is active;
3. **sharp layer:** the minimizing edge orbit is the extremizer of a
   body-dependent central-section problem.

Consequently the interpolation from a cross-polytope to a cube has no sign
reversal.  It can, and does, have sharp-edge and equality-chamber transitions.

## 4. A second closed family: cubes

Let (C_t=[-t,t]^d\cap\mathbb Z^d), and put (N=2t+1).  For unequal cube
radii (p,q), define

\[
 L_{p,q}(k)=
 \begin{cases}
 2\min(p,q)+1,&0\le k\le|p-q|,\\
 p+q+1-k,&|p-q|<k\le p+q,\\
 0,&k>p+q.
 \end{cases}
\]

Then

\[
 g_{C_p,C_q}(u)=\prod_{i=1}^d L_{p,q}(|u_i|).
\]

The sequence (L_{p,q}) is nonnegative and log-concave, so a transfer
((a,b)\mapsto(a-1,b+1)) has the exact increment

\[
 \prod_{k\ne i,j}L_{p,q}(u_k)
 \left[L_{p,q}(a-1)L_{p,q}(b+1)
       -L_{p,q}(a)L_{p,q}(b)\right]\ge0.
\]

For equal radii and a fully active shell (2\le s\le2t), the local bracket is
(a-b-1).  Hence the sharp constant is

\[
 \kappa^{\square}_{d,t,s}=
 \begin{cases}
 1,&d=2,\ s\text{ even},\\
 2,&d=2,\ s\text{ odd},\\
 (2t+3-s)(2t+1)^{d-3},&d\ge3.
 \end{cases}
\tag{Cube-kappa}
\]

For (d\ge3), equality in the lower bound is attained by

\[
 \operatorname{sort}(s-2,2,0^{d-2})
 \longrightarrow
 \operatorname{sort}(s-2,1,1,0^{d-3}).
\]

To prove sharpness, write the transferred coordinates as (a,b), their gap
as (D=a-b\), and the residual sum as (r=s-a-b).  Merging two residual
coordinates gives

\[
 (N-x)(N-y)\ge N(N-x-y),
\]

so

\[
 \prod_{k\ne i,j}(N-u_k)\ge(N-r)N^{d-3}.
\]

Since (D-1\ge1), (a+b\ge2), and (N-r=N-s+a+b), every edge weight is at
least ((N-s+2)N^{d-3}).  The displayed edge has (D=2) and concentrates all
residual mass in one coordinate, so it attains the bound.  In (d=2), the
minimum admissible gap is two on even shells and three on odd shells.

This supplies a non-Lee sharp theorem with a different central-section law:
Lee constants are lower-dimensional Lee-ball counts, whereas cube constants
are products of interval-section lengths.

## 5. Mixed Minkowski bodies and an exact minimizer transition

The outer-shell phase can be proved for an infinite mixed family, rather than
only observed in a finite table.  Let

\[
 K_{1,b}=B_1+bB_\infty\subset\mathbb R^3,
 \qquad b\ge1,
\]

put (N=2b+1), and let (S=N+1=2(b+1)) be its outer fully active shell.
The lattice points of (K_{1,b}) have the same four-state decomposition used
below for (b=1), with

\[
 Q_b=\{-b,-b+1,\ldots,b\},
 \qquad E_b=\{-b-1,b+1\}.
\]

Their one-dimensional state-correlation matrices are

\[
 M_0=\begin{pmatrix}N&0\\0&2\end{pmatrix},\qquad
 M_k=\begin{pmatrix}N-k&1\\1&0\end{pmatrix}
 \quad(1\le k\le N-1),
\]

\[
 M_N=\begin{pmatrix}0&1\\1&0\end{pmatrix},\qquad
 M_{N+1}=\begin{pmatrix}0&0\\0&1\end{pmatrix}.
\tag{M-b}
\]

Suppose first that a shell-(S) transfer acts on two positive coordinates
(a>c\ge1), has gap (D=a-c\ge2), and leaves residual coordinate (r).
Put (A_i=N-u_i).  When all shifts are positive, the state sum reduces to

\[
 F(A_1,A_2,A_3)
 =A_1A_2A_3
 +2(A_1A_2+A_1A_3+A_2A_3)
 +2(A_1+A_2+A_3).
\]

The same transfer formula remains valid when the residual shift is zero,
after the (M_0(1,1)=2) state is included.  In both cases, direct subtraction
gives

\[
 \Delta=(N-r+2)(D-1).
\tag{positive-pair}
\]

Because the recipient is positive, (a+c\ge4), hence (r\le S-4=N-3).
Therefore Δ is at least five, with equality exactly when

\[
 D=2,\qquad \{a,c\}=\{3,1\},\qquad r=S-4=2b-2.
\]

It remains to rule out a cheaper transfer into a zero coordinate.  Write its
source as ((a,r,0)) with (a+r=S).  Substitution in (M-b) gives

\[
 \Delta=
 \begin{cases}
 N^2,&r=0,\\
 (N-1)(N+3),&r=1,\\
 a^2+2N-3,&r\ge2.
 \end{cases}
\tag{zero-recipient}
\]

All three quantities are at least seven for (N\ge3), except that the first
two are even larger.  This proves the following sharp statement.

### Proposition 3 (an infinite sharp-κ phase)

For every (b\ge1), on the outer fully active shell (S=2(b+1)) of
(K_{1,b}\subset\mathbb Z^3),

\[
 \kappa_{K_{1,b}}(S)=5,
\]

and the unique minimizing edge orbit is

\[
 \operatorname{sort}(2b-2,3,1)
 \longrightarrow
 \operatorname{sort}(2b-2,2,2).
\tag{mixed-minimizer}
\]

This differs from the cube/Lee axial-residual orbit.  In particular, fixing
the same axial radius two gives the exact three-body phase table

\[
\begin{array}{c|c|c|c}
\text{body}&(a,b)&\kappa(s=4)&\text{minimizing orbit(s)}\\ \hline
2B_\infty&(0,2)&3&(2,2,0)\to(2,1,1)\\
B_1+B_\infty&(1,1)&5&(3,1,0)\to(2,2,0)\\
2B_1&(2,0)&1&\text{three shell-edge orbits}.
\end{array}
\tag{radius-two-phase}
\]

The sign remains positive in all three rows, but both the sharp value and the
minimizing geometry change nonmonotonically.  Thus the cross-to-cube
interpolation exhibits a genuine quantitative phase, not a reversal of the
majorization order.

### The smallest mixed member (K_{1,1})

Let

\[
 K=K_{1,1}=B_1+B_\infty\subset\mathbb R^3.
\]

Its lattice points satisfy

\[
 \sum_{i=1}^3 (|x_i|-1)_+\le1.
\]

Put (Q=\{-1,0,1\}), (E=\{-2,2\}), and

\[
 \mathcal S=\{000,100,010,001\}.
\]

The 81 lattice points of (K) form the disjoint union

\[
 K\cap\mathbb Z^3
 =\bigsqcup_{\alpha\in\mathcal S}
 S_{\alpha_1}\times S_{\alpha_2}\times S_{\alpha_3},
 \qquad S_0=Q,\quad S_1=E.
\]

For (k\ge0), let

\[
 M_k(\alpha,\beta)=|S_\alpha\cap(S_\beta-k)|.
\]

The only matrices needed on the fully active shells (2\le s\le4) are

\[
\begin{array}{c|ccccc}
k&0&1&2&3&4\\ \hline
M_k&
\begin{psmallmatrix}3&0\\0&2\end{psmallmatrix}&
\begin{psmallmatrix}2&1\\1&0\end{psmallmatrix}&
\begin{psmallmatrix}1&1\\1&0\end{psmallmatrix}&
\begin{psmallmatrix}0&1\\1&0\end{psmallmatrix}&
\begin{psmallmatrix}0&0\\0&1\end{psmallmatrix}.
\end{array}
\]

Therefore the autocovariogram is exactly

\[
 g_K(u)=\sum_{\alpha,\beta\in\mathcal S}
 \prod_{i=1}^3 M_{u_i}(\alpha_i,\beta_i).
\tag{State}
\]

Multiplication in (State) gives

\[
\begin{array}{c|c|c}
s&\lambda&g_K(\lambda)\\ \hline
2&(2,0,0),(1,1,0)&39,50\\
3&(3,0,0),(2,1,0),(1,1,1)&18,34,44\\
4&(4,0,0),(3,1,0),(2,2,0),(2,1,1)&9,18,23,30.
\end{array}
\]

### Corollary 4 (complete first mixed shell table)

For (K_{1,1}\subset\mathbb Z^3), the sharp constants and unique minimizing
edge orbits on the fully active shells are

\[
\begin{array}{c|c|c}
s&\kappa_K(s)&\text{minimizing edge}\\ \hline
2&11&(2,0,0)\to(1,1,0)\\
3&10&(2,1,0)\to(1,1,1)\\
4&5 &(3,1,0)\to(2,2,0).
\end{array}
\]

In particular, at (s=4) the Lee/cube axial-residual candidate

\[
 (2,2,0)\to(2,1,1)
\]

has weight (7) and ceases to minimize.  Formula (State) proves all values
without a scan.  In the universal fiber formula (UF), the winning boundary
edge activates five (0/1) diagonal channels, while the axial-residual edge
activates seven.  The single-cap state constraint 
(\alpha_1+\alpha_2+\alpha_3\le1) is the structural reason: at the outer
shell, competing medium-coordinate translations cannot use two cap states at
once.

This is the first instance of the sharp-κ phase in Proposition 3, and not a
sign phase: every transfer remains positive.

## 6. Exact boundary of the sign theorem

Convexity/CDI cannot simply be dropped.  In dimension two let

\[
 X=\{0,\pm e_1,\pm e_2,\pm2e_1,\pm2e_2\}.
\]

This is an unconditional permutation-invariant coordinate downset, but its
(r=2) diagonal fiber is \(\{-2,2\}\), with the center (0) missing.  Directly,

\[
 g_X(2,0)=3>2=g_X(1,1).
\]

Thus the first balancing transfer has increment (-1).  Filling the missing
diagonal orbit gives (B_1^2(2)\cap\mathbb Z^2), for which the same increment
is (8-5=3).  The sign change occurs when the diagonal hole is filled, not
when a convex cross-polytope is deformed toward a convex cube.

## 7. Exact scan summary

The companion exact-integer scan found no negative edge in any of the
following pairwise cross-covariograms (equal and unequal bodies were both
included):

- 21 capped cross-polytopes in (d=2) and 10 in (d=3);
- 19 bodies (aB_1+bB_\infty) in (d=2) and 15 in (d=3);
- 30 lattice (\ell_p)-balls in (d=2) and 18 in (d=3), with
  (p\in\{1,2,3,4,6,\infty\});
- every pair of the 19 lattice-convex symmetric downsets in a
  two-dimensional coordinate box of radius four;
- every pair of the 19 CDI downsets in that box and every pair of the 11 CDI
  downsets in the three-dimensional coordinate box of radius two;
- every pair of the 30 CDI downsets among all 65 symmetric downsets in the
  three-dimensional coordinate box of radius three (47,236 exact edge
  evaluations).

By contrast, all symmetric downsets included 491 negative edges in (d=2)
and 108 in (d=3).  This agrees exactly with the CDI mechanism: the broad
convex class stays on the nonnegative side, while diagonal holes permit order
reversal.

Full tables are in:

- `results/polytope_transfer_phase_scan.md`;
- `results/polytope_transfer_phase_scan.json`;
- `results/minkowski_sum_phase_table.md`.
