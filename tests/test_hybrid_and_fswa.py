from __future__ import annotations

from itertools import product

import pytest

from ehrhart_fswa.counts import (
    hybrid_l1_radius,
    hybrid_lattice_count,
    hybrid_max_l2_squared,
    hybrid_overlap_count,
    truncated_l1_lattice_count,
)
from ehrhart_fswa.fswa import Family, common_core_metrics
from ehrhart_fswa.shifts import integer_l1_shifts


def _points(radius: int, dimension: int, member) -> set[tuple[int, ...]]:
    return {
        point
        for point in product(range(-radius, radius + 1), repeat=dimension)
        if member(point)
    }


@pytest.mark.parametrize("dimension", [1, 2, 3, 4])
@pytest.mark.parametrize("coordinate_radius", [0, 1, 2, 3])
def test_truncated_l1_count_matches_brute_force(
    coordinate_radius: int, dimension: int
) -> None:
    for l1_radius in range(coordinate_radius * dimension + 3):
        points = _points(
            coordinate_radius,
            dimension,
            lambda point: sum(map(abs, point)) <= l1_radius,
        )
        assert truncated_l1_lattice_count(
            coordinate_radius, dimension, l1_radius
        ) == len(points)


@pytest.mark.parametrize("dimension", [1, 2, 3])
@pytest.mark.parametrize("coordinate_radius", [0, 1, 2, 3])
def test_hybrid_count_overlap_and_norm_match_brute_force(
    coordinate_radius: int, dimension: int
) -> None:
    l1_radius = hybrid_l1_radius(coordinate_radius, dimension)
    points = _points(
        coordinate_radius,
        dimension,
        lambda point: sum(map(abs, point)) <= l1_radius,
    )
    assert hybrid_lattice_count(coordinate_radius, dimension) == len(points)
    assert hybrid_max_l2_squared(coordinate_radius, dimension) == max(
        (sum(value * value for value in point) for point in points), default=0
    )
    for shift in integer_l1_shifts(dimension, 2):
        brute_overlap = sum(
            tuple(point[i] + shift[i] for i in range(dimension)) in points
            for point in points
        )
        assert hybrid_overlap_count(coordinate_radius, shift) == brute_overlap


def _family_points(family: str, radius: int, dimension: int) -> set[tuple[int, ...]]:
    def member(point: tuple[int, ...]) -> bool:
        if family == "cube":
            return True
        if family == "cross_polytope":
            return sum(map(abs, point)) <= radius
        if family.startswith("cross_blocks_"):
            block_dimension = int(family.rsplit("_", 1)[1])
            return all(
                sum(map(abs, point[i : i + block_dimension])) <= radius
                for i in range(0, dimension, block_dimension)
            )
        if family == "hexagon_blocks":
            return all(
                max(abs(point[i]), abs(point[i + 1]), abs(point[i] + point[i + 1]))
                <= radius
                for i in range(0, dimension, 2)
            )
        if family.startswith("hybrid_"):
            block_dimension = (
                dimension if family == "hybrid_full" else int(family.rsplit("_", 1)[1])
            )
            return all(
                sum(map(abs, point[i : i + block_dimension]))
                <= hybrid_l1_radius(radius, block_dimension)
                for i in range(0, dimension, block_dimension)
            )
        raise AssertionError(family)

    return _points(radius, dimension, member)


@pytest.mark.parametrize(
    ("family", "dimension"),
    [
        ("cube", 2),
        ("cross_polytope", 2),
        ("cross_blocks_2", 4),
        ("hexagon_blocks", 2),
        ("hybrid_full", 2),
        ("hybrid_blocks_4", 4),
    ],
)
@pytest.mark.parametrize("radius", [1, 2, 3])
@pytest.mark.parametrize("secret_radius", [0, 1])
def test_common_core_formula_matches_explicit_intersection(
    family: Family, dimension: int, radius: int, secret_radius: int
) -> None:
    source = _family_points(family, radius, dimension)
    shifted_sources = []
    for shift in integer_l1_shifts(dimension, secret_radius):
        shifted_sources.append(
            {tuple(point[i] + shift[i] for i in range(dimension)) for point in source}
        )
    common_core = set.intersection(*shifted_sources)
    metrics = common_core_metrics(family, dimension, radius, secret_radius)
    assert metrics.source_count == len(source)
    assert metrics.target_count == len(common_core)
