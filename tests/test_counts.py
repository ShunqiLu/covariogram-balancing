from __future__ import annotations

from itertools import product

import pytest

from ehrhart_fswa.counts import (
    block_hexagon_lattice_count,
    block_hexagon_overlap_count,
    block_cross_polytope_lattice_count,
    block_cross_polytope_overlap_count,
    cross_polytope_lattice_count,
    cross_polytope_overlap_count,
    cube_lattice_count,
    cube_overlap_count,
    hexagon_lattice_count,
    hexagon_overlap_count,
)
from ehrhart_fswa.shifts import integer_l1_shifts


def brute_points(radius: int, dimension: int, member) -> set[tuple[int, ...]]:
    return {
        point
        for point in product(range(-radius, radius + 1), repeat=dimension)
        if member(point)
    }


def brute_overlap(points: set[tuple[int, ...]], shift: tuple[int, ...]) -> int:
    return sum(
        tuple(point[i] + shift[i] for i in range(len(point))) in points
        for point in points
    )


@pytest.mark.parametrize("dimension", [1, 2, 3])
@pytest.mark.parametrize("radius", [0, 1, 2, 3])
def test_cube_formula_matches_brute_force(radius: int, dimension: int) -> None:
    points = brute_points(radius, dimension, lambda _: True)
    assert cube_lattice_count(radius, dimension) == len(points)
    for shift in integer_l1_shifts(dimension, 3):
        assert cube_overlap_count(radius, shift) == brute_overlap(points, shift)


@pytest.mark.parametrize("dimension", [1, 2, 3])
@pytest.mark.parametrize("radius", [0, 1, 2, 3])
def test_cross_polytope_dp_matches_brute_force(radius: int, dimension: int) -> None:
    points = brute_points(radius, dimension, lambda p: sum(map(abs, p)) <= radius)
    assert cross_polytope_lattice_count(radius, dimension) == len(points)
    for shift in integer_l1_shifts(dimension, 3):
        assert cross_polytope_overlap_count(radius, shift) == brute_overlap(
            points, shift
        )


@pytest.mark.parametrize("radius", [0, 1, 2, 3, 4])
def test_hexagon_formula_and_overlap_match_brute_force(radius: int) -> None:
    points = brute_points(
        radius,
        2,
        lambda p: max(abs(p[0]), abs(p[1]), abs(p[0] + p[1])) <= radius,
    )
    assert hexagon_lattice_count(radius) == len(points)
    for shift in integer_l1_shifts(2, 3):
        assert hexagon_overlap_count(radius, shift) == brute_overlap(points, shift)


def test_hexagon_block_product_factorizes() -> None:
    radius = 2
    shift = (1, -1, 0, 2)
    expected = hexagon_overlap_count(radius, shift[:2]) * hexagon_overlap_count(
        radius, shift[2:]
    )
    assert block_hexagon_overlap_count(radius, shift) == expected
    assert block_hexagon_lattice_count(radius, 4) == hexagon_lattice_count(radius) ** 2


def test_cross_polytope_block_product_factorizes() -> None:
    radius = 3
    shift = (1, -1, 0, 2)
    expected = cross_polytope_overlap_count(
        radius, shift[:2]
    ) * cross_polytope_overlap_count(radius, shift[2:])
    assert block_cross_polytope_overlap_count(radius, shift, 2) == expected
    assert block_cross_polytope_lattice_count(radius, 4, 2) == (
        cross_polytope_lattice_count(radius, 2) ** 2
    )


def test_cross_polytope_signed_permutation_symmetry() -> None:
    assert cross_polytope_overlap_count(5, (3, -1, 0, 2)) == (
        cross_polytope_overlap_count(5, (-2, 0, -3, 1))
    )


@pytest.mark.parametrize(
    "call",
    [
        lambda: cube_lattice_count(-1, 2),
        lambda: cross_polytope_lattice_count(1, 0),
        lambda: block_hexagon_lattice_count(1, 3),
    ],
)
def test_invalid_parameters_raise(call) -> None:
    with pytest.raises(ValueError):
        call()
