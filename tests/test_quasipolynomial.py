from math import comb

from ehrhart_fswa.counts import cube_overlap_count
from ehrhart_fswa.quasipolynomial import (
    discover_from_counter,
    fit_quasipolynomial_candidate,
)


def test_discovers_eventual_cube_overlap_polynomial() -> None:
    candidate, values = discover_from_counter(
        lambda t: cube_overlap_count(t, (2, 0, 0, 0)),
        degree=4,
        checked_through=30,
    )
    assert candidate is not None
    assert candidate.period == 1
    assert candidate.onset == 1
    assert all(candidate.evaluate(t) == values[t] for t in range(1, 31))


def test_discovers_period_two_quasipolynomial() -> None:
    # Degree two in k on each parity class, deliberately not one polynomial in t.
    values = {t: (3 * comb(t // 2, 2) + 2 * (t // 2) + (t % 2)) for t in range(31)}
    candidate = fit_quasipolynomial_candidate(
        values, degree=2, max_period=3, max_onset=0
    )
    assert candidate is not None
    assert candidate.period == 2
    assert candidate.onset == 0
    assert all(candidate.evaluate(t) == values[t] for t in values)


def test_rejects_sequence_outside_search_model() -> None:
    values = {t: 2**t for t in range(31)}
    assert (
        fit_quasipolynomial_candidate(values, degree=3, max_period=3, max_onset=2)
        is None
    )
