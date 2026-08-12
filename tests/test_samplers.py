from random import Random

import pytest

from ehrhart_fswa.counts import truncated_l1_lattice_count
from ehrhart_fswa.samplers import (
    rank_truncated_l1,
    sample_truncated_l1,
    unrank_truncated_l1,
)


@pytest.mark.parametrize("dimension", [1, 2, 3, 4])
@pytest.mark.parametrize("coordinate_radius", [0, 1, 2])
def test_rank_unrank_is_a_bijection(coordinate_radius: int, dimension: int) -> None:
    l1_radius = coordinate_radius * dimension // 2 + 1
    total = truncated_l1_lattice_count(coordinate_radius, dimension, l1_radius)
    points = [
        unrank_truncated_l1(rank, coordinate_radius, dimension, l1_radius)
        for rank in range(total)
    ]
    assert len(points) == len(set(points)) == total
    assert [
        rank_truncated_l1(point, coordinate_radius, l1_radius) for point in points
    ] == list(range(total))


def test_seeded_sampler_is_reproducible_and_valid() -> None:
    left = Random(7)
    right = Random(7)
    samples_left = [sample_truncated_l1(left, 3, 4, 5) for _ in range(20)]
    samples_right = [sample_truncated_l1(right, 3, 4, 5) for _ in range(20)]
    assert samples_left == samples_right
    assert all(max(map(abs, point)) <= 3 for point in samples_left)
    assert all(sum(map(abs, point)) <= 5 for point in samples_left)


@pytest.mark.parametrize(
    "call",
    [
        lambda: unrank_truncated_l1(-1, 1, 2, 2),
        lambda: unrank_truncated_l1(100, 1, 2, 2),
        lambda: rank_truncated_l1((2, 0), 1, 2),
        lambda: rank_truncated_l1((1, 1), 2, 1),
    ],
)
def test_invalid_rank_inputs_raise(call) -> None:
    with pytest.raises(ValueError):
        call()
