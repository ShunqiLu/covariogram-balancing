from __future__ import annotations

import pytest

from ehrhart_fswa.counts import cross_polytope_overlap_count
from ehrhart_fswa.generating_function_experiment import integer_partitions_at_most
from ehrhart_fswa.generating_functions import (
    coordinate_numerator,
    cross_lens_generating_function,
)


@pytest.mark.parametrize("absolute_shift", range(6))
def test_coordinate_generating_function_coefficients(absolute_shift: int) -> None:
    generating_function = cross_lens_generating_function((absolute_shift,))
    for left_degree in range(10):
        for right_degree in range(10):
            brute = sum(
                abs(value) == left_degree
                and abs(value + absolute_shift) == right_degree
                for value in range(-20, 21)
            )
            assert generating_function.coefficient(left_degree, right_degree) == brute


@pytest.mark.parametrize("dimension", [1, 2, 3, 4])
def test_arbitrary_shift_rectangle_formula_matches_dp(dimension: int) -> None:
    for shift in integer_partitions_at_most(5, dimension):
        generating_function = cross_lens_generating_function(shift)
        for radius in range(9):
            assert generating_function.rectangle_sum(radius) == (
                cross_polytope_overlap_count(radius, shift)
            )


def test_coordinate_numerator_rejects_negative_input() -> None:
    with pytest.raises(ValueError):
        coordinate_numerator(-1)


def test_partition_generator_is_unique_and_canonical() -> None:
    partitions = list(integer_partitions_at_most(5, 4))
    assert len(partitions) == len(set(partitions))
    assert all(
        list(partition) == sorted(partition, reverse=True) for partition in partitions
    )
    assert all(sum(partition) <= 5 for partition in partitions)
