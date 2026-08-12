"""Computational checks for the first exact-formula theorem candidates."""

from __future__ import annotations

import pytest

from ehrhart_fswa.counts import (
    block_hexagon_overlap_count,
    cross_polytope_lattice_count,
    cross_polytope_overlap_count,
    hexagon_lattice_count,
    hexagon_overlap_count,
)
from ehrhart_fswa.shifts import integer_l1_shifts


@pytest.mark.parametrize("dimension", range(1, 7))
@pytest.mark.parametrize("radius", range(1, 11))
def test_cross_axis_two_is_smaller_cross_polytope(radius: int, dimension: int) -> None:
    shift = (2,) + (0,) * (dimension - 1)
    assert cross_polytope_overlap_count(radius, shift) == (
        cross_polytope_lattice_count(radius - 1, dimension)
    )


@pytest.mark.parametrize("dimension", range(2, 7))
@pytest.mark.parametrize("radius", range(1, 11))
def test_cross_unit_and_split_shifts_have_same_closed_form(
    radius: int, dimension: int
) -> None:
    unit_shift = (1,) + (0,) * (dimension - 1)
    split_shift = (1, 1) + (0,) * (dimension - 2)
    expected = cross_polytope_lattice_count(
        radius, dimension
    ) - cross_polytope_lattice_count(radius, dimension - 1)
    assert cross_polytope_overlap_count(radius, unit_shift) == expected
    assert cross_polytope_overlap_count(radius, split_shift) == expected


@pytest.mark.parametrize("dimension", range(1, 7))
@pytest.mark.parametrize("radius", range(1, 9))
def test_cross_axis_two_is_worst_for_l1_shift_radius_two(
    radius: int, dimension: int
) -> None:
    overlaps = [
        cross_polytope_overlap_count(radius, shift)
        for shift in integer_l1_shifts(dimension, 2)
    ]
    expected = cross_polytope_lattice_count(radius - 1, dimension)
    assert min(overlaps) == expected


@pytest.mark.parametrize("radius", range(1, 30))
def test_hexagon_directional_formulas(radius: int) -> None:
    assert hexagon_overlap_count(radius, (2, 0)) == 3 * radius**2 - radius - 1
    assert hexagon_overlap_count(radius, (1, 1)) == 3 * radius**2 - radius
    assert hexagon_overlap_count(radius, (1, 0)) == 3 * radius**2 + radius
    assert hexagon_overlap_count(radius, (1, -1)) == 3 * radius**2 + radius


@pytest.mark.parametrize("dimension", [2, 4, 6])
@pytest.mark.parametrize("radius", range(1, 9))
def test_hexagon_axis_two_is_worst_for_block_l1_shift_radius_two(
    radius: int, dimension: int
) -> None:
    overlaps = [
        block_hexagon_overlap_count(radius, shift)
        for shift in integer_l1_shifts(dimension, 2)
    ]
    expected = (3 * radius**2 - radius - 1) * hexagon_lattice_count(radius) ** (
        dimension // 2 - 1
    )
    assert min(overlaps) == expected
