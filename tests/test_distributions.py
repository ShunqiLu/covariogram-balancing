from fractions import Fraction

import pytest

from ehrhart_fswa.distribution_experiment import analyze_family
from ehrhart_fswa.distributions import (
    subset_uniform_tv_distance,
    uniform_set_tv_distance,
)


def test_uniform_set_tv_formula_for_unequal_supports() -> None:
    left = {1, 2, 3, 4}
    right = {3, 4, 5}
    assert uniform_set_tv_distance(left, right) == Fraction(1, 2)


def test_nested_uniform_tv_is_rejection_mass() -> None:
    assert subset_uniform_tv_distance(7, 10) == Fraction(3, 10)


@pytest.mark.parametrize(
    "family", ["cube", "cross_polytope", "hybrid_full", "hexagon_blocks"]
)
def test_common_target_is_no_larger_than_pairwise_and_has_zero_tv(family: str) -> None:
    row = analyze_family(family, 2, 3, 1)
    assert Fraction(row.common_core_acceptance_exact) <= Fraction(
        row.minimum_pairwise_acceptance_exact
    )
    assert row.common_target_output_tv_exact == "0/1"


def test_empty_supports_are_rejected() -> None:
    with pytest.raises(ValueError):
        uniform_set_tv_distance(set(), {1})
    with pytest.raises(ValueError):
        subset_uniform_tv_distance(0, 1)
