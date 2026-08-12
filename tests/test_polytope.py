from fractions import Fraction

import pytest

from ehrhart_fswa.polytope import (
    SymmetricHPolytope,
    integer_hexagon,
    rational_half_square,
    rational_octagon,
)
from ehrhart_fswa.shifts import integer_l1_shifts


def test_generic_hexagon_matches_specialized_counts() -> None:
    from ehrhart_fswa.counts import hexagon_lattice_count, hexagon_overlap_count

    polytope = integer_hexagon()
    for scale in range(5):
        assert polytope.lattice_count(scale) == hexagon_lattice_count(scale)
        for shift in integer_l1_shifts(2, 2):
            assert polytope.overlap_count(scale, shift) == hexagon_overlap_count(
                scale, shift
            )


def test_half_square_has_period_two_ehrhart_count() -> None:
    polytope = rational_half_square()
    for scale in range(10):
        expected = (2 * (scale // 2) + 1) ** 2
        assert polytope.lattice_count(scale) == expected


def test_generic_common_core_matches_explicit_shift_intersection() -> None:
    polytope = rational_octagon()
    scale = 3
    source = set(polytope.lattice_points(scale))
    shifted = [
        {tuple(point[i] + shift[i] for i in range(2)) for point in source}
        for shift in integer_l1_shifts(2, 1)
    ]
    assert polytope.common_core_count_l1(scale, 1) == len(set.intersection(*shifted))


def test_fractional_facets_are_compared_exactly() -> None:
    polytope = SymmetricHPolytope.create(
        normals=((2,),),
        bounds=(Fraction(3, 2),),
        coordinate_bounds=(1,),
    )
    assert list(polytope.lattice_points(1)) == [(0,)]
    assert list(polytope.lattice_points(2)) == [(-1,), (0,), (1,)]


@pytest.mark.parametrize(
    "constructor",
    [
        lambda: SymmetricHPolytope.create([], [], [1]),
        lambda: SymmetricHPolytope.create([(1, 0)], [1], [1]),
        lambda: SymmetricHPolytope.create([(1,)], [0], [1]),
    ],
)
def test_invalid_h_representations_raise(constructor) -> None:
    with pytest.raises(ValueError):
        constructor()
