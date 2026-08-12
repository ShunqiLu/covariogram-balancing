# Fixed-shift Ehrhart structure probe

Each candidate is determined from exact counts and checked on every integer scale in the stated interval. This is a finite computational check, not by itself a proof for all scales. The evidence column states whether a separate proof is supplied in the manuscript. `C(k,j)` denotes a binomial coefficient.

| study | family | n | u | degree | period | onset | checked through | evidence |
|---|---|---:|---|---:|---:|---:|---:|---|
| cube_n4_axis2 | cube | 4 | `(2, 0, 0, 0)` | 4 | 1 | 1 | 80 | proved by formula/theorem |
| cube_n4_split11 | cube | 4 | `(1, 1, 0, 0)` | 4 | 1 | 0 | 80 | proved by formula/theorem |
| cross_n2_axis2 | cross_polytope | 2 | `(2, 0)` | 2 | 1 | 1 | 80 | proved by formula/theorem |
| cross_n2_split11 | cross_polytope | 2 | `(1, 1)` | 2 | 1 | 0 | 80 | proved by formula/theorem |
| cross_n4_axis2 | cross_polytope | 4 | `(2, 0, 0, 0)` | 4 | 1 | 1 | 80 | proved by formula/theorem |
| cross_n4_split11 | cross_polytope | 4 | `(1, 1, 0, 0)` | 4 | 1 | 0 | 80 | proved by formula/theorem |
| hex_n2_axis2 | hexagon | 2 | `(2, 0)` | 2 | 1 | 1 | 80 | proved by formula/theorem |
| hex_n2_diagonal11 | hexagon | 2 | `(1, 1)` | 2 | 1 | 0 | 80 | proved by formula/theorem |
| hex_n2_root11 | hexagon | 2 | `(1, -1)` | 2 | 1 | 0 | 80 | proved by formula/theorem |
| rational_half_square_axis1 | rational_half_square | 2 | `(1, 0)` | 2 | 2 | 0 | 80 | finite fit and holdout checks only |
| rational_octagon_axis1 | rational_octagon | 2 | `(1, 0)` | 2 | 2 | 0 | 80 | finite fit and holdout checks only |
| hybrid_H_n4_count | hybrid_H | 4 | `(0, 0, 0, 0)` | 4 | 1 | 0 | 80 | proved integral Ehrhart case |
| hybrid_H_n2_irrational_count | hybrid_H_irrational | 2 | `(0, 0)` | -- | -- | -- | -- | finite fit only; global quasi-polynomial is disproved |

## Exact Newton-basis candidates

### cube_n4_axis2

- `all residues`: `N(t) = 27 + 348*C((t-1)/1,1) + 992*C((t-1)/1,2) + 1056*C((t-1)/1,3) + 384*C((t-1)/1,4)`

### cube_n4_split11

- `all residues`: `N(t) = 36*C(t,1) + 328*C(t,2) + 672*C(t,3) + 384*C(t,4)`

### cross_n2_axis2

- `all residues`: `N(t) = 1 + 4*C((t-1)/1,1) + 4*C((t-1)/1,2)`

### cross_n2_split11

- `all residues`: `N(t) = 2*C(t,1) + 4*C(t,2)`

### cross_n4_axis2

- `all residues`: `N(t) = 1 + 8*C((t-1)/1,1) + 24*C((t-1)/1,2) + 32*C((t-1)/1,3) + 16*C((t-1)/1,4)`

### cross_n4_split11

- `all residues`: `N(t) = 2*C(t,1) + 12*C(t,2) + 24*C(t,3) + 16*C(t,4)`

### hex_n2_axis2

- `all residues`: `N(t) = 1 + 8*C((t-1)/1,1) + 6*C((t-1)/1,2)`

### hex_n2_diagonal11

- `all residues`: `N(t) = 2*C(t,1) + 6*C(t,2)`

### hex_n2_root11

- `all residues`: `N(t) = 4*C(t,1) + 6*C(t,2)`

### rational_half_square_axis1

- `t mod 2 = 0`: `N(t) = 6*C((t-0)/2,1) + 8*C((t-0)/2,2)`
- `t mod 2 = 1`: `N(t) = 6*C((t-1)/2,1) + 8*C((t-1)/2,2)`

### rational_octagon_axis1

- `t mod 2 = 0`: `N(t) = 16*C((t-0)/2,1) + 28*C((t-0)/2,2)`
- `t mod 2 = 1`: `N(t) = 2 + 28*C((t-1)/2,1) + 28*C((t-1)/2,2)`

### hybrid_H_n4_count

- `all residues`: `N(t) = 1 + 32*C(t,1) + 192*C(t,2) + 352*C(t,3) + 192*C(t,4)`

### hybrid_H_n2_irrational_count

No candidate was found within the search bounds.

