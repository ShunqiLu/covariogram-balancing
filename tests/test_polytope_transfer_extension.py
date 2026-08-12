"""Exact regression tests for the non-Lee transfer theorems.

These tests are not evidence in place of the proofs.  They protect the
implementation, formulas, and tables from transcription regressions.
"""

from itertools import product

from ehrhart_fswa.counts import cube_overlap_count
from research.polytope_transfer_phase_scan import (
    atomic_exposure,
    capped_cross_polytope,
    cross_covariogram,
    l1_plus_linf,
    lp_ball,
    scan_pair,
    transfer_edges,
)


def test_atomic_exposure_matches_endpoint_indicator_exhaustively() -> None:
    for alpha, beta, difference in product(range(9), range(9), range(2, 11)):
        if (alpha - beta + difference) % 2:
            continue
        expected = int(abs(beta - difference + 2) <= alpha < beta + difference)
        assert atomic_exposure(alpha, beta, difference) == expected


def test_small_symmetric_convex_cross_covariograms_have_no_negative_arc() -> None:
    bodies = [
        capped_cross_polytope(2, 3, 2),
        capped_cross_polytope(2, 4, 3),
        l1_plus_linf(2, 1, 2),
        lp_ball(2, 2, 3),
        lp_ball(2, "inf", 2),
    ]
    for left in bodies:
        for right in bodies:
            histogram, _ = scan_pair(left, right, max_shell=5)
            assert min(histogram, default=0) >= 0


def test_diagonal_hole_allows_a_negative_balancing_increment() -> None:
    cross = frozenset(
        {
            (0, 0),
            (1, 0),
            (-1, 0),
            (2, 0),
            (-2, 0),
            (0, 1),
            (0, -1),
            (0, 2),
            (0, -2),
        }
    )
    assert cross_covariogram(cross, cross, (2, 0)) == 3
    assert cross_covariogram(cross, cross, (1, 1)) == 2


def test_cube_sharp_constant_formula() -> None:
    for dimension in range(2, 6):
        for radius in range(1, 5):
            side = 2 * radius + 1
            for shell in range(2, 2 * radius + 1):
                weights = [
                    cube_overlap_count(radius, target)
                    - cube_overlap_count(radius, source)
                    for source, target in transfer_edges(shell, dimension)
                ]
                observed = min(weights)
                if dimension == 2:
                    expected = 1 if shell % 2 == 0 else 2
                else:
                    expected = (side - shell + 2) * side ** (dimension - 3)
                assert observed == expected


def test_capped_cross_polytope_tent_formula() -> None:
    for cap in range(1, 7):
        for total_radius in range(1, 2 * cap + 1):
            body = capped_cross_polytope(2, total_radius, cap)
            increment = cross_covariogram(body.points, body.points, (1, 1)) - cross_covariogram(
                body.points, body.points, (2, 0)
            )
            assert increment == min(2 * total_radius - 1, 4 * cap - 2 * total_radius + 1)


def test_mixed_outer_shell_has_sharp_value_five_and_unique_orbit() -> None:
    for cube_radius in range(1, 9):
        body = l1_plus_linf(3, 1, cube_radius)
        shell = 2 * (cube_radius + 1)
        weighted = [
            (
                cross_covariogram(body.points, body.points, target)
                - cross_covariogram(body.points, body.points, source),
                source,
                target,
            )
            for source, target in transfer_edges(shell, 3)
        ]
        sharp = min(weight for weight, _, _ in weighted)
        minimizers = [(source, target) for weight, source, target in weighted if weight == sharp]
        expected = (
            tuple(sorted((2 * cube_radius - 2, 3, 1), reverse=True)),
            tuple(sorted((2 * cube_radius - 2, 2, 2), reverse=True)),
        )
        assert sharp == 5
        assert minimizers == [expected]
