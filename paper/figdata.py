"""Exact data used by the figure scripts.  Run from paper/."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ehrhart_fswa.majorization import (  # noqa: E402
    balancing_neighbors,
    classify_sharp_arcs,
    lee_shell_partitions,
    majorization_distance,
    sharp_equal_radius_constant,
    unequal_lee_lens_count,
)


def structural_candidates(b: int, d: int, s: int):
    """The two candidates of the structural theorem, and the threshold.

    Exact integers: the recipient-one weight, the recipient-zero weight, and
    $\\Theta_{d,b}(s)$, whose sign says which weight is smaller.
    """
    N, e = 2 * b + 1, d - 2

    def gamma(r: int) -> int:
        value = (N + 2 - r) * N ** (e - 1)
        if e >= 2:
            value += 2 * (e - 1) * (N - r) * N ** (e - 2)
        return value

    balanced = gamma(s - 4)
    canonical = gamma(s - 2) + 2 * N ** (e - 1) * (2 * N - s)
    return balanced, canonical, N * (2 * N - s - 1) - 2 * (d - 3)


def shell_graph(radius: int, total: int, dimension: int):
    parts = lee_shell_partitions(total, dimension)
    lens = {p: unequal_lee_lens_count(radius, radius, p) for p in parts}
    edges = []
    for p in parts:
        for q in balancing_neighbors(p):
            if q in lens:
                edges.append((p, q, lens[q] - lens[p]))
    return parts, lens, edges


if __name__ == "__main__":
    t, s, d = 5, 8, 3
    print(f"kappa(d=3,t=5,s=8) = {sharp_equal_radius_constant(t, s, d)}")
    print("sharp arcs:", classify_sharp_arcs(t, s, d))
    J = lambda p: unequal_lee_lens_count(t, t, p)  # noqa: E731
    for a, b in [((4, 3, 1), (4, 2, 2)), ((4, 2, 2), (3, 3, 2)),
                 ((4, 3, 1), (3, 3, 2)), ((6, 2, 0), (6, 1, 1))]:
        print(f"  {a} -> {b}: w = {J(b) - J(a)}, d_M = "
              f"{majorization_distance(a, b)}")

    print()
    print("outermost shell t=3 s=6 path")
    path = [(6, 0, 0), (5, 1, 0), (4, 2, 0), (3, 3, 0)]
    Jo = lambda p: unequal_lee_lens_count(3, 3, p)  # noqa: E731
    for a, b in zip(path, path[1:]):
        print(f"  {a} -> {b}: w = {Jo(b) - Jo(a)}")
    print("  endpoints: deficit =", Jo(path[-1]) - Jo(path[0]),
          " d_M =", majorization_distance(path[0], path[-1]),
          " kappa =", sharp_equal_radius_constant(3, 6, 3))

    print()
    print("structural candidates at the threshold ties")
    for b_, d_, s_ in [(2, 13, 5), (3, 24, 7), (3, 31, 5)]:
        bal, can, theta = structural_candidates(b_, d_, s_)
        print(f"  b={b_} d={d_} s={s_}: recipient one={bal} "
              f"recipient zero={can} theta={theta}")

    print()
    print("Lee/cube constants d=3 t=5")
    for s3 in range(2, 13):
        lee = sharp_equal_radius_constant(5, s3, 3) if s3 <= 10 else 0
        H = 11
        cube = (H + 2 - s3) if 2 <= s3 <= H else 0
        print(f"  s={s3}: lee={lee} cube={cube}")
