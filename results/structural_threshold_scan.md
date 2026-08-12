# Structural threshold scan

Exact regression scan for the structural theorem on
`A_b = (C_d + b B_inf^d) cap Z^d`, `N = 2b+1`.  Every check uses exact
integer arithmetic; no value here enters a proof.

| check | range | failures |
|---|---|---|
| master kernel against direct enumeration | `1 <= d <= 4`, `1 <= b <= 2`, all shifts in `[0, N]^d` | 0 |
| edge law, both cases | `2 <= d <= 7`, `1 <= b <= 4`, every shell and every unit balancing transfer | 0 |
| zero-recipient endpoint `a = s`: closed form and strict loss to the canonical edge | `3 <= d <= 39`, `1 <= b <= 6`, every shell `4 <= s <= N` | 0 |
| structural theorem: value, minimizing orbit, threshold sign | `3 <= d <= 39`, `2 <= b <= 6`, every shell `4 <= s <= N` | 0 |

Threshold ties, where `Theta = N(2N-s-1) - 2(d-3)` vanishes and both the
balanced-gap arc and the canonical axial-residual edge attain the shell
minimum:

| d | b | s |
|---|---|---|
| 13 | 2 | 5 |
| 24 | 3 | 7 |
| 31 | 3 | 5 |
| 39 | 4 | 9 |
