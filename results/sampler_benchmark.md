# Exact reference sampler benchmark

These are reproducible Python reference timings, not constant-time implementation claims. Rank samplers are exactly uniform by a count/unrank bijection.

| family | n | t | #points | entropy bits | median us | p95 us | CT claim |
|---|---:|---:|---:|---:|---:|---:|---|
| cube | 4 | 16 | 1185921 | 20.178 | 2.200 | 2.600 | no |
| cross_polytope_rank | 4 | 16 | 50049 | 15.611 | 15.950 | 19.800 | no |
| hybrid_H_rank | 4 | 16 | 570113 | 19.121 | 17.700 | 25.200 | no |
| cube | 8 | 16 | 1406408618241 | 40.355 | 4.100 | 4.900 | no |
| cross_polytope_rank | 8 | 16 | 39490049 | 25.235 | 34.200 | 43.700 | no |
| hybrid_H_rank | 8 | 16 | 92468693985 | 36.428 | 42.350 | 64.300 | no |
| cube | 16 | 16 | 1977985201462558877934081 | 80.710 | 7.400 | 9.000 | no |
| cross_polytope_rank | 16 | 16 | 252055236609 | 37.875 | 61.300 | 85.500 | no |
| hybrid_H_rank | 16 | 16 | 258172311189980049921 | 67.807 | 77.150 | 184.100 | no |
