"""Exact scan behind the structural theorem for A_b = (C_d + b B_inf^d) cap Z^d.

The body is

    A_b^{(d)} = { x in Z^d : sum_i (|x_i| - b)_+ <= 1 },     N = 2b+1,

and for every shift with all coordinates in {0, ..., N} its self-overlap obeys
the master kernel

    g(u) = prod_i m_i + 2 sum_j prod_{i!=j} m_i
           + sum_{j!=k, u_j,u_k >= 1} prod_{i!=j,k} m_i,        m_i = N - u_i.

This script checks, by exact integer arithmetic:

  K   the master kernel against direct lattice enumeration (small d, b);
  E   both cases of the edge law, from d = 2 up,
          c >= 1 : Delta = (D-1) g^{(e)}(w)
          c  = 0 : Delta = (a-1) g^{(e)}(w) + 2 P(w) + 2 (N-a) F(w);
  Z   the endpoint a = s of the zero-recipient regime, where the residual is
      empty: weight (s-1) Gamma(0) + 2 N^e, strictly above the canonical value;
  T   the structural theorem: on every shell 4 <= s <= N the shell minimum is
      min{ Gamma(s-4), Gamma(s-2) + 2 N^{e-1} (2N-s) }, attained only by the
      balanced-gap arc with recipient one, respectively only by the canonical
      axial-residual edge, according to the sign of
          Theta = N(2N-s-1) - 2(d-3),
      with both orbits attaining it when Theta = 0.

Nothing here enters a proof; the scan is a regression check on the statement.

Usage:
    python research/structural_threshold_scan.py [--dmax 39] [--bmax 6]
"""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
from itertools import product
from math import prod
from pathlib import Path


def body_points(dimension: int, b: int) -> frozenset[tuple[int, ...]]:
    m = b + 1
    return frozenset(
        x
        for x in product(range(-m, m + 1), repeat=dimension)
        if sum(max(abs(v) - b, 0) for v in x) <= 1
    )


def overlap_direct(points: frozenset[tuple[int, ...]], u: tuple[int, ...]) -> int:
    return sum(1 for x in points if tuple(x[i] + u[i] for i in range(len(u))) in points)


def g_kernel(u: tuple[int, ...], N: int) -> int:
    """Master kernel, written out term by term."""
    d = len(u)
    m = [N - v for v in u]
    total = prod(m)
    total += 2 * sum(prod(m[i] for i in range(d) if i != j) for j in range(d))
    total += sum(
        prod(m[i] for i in range(d) if i != j and i != k)
        for j in range(d)
        for k in range(d)
        if j != k and u[j] >= 1 and u[k] >= 1
    )
    return total


def g_fast(u: tuple[int, ...], N: int) -> int:
    """Master kernel, grouped over the zero coordinates.

    Falls back to the term-by-term form when some factor vanishes.
    """
    d = len(u)
    positive = [v for v in u if v >= 1]
    if any(v == N for v in positive):
        return g_kernel(u, N)
    zeros = d - len(positive)
    P = prod(N - v for v in positive) * N**zeros
    inv_pos = sum(Fraction(1, N - v) for v in positive)
    inv_all = inv_pos + Fraction(zeros, N)
    sq_pos = sum(Fraction(1, (N - v) ** 2) for v in positive)
    value = P * (1 + 2 * inv_all + (inv_pos * inv_pos - sq_pos))
    assert value.denominator == 1
    return int(value)


def residual_functionals(w: tuple[int, ...], N: int) -> tuple[int, int]:
    m = [N - v for v in w]
    P = prod(m)
    F = sum(prod(m[i] for i in range(len(w)) if i != j) for j in range(len(w)) if w[j] >= 1)
    return P, F


def gamma(r: int, e: int, N: int) -> int:
    """g^{(e)} at the concentrated shift r e_1."""
    if e <= 0:
        return 1
    value = (N + 2 - r) * N ** (e - 1)
    if e >= 2:
        value += 2 * (e - 1) * (N - r) * N ** (e - 2)
    return value


def partitions(total: int, parts: int) -> list[tuple[int, ...]]:
    def rec(rem: int, slots: int, cap: int):
        if slots == 1:
            if rem <= cap:
                yield (rem,)
            return
        for first in range(min(rem, cap), -1, -1):
            if first * slots < rem:
                break
            for tail in rec(rem - first, slots - 1, first):
                yield (first,) + tail

    return list(rec(total, parts, total))


