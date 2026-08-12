"""Regression tests for the upgraded shell theorems.

These tests fix, as exact integer enumerations, the three statements upgraded
during revision: the mixed-family constants kappa_b(S)=5, kappa_b(S+1)=4, and
kappa_b(s)=0 for s>=S+2 (Theorem: mixed-sharp), the cube constants on the
full active range 2<=s<=2t+1 with vanishing beyond (Theorem: cube-sharp), and
the vanishing of Lee-shell constants beyond the support bound s>2t.  They are
regression tests for the implementation; no finite computation enters the
proofs.
"""

from ehrhart_fswa.counts import cross_polytope_overlap_count, cube_overlap_count
from research.polytope_transfer_phase_scan import (
    cross_covariogram,
    l1_plus_linf,
    transfer_edges,
)


def _weighted_edges(points, shell, dimension=3):
    return [
        (
            cross_covariogram(points, points, target)
            - cross_covariogram(points, points, source),
            source,
            target,
        )
        for source, target in transfer_edges(shell, dimension)
    ]


def test_mixed_shell_S_has_sharp_value_five_with_unique_nonaxial_orbit() -> None:
    for b in range(1, 7):
        body = l1_plus_linf(3, 1, b)
        shell = 2 * b + 2
        weighted = _weighted_edges(body.points, shell)
        sharp = min(weight for weight, _, _ in weighted)
        minimizers = [(src, tgt) for weight, src, tgt in weighted if weight == sharp]
        expected = (
            tuple(sorted((2 * b - 2, 3, 1), reverse=True)),
            tuple(sorted((2 * b - 2, 2, 2), reverse=True)),
        )
        assert sharp == 5
        assert minimizers == [expected]


def test_mixed_shell_S_plus_one_has_sharp_value_four() -> None:
    for b in range(1, 7):
        body = l1_plus_linf(3, 1, b)
        shell = 2 * b + 3
        weighted = _weighted_edges(body.points, shell)
        sharp = min(weight for weight, _, _ in weighted)
        minimizers = sorted(
            (src, tgt) for weight, src, tgt in weighted if weight == sharp
        )
        primary = (
            tuple(sorted((2 * b - 1, 3, 1), reverse=True)),
            tuple(sorted((2 * b - 1, 2, 2), reverse=True)),
        )
        assert sharp == 4
        if b == 1:
            extra = ((3, 2, 0), (3, 1, 1))
            assert minimizers == sorted([primary, extra])
        else:
            assert minimizers == [primary]


def test_mixed_shells_beyond_S_plus_one_are_inactive() -> None:
    for b in range(1, 6):
        body = l1_plus_linf(3, 1, b)
        for shell in (2 * b + 4, 2 * b + 5):
            weights = [w for w, _, _ in _weighted_edges(body.points, shell)]
            assert min(weights) == 0


def test_cube_kappa_on_full_active_range_and_beyond() -> None:
    for dimension in range(2, 5):
        for radius in range(1, 4):
            side = 2 * radius + 1
            for shell in range(2, 2 * radius + 4):
                weights = [
                    cube_overlap_count(radius, target)
                    - cube_overlap_count(radius, source)
                    for source, target in transfer_edges(shell, dimension)
                ]
                observed = min(weights)
                if shell >= 2 * radius + 2:
                    expected = 0
                elif dimension == 2:
                    expected = 1 if shell % 2 == 0 else 2
                else:
                    expected = (side + 2 - shell) * side ** (dimension - 3)
                assert observed == expected


def test_incomparable_compositions_can_share_a_lens_value() -> None:
    """Remark (order-theoretic scope): (4,1,1) and (3,3,0) are incomparable
    on P_3(6) yet have the same equal-radius lens value for t=3."""
    assert cross_polytope_overlap_count(3, (4, 1, 1)) == 4
    assert cross_polytope_overlap_count(3, (3, 3, 0)) == 4


def test_lee_shells_beyond_support_bound_are_inactive() -> None:
    for dimension in range(2, 5):
        for radius in range(1, 4):
            for shell in (2 * radius + 1, 2 * radius + 2):
                for source, target in transfer_edges(shell, dimension):
                    assert cross_polytope_overlap_count(radius, source) == 0
                    assert cross_polytope_overlap_count(radius, target) == 0
