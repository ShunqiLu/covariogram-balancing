# Exact reference sampler benchmark

These are reproducible Python reference timings, not constant-time implementation claims. Rank samplers are exactly uniform by a count/unrank bijection.

| family | n | t | #points | entropy bits | median us | p95 us | CT claim |
|---|---:|---:|---:|---:|---:|---:|---|
| cube | 4 | 16 | 1185921 | 20.178 | 2.100 | 2.400 | no |
| cross_polytope_rank | 4 | 16 | 50049 | 15.611 | 15.700 | 19.100 | no |
| hybrid_H_rank | 4 | 16 | 570113 | 19.121 | 19.800 | 27.300 | no |
| cube | 8 | 16 | 1406408618241 | 40.355 | 4.100 | 4.600 | no |
| cross_polytope_rank | 8 | 16 | 39490049 | 25.235 | 32.800 | 40.000 | no |
| hybrid_H_rank | 8 | 16 | 92468693985 | 36.428 | 37.400 | 49.000 | no |
| cube | 16 | 16 | 1977985201462558877934081 | 80.710 | 6.900 | 7.900 | no |
| cross_polytope_rank | 16 | 16 | 252055236609 | 37.875 | 66.550 | 91.900 | no |
| hybrid_H_rank | 16 | 16 | 258172311189980049921 | 67.807 | 86.400 | 200.500 | no |
