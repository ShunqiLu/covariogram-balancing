from __future__ import annotations

from fractions import Fraction

import pytest

from ehrhart_fswa.retry_interface import (
    growing_query_qrom_retry_error,
    growing_table_retry_error,
    retry_coupling_error,
    sequential_stage_error,
    stationary_retry_coupling_error,
)


def test_capped_geometric_coupling_sum_is_exact() -> None:
    acceptance = Fraction(1, 3)
    errors = [Fraction(1, 100), Fraction(2, 100), Fraction(3, 100)]
    assert retry_coupling_error(acceptance, errors) == (
        errors[0]
        + Fraction(2, 3) * errors[1]
        + Fraction(4, 9) * errors[2]
    )


def test_stationary_retry_has_one_geometric_factor() -> None:
    assert stationary_retry_coupling_error(
        Fraction(2, 5), Fraction(1, 100)
    ) == Fraction(1, 40)


def test_growing_table_closed_form_matches_long_partial_sum() -> None:
    acceptance = Fraction(1, 2)
    ratio = Fraction(1, 10_000)
    closed = growing_table_retry_error(acceptance, 7, ratio)
    partial = retry_coupling_error(
        acceptance,
        [Fraction(7 + index, 10_000) for index in range(80)],
    )
    assert closed - partial < Fraction(1, 10**20)
    assert closed == ratio * (Fraction(7, 1) / acceptance + 2)


def test_sequential_stage_error_is_multiplicative() -> None:
    errors = [Fraction(1, 10), Fraction(1, 5), Fraction(1, 4)]
    assert sequential_stage_error(errors) == Fraction(23, 50)
    assert sequential_stage_error(errors) < sum(errors)


@pytest.mark.parametrize("acceptance", [Fraction(0), Fraction(3, 2)])
def test_invalid_acceptance_is_rejected(acceptance: Fraction) -> None:
    with pytest.raises(ValueError):
        stationary_retry_coupling_error(acceptance, Fraction(0))


def test_growing_query_qrom_retry_bounds_long_geometric_sum() -> None:
    acceptance = Fraction(2, 5)
    point_probability = Fraction(1, 2**40)
    expected = growing_query_qrom_retry_error(acceptance, 11, point_probability)
    survival = 1.0 - float(acceptance)
    partial = sum(
        survival**index
        * (
            ((11 + index) * float(point_probability)) ** 0.5
            + (11 + index) * float(point_probability) / 2.0
        )
        for index in range(500)
    )
    assert partial <= expected
    assert expected - partial < 1e-6


def test_growing_query_qrom_retry_clips_trace_distance() -> None:
    assert growing_query_qrom_retry_error(Fraction(1, 10), 10, Fraction(1)) == 1