def shell_arcs(dimension: int, shell: int):
    """Every unit balancing transfer of the shell, with its local data."""
    for lam in partitions(shell, dimension):
        for i in range(dimension):
            for j in range(dimension):
                if i == j or lam[i] < lam[j] + 2:
                    continue
                mu = list(lam)
                mu[i] -= 1
                mu[j] += 1
                residual = tuple(
                    sorted((lam[k] for k in range(dimension) if k not in (i, j)), reverse=True)
                )
                yield lam, tuple(sorted(mu, reverse=True)), lam[i], lam[j], residual


def check_kernel(dmax: int = 4, bmax: int = 2) -> int:
    failures = 0
    for dimension in range(1, dmax + 1):
        for b in range(1, bmax + 1):
            N = 2 * b + 1
            points = body_points(dimension, b)
            for u in product(range(0, N + 1), repeat=dimension):
                want = overlap_direct(points, u)
                if g_kernel(u, N) != want or g_fast(u, N) != want:
                    failures += 1
    return failures


def check_edge_law(dmax: int = 7, bmax: int = 4) -> int:
    """Both cases of the edge law, from d = 2 up.

    Dimension two exercises the empty-residual conventions g^{(0)}(0) = P = 1
    and F = 0.
    """
    failures = 0
    for b in range(1, bmax + 1):
        N = 2 * b + 1
        for dimension in range(2, dmax + 1):
            for shell in range(2, N + 1):
                for source, target, a, c, w in shell_arcs(dimension, shell):
                    delta = g_fast(target, N) - g_fast(source, N)
                    gw = g_fast(w, N) if w else 1
                    if c >= 1:
                        want = (a - c - 1) * gw
                    else:
                        P, F = residual_functionals(w, N)
                        want = (a - 1) * gw + 2 * P + 2 * (N - a) * F
                    if delta != want:
                        failures += 1
    return failures


def check_zero_recipient_endpoint(dimensions, bmax: int = 6) -> int:
    """The donor-heavy endpoint a = s of the zero-recipient regime.

    There the residual vanishes, so F is an empty sum and the surcharge
    2 N^{e-1} (2N-s) of the generic case does not apply: the weight is
    (s-1) Gamma(0) + 2 N^e.  It has to exceed the canonical value strictly,
    which is what keeps the canonical axial-residual edge the unique minimizer
    of that regime.
    """
    failures = 0
    for b in range(1, bmax + 1):
        N = 2 * b + 1
        for dimension in dimensions:
            e = dimension - 2
            for shell in range(4, N + 1):
                source = (shell,) + (0,) * (dimension - 1)
                target = tuple(
                    sorted((shell - 1, 1) + (0,) * (dimension - 2), reverse=True)
                )
                weight = g_fast(target, N) - g_fast(source, N)
                closed = (shell - 1) * gamma(0, e, N) + 2 * N**e
                canonical = gamma(shell - 2, e, N) + 2 * N ** (e - 1) * (2 * N - shell)
                if weight != closed or weight <= canonical:
                    failures += 1
                    print(
                        f"  FAIL endpoint d={dimension} b={b} s={shell} "
                        f"weight={weight} closed={closed} canonical={canonical}"
                    )
    return failures


def check_theorem(dimensions, bmax: int = 6, verbose: bool = False):
    failures = 0
    ties = []
    for b in range(2, bmax + 1):
        N = 2 * b + 1
        for dimension in dimensions:
            e = dimension - 2
            for shell in range(4, N + 1):
                balanced = gamma(shell - 4, e, N)
                canonical = gamma(shell - 2, e, N) + 2 * N ** (e - 1) * (2 * N - shell)
                theta = N * (2 * N - shell - 1) - 2 * (dimension - 3)
                if (balanced < canonical) != (theta > 0):
                    failures += 1
                if (balanced == canonical) != (theta == 0):
                    failures += 1
                best = None
                argmin: list[tuple[int, int, tuple[int, ...]]] = []
                for source, target, a, c, w in shell_arcs(dimension, shell):
                    delta = g_fast(target, N) - g_fast(source, N)
                    if best is None or delta < best:
                        best, argmin = delta, [(a, c, w)]
                    elif delta == best:
                        argmin.append((a, c, w))
                argmin = sorted(set(argmin))
                tail = (0,) * (dimension - 3)
                orbit_balanced = (3, 1, tuple(sorted((shell - 4,) + tail, reverse=True)))
                orbit_canonical = (2, 0, tuple(sorted((shell - 2,) + tail, reverse=True)))
                if theta > 0:
                    expected = [orbit_balanced]
                elif theta < 0:
                    expected = [orbit_canonical]
                else:
                    expected = sorted({orbit_balanced, orbit_canonical})
                    ties.append((dimension, b, shell))
                if best != min(balanced, canonical) or argmin != expected:
                    failures += 1
                    print(
                        f"  FAIL d={dimension} b={b} s={shell} theta={theta} "
                        f"kappa={best} want={min(balanced, canonical)} "
                        f"argmin={argmin} expected={expected}"
                    )
                elif verbose:
                    print(
                        f"  ok d={dimension:3d} b={b} s={shell:2d} "
                        f"theta={theta:6d} kappa={best}"
                    )
    return failures, ties


