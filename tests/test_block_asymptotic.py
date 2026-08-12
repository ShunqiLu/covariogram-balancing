from fractions import Fraction
from math import comb
from typing import Literal

import pytest

from ehrhart_fswa.block_asymptotic import (
    base_count,
    fixed_block_acceptance,
    hstar_acceptance_bounds,
    hstar_degree_bounds,
    hstar_erosion_ratio,
    hstar_mean,
    hstar_mlr_dominates,
    hstar_vector_from_ehrhart_values,
)
from ehrhart_fswa.counts import cross_polytope_lattice_count


def test_fixed_block_factorization() -> None:
    expected = (
        Fraction(
            cross_polytope_lattice_count(8, 4), cross_polytope_lattice_count(10, 4)
        )
        ** 3
    )
    assert fixed_block_acceptance("cross", 4, 3, 10, 2) == expected


def test_hexagon_dimension_validation() -> None:
    with pytest.raises(ValueError):
        fixed_block_acceptance("hexagon", 4, 2, 10, 2)


@pytest.mark.parametrize(
    ("family", "block_dimension"),
    [("cube", 1), ("cube", 4), ("cross", 2), ("cross", 4), ("hexagon", 2)],
)
def test_hstar_bounds_contain_named_integral_blocks(
    family: Literal["cube", "cross", "hexagon"], block_dimension: int
) -> None:
    for blocks in (1, 3, 8):
        for erosion in (1, 2, 3):
            for scale in range(
                erosion + block_dimension, erosion + block_dimension + 8
            ):
                lower, upper = hstar_acceptance_bounds(
                    block_dimension, blocks, scale, erosion
                )
                actual = fixed_block_acceptance(
                    family, block_dimension, blocks, scale, erosion
                )
                assert lower <= actual <= upper


@pytest.mark.parametrize(
    ("family", "block_dimension"),
    [("cube", 1), ("cube", 4), ("cross", 2), ("cross", 4), ("hexagon", 2)],
)
def test_hstar_barycentric_identity_for_named_blocks(
    family: Literal["cube", "cross", "hexagon"], block_dimension: int
) -> None:
    values = [
        base_count(family, block_dimension, scale)
        for scale in range(block_dimension + 1)
    ]
    hstar = hstar_vector_from_ehrhart_values(values)
    assert hstar[0] == 1
    assert all(value >= 0 for value in hstar)
    for erosion in (1, 2, 3):
        for scale in range(erosion + block_dimension, erosion + block_dimension + 8):
            assert hstar_erosion_ratio(hstar, scale, erosion) == Fraction(
                base_count(family, block_dimension, scale - erosion),
                base_count(family, block_dimension, scale),
            )
            refined_lower, refined_upper = hstar_degree_bounds(hstar, scale, erosion)
            actual = hstar_erosion_ratio(hstar, scale, erosion)
            assert refined_lower <= actual <= refined_upper
            assert refined_lower < actual < refined_upper


def test_hstar_mean_encodes_normalized_boundary_coefficient() -> None:
    # Cross-polytope h*=(1+x)^b has mean b/2, so c_(b-1)/(b vol)=1/2.
    for dimension in range(1, 7):
        hstar = tuple(comb(dimension, index) for index in range(dimension + 1))
        assert hstar_mean(hstar) == Fraction(dimension, 2)
        normalized_boundary = Fraction(dimension + 1, 2) - hstar_mean(hstar)
        assert normalized_boundary == Fraction(1, 2)


def test_reeve_hstar_likelihood_ratio_order_is_scale_uniform() -> None:
    # The Reeve tetrahedron R_m has h* = (1, 0, m-1, 0).
    for smaller_height, larger_height in ((1, 2), (2, 3), (3, 9)):
        smaller = (1, 0, smaller_height - 1, 0)
        larger = (1, 0, larger_height - 1, 0)
        assert hstar_mlr_dominates(larger, smaller)
        for erosion in (1, 2, 4):
            for scale in range(erosion + 3, erosion + 14):
                assert hstar_erosion_ratio(
                    larger, scale, erosion
                ) <= hstar_erosion_ratio(smaller, scale, erosion)


def test_hstar_likelihood_ratio_validation() -> None:
    with pytest.raises(ValueError):
        hstar_mlr_dominates((1, 0), (1, 0, 0))
    with pytest.raises(ValueError):
        hstar_mlr_dominates((0, 0), (1, 0))
