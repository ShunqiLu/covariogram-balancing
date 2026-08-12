from fractions import Fraction

import pytest

from ehrhart_fswa.mldsa_case import (
    PARAMETER_SETS,
    analyze_parameter_set,
    interval_common_target,
)


def test_interval_common_target_matches_direct_intersection() -> None:
    gamma1, beta = 7, 2
    source = set(range(-gamma1 + 1, gamma1 + 1))
    direct = set.intersection(
        *(set(value + offset for value in source) for offset in range(-beta, beta + 1))
    )
    maximal, fips = interval_common_target(gamma1, beta)
    assert direct == set(range(maximal[0], maximal[1] + 1))
    assert set(range(fips[0], fips[1] + 1)) < direct


@pytest.mark.parametrize("parameters", PARAMETER_SETS)
def test_mldsa_exact_probability(parameters) -> None:
    row = analyze_parameter_set(parameters)
    expected = Fraction(parameters.gamma1 - parameters.beta, parameters.gamma1)
    assert Fraction(row.maximal_acceptance_exact) == expected ** (256 * parameters.ell)
    assert row.source_coefficient_count == 2 * parameters.gamma1
    assert row.maximal_common_coefficient_count == 2 * (
        parameters.gamma1 - parameters.beta
    )
    assert row.fips_z_coefficient_count == 2 * (
        parameters.gamma1 - parameters.beta
    ) - 1


def test_invalid_interval_parameters() -> None:
    with pytest.raises(ValueError):
        interval_common_target(3, 3)


def test_fips_pdf_and_potential_update_repetition_values_are_distinct() -> None:
    rows = [analyze_parameter_set(parameters) for parameters in PARAMETER_SETS]
    assert [row.fips_pdf_average_repetitions_all_checks for row in rows] == [
        4.25,
        5.10,
        3.85,
    ]
    assert [
        row.potential_updates_average_repetitions_all_checks for row in rows
    ] == [4.36, 5.14, 3.91]
