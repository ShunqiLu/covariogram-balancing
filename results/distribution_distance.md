# Pairwise conditioning versus a common FSwA target

Naive output for shift `u` is uniform on `S intersection (S+u)`. These supports depend on `u`. The common-target construction instead uses the intersection of all shifted sources and has exact output distance zero between secrets.

| family | n | t | #S | min pairwise A | common A | max naive TV | common TV |
|---|---:|---:|---:|---:|---:|---:|---:|
| cube | 2 | 8 | 289 | 15/17 | 169/289 | 2/15 | 0/1 |
| cross_polytope | 2 | 8 | 145 | 113/145 | 17/29 | 28/113 | 0/1 |
| hybrid_full | 2 | 8 | 229 | 195/229 | 145/229 | 34/195 | 0/1 |
| hexagon_blocks | 2 | 8 | 217 | 183/217 | 127/217 | 34/183 | 0/1 |
