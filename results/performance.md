# Exact-routine performance and memory

Environment: Python 3.13.5, Windows-11-10.0.26200-SP0 (build 26200), executable `D:\soft\Anaconda\python.exe`; CPU Intel(R) Core(TM) Ultra 9 275HX (24 physical cores, 24 logical processors); 63.43 GiB RAM; WSL=False; active power scheme `Balanced (381b4222-f694-41f0-9685-ff5bb260df2e)`. Times are one deterministic reference run; memory is the peak Python heap reported by `tracemalloc`, not process RSS. These figures are reproducibility diagnostics, not optimized implementation claims.

| operation | parameters | seconds | peak MiB | result fingerprint |
|---|---|---:|---:|---|
| cross-overlap bivariate DP | `d=4,t=40,u=(6,0,0,0)` | 0.013211 | 0.057 | `digits=7,mod2^64=1321641` |
| truncated-l1 count | `d=32,B=608,L=floor(608*sqrt(32))` | 0.290798 | 0.687 | `digits=88,mod2^64=2794106642062884865` |
| generic rational H-enumeration | `rational octagon,d=2,t=80,u=(1,0)` | 1.566573 | 0.086 | `digits=5,mod2^64=22480` |
| rank/unrank round trips | `64 deterministic ranks,d=16,B=16,L=64` | 0.297024 | 0.071 | `digits=21,mod2^64=17419879899224605695` |

## Complexity model

- **cross-overlap bivariate DP:** O(d t^3) naive sparse-truncated arithmetic; O(t^2) states. exact Python integers; signed-permutation canonical cache.
- **truncated-l1 count:** O(d L) arithmetic and O(L) coefficient storage. sliding-window univariate DP.
- **generic rational H-enumeration:** O((2t+1)^d * number_of_facets). independent low-dimensional reference enumerator.
- **rank/unrank round trips:** O(samples*d*B) completion-count queries after DP caching. reference implementation; no constant-time claim.