def write_markdown(summary: dict[str, object], destination: Path) -> None:
    ties = summary["threshold_ties"]
    assert isinstance(ties, list)
    lines = [
        "# Structural threshold scan",
        "",
        "Exact regression scan for the structural theorem on",
        "`A_b = (C_d + b B_inf^d) cap Z^d`, `N = 2b+1`.  Every check uses exact",
        "integer arithmetic; no value here enters a proof.",
        "",
        "| check | range | failures |",
        "|---|---|---|",
        "| master kernel against direct enumeration | "
        f"`1 <= d <= {summary['kernel_dmax']}`, `1 <= b <= {summary['kernel_bmax']}`, "
        f"all shifts in `[0, N]^d` | {summary['kernel_failures']} |",
        "| edge law, both cases | "
        f"`2 <= d <= {summary['edge_dmax']}`, `1 <= b <= {summary['edge_bmax']}`, "
        "every shell and every unit balancing transfer | "
        f"{summary['edge_failures']} |",
        "| zero-recipient endpoint `a = s`: closed form and strict loss to the "
        "canonical edge | "
        f"`3 <= d <= {summary['theorem_dmax']}`, `1 <= b <= {summary['theorem_bmax']}`, "
        "every shell `4 <= s <= N` | "
        f"{summary['endpoint_failures']} |",
        "| structural theorem: value, minimizing orbit, threshold sign | "
        f"`3 <= d <= {summary['theorem_dmax']}`, `2 <= b <= {summary['theorem_bmax']}`, "
        "every shell `4 <= s <= N` | "
        f"{summary['theorem_failures']} |",
        "",
        "Threshold ties, where `Theta = N(2N-s-1) - 2(d-3)` vanishes and both the",
        "balanced-gap arc and the canonical axial-residual edge attain the shell",
        "minimum:",
        "",
        "| d | b | s |",
        "|---|---|---|",
    ]
    lines.extend(f"| {d} | {b} | {s} |" for d, b, s in ties)
    lines.append("")
    destination.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dmax", type=int, default=39)
    parser.add_argument("--bmax", type=int, default=6)
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    # Direct enumeration and the full arc sweep are exponential in the
    # dimension, so their ranges are fixed and small.
    kernel_dmax, kernel_bmax = 4, 2
    edge_dmax, edge_bmax = 7, 4

    print("K  master kernel against direct enumeration")
    kernel_failures = check_kernel(kernel_dmax, kernel_bmax)
    print("   failures:", kernel_failures)
    print("E  edge law, both cases")
    edge_failures = check_edge_law(edge_dmax, edge_bmax)
    print("   failures:", edge_failures)
    print(f"Z  zero-recipient endpoint a = s, 1 <= b <= {args.bmax}, "
          f"3 <= d <= {args.dmax}")
    endpoint_failures = check_zero_recipient_endpoint(
        range(3, args.dmax + 1), args.bmax
    )
    print("   failures:", endpoint_failures)
    print(f"T  structural theorem, 2 <= b <= {args.bmax}, 3 <= d <= {args.dmax}")
    failures, ties = check_theorem(range(3, args.dmax + 1), args.bmax, args.verbose)
    print("   failures:", failures)
    print("   threshold ties (d, b, s):", ties)

    summary = {
        "kernel_dmax": kernel_dmax,
        "kernel_bmax": kernel_bmax,
        "kernel_failures": kernel_failures,
        "edge_dmax": edge_dmax,
        "edge_bmax": edge_bmax,
        "edge_failures": edge_failures,
        "endpoint_failures": endpoint_failures,
        "theorem_dmax": args.dmax,
        "theorem_bmax": args.bmax,
        "theorem_failures": failures,
        "threshold_ties": [list(tie) for tie in ties],
    }
    root = Path(__file__).resolve().parents[1]
    json_path = root / "results" / "structural_threshold_scan.json"
    markdown_path = root / "results" / "structural_threshold_scan.md"
    json_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    write_markdown(summary, markdown_path)
    print(f"wrote {json_path}")
    print(f"wrote {markdown_path}")


if __name__ == "__main__":
    main()
