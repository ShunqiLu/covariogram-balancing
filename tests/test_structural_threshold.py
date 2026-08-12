"""Regression tests for the structural theorem on A_b = (C_d + b B_inf^d).

These fix, as exact integer enumerations, the three statements of the
structural section: the master kernel, the two cases of the edge law, and the
sharp constant together with its minimizing orbit and the sign of the
threshold Theta = N(2N-s-1) - 2(d-3).  The wide scan (2 <= b <= 6,
3 <= d <= 39) lives in research/structural_threshold_scan.py; the tests below
cover a reduced range plus the four dimensions at which the threshold ties.
No finite computation enters the proofs.
"""

from research.structural_threshold_scan import (
    check_edge_law,
    check_kernel,
    check_theorem,
    check_zero_recipient_endpoint,
    gamma,
    g_fast,
    g_kernel,
    shell_arcs,
)


def test_master_kernel_matches_direct_enumeration() -> None:
    assert check_kernel(dmax=4, bmax=2) == 0


def test_edge_law_both_cases() -> None:
    """Includes d = 2, where the residual is empty and g^{(0)}(0) = 1."""
    assert check_edge_law(dmax=6, bmax=3) == 0


def test_zero_recipient_endpoint_loses_to_the_canonical_edge() -> None:
    """a = s has an empty residual, so it pays 2N^e instead of the surcharge."""
    assert check_zero_recipient_endpoint(range(3, 20), bmax=5) == 0


def test_structural_theorem_low_dimensions() -> None:
    failures, ties = check_theorem(range(3, 13), bmax=4)
    assert failures == 0
    assert ties == []


def test_structural_theorem_at_threshold_ties() -> None:
    """The four smallest ties claimed in the paper, and nothing else nearby."""
    expected = {(13, 2, 5), (24, 3, 7), (31, 3, 5), (39, 4, 9)}
    failures, ties = check_theorem([13, 24, 31, 39], bmax=4)
    assert failures == 0
    assert set(ties) == expected


def test_canonical_edge_wins_above_the_threshold() -> None:
    """d = 14, b = 2, s = 5 is the first case past a tie: Theta < 0 there."""
    b, dimension, shell = 2, 14, 5
    N, e = 2 * b + 1, dimension - 2
    weights = [
        g_fast(target, N) - g_fast(source, N)
        for source, target, *_ in shell_arcs(dimension, shell)
    ]
    canonical = gamma(shell - 2, e, N) + 2 * N ** (e - 1) * (2 * N - shell)
    assert N * (2 * N - shell - 1) - 2 * (dimension - 3) < 0
    assert min(weights) == canonical < gamma(shell - 4, e, N)


def test_dimension_three_closed_form() -> None:
    """kappa = N + 6 - s on 4 <= s <= N, matching Theorem mixed-sharp at N+1."""
    for b in range(2, 7):
        N = 2 * b + 1
        for shell in range(4, N + 1):
            weights = [
                g_kernel(target, N) - g_kernel(source, N)
                for source, target, *_ in shell_arcs(3, shell)
            ]
            assert min(weights) == N + 6 - shell
