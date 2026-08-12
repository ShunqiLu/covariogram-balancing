"""Exact error accounting for restart-until-accept certificates."""

from __future__ import annotations

from fractions import Fraction
from math import sqrt
from typing import Sequence


def retry_coupling_error(
    ideal_acceptance: Fraction,
    per_round_errors: Sequence[Fraction],
) -> Fraction:
    """Return ``sum_i (1-a)^i e_i`` for zero-indexed retry errors.

    The quantity is the exact union-of-couplings bound through the supplied
    number of rounds.  It applies to the joint stopping-time/output law and
    includes the ideal failure symbol when the list represents a retry cap.
    """

    if not 0 < ideal_acceptance <= 1:
        raise ValueError("ideal_acceptance must lie in (0,1]")
    if any(error < 0 for error in per_round_errors):
        raise ValueError("per-round errors must be nonnegative")
    survival = 1 - ideal_acceptance
    weight = Fraction(1)
    total = Fraction(0)
    for error in per_round_errors:
        total += weight * error
        weight *= survival
    return min(Fraction(1), total)


def stationary_retry_coupling_error(
    ideal_acceptance: Fraction,
    per_round_error: Fraction,
) -> Fraction:
    """Infinite-retry bound for a uniform conditional trial error."""

    if not 0 < ideal_acceptance <= 1:
        raise ValueError("ideal_acceptance must lie in (0,1]")
    if per_round_error < 0:
        raise ValueError("per_round_error must be nonnegative")
    return min(Fraction(1), per_round_error / ideal_acceptance)


def growing_table_retry_error(
    ideal_acceptance: Fraction,
    initial_queries: int,
    maximum_fiber_ratio: Fraction,
    source_error_per_round: Fraction = Fraction(0),
) -> Fraction:
    """Infinite-retry ROM error with one new challenge input per rejection.

    Round ``i`` (starting at zero) has the fiber hit certificate
    ``(initial_queries+i)*maximum_fiber_ratio``.  Summing it against the
    ideal geometric survival weights gives

    ``ratio*(q0/a + (1-a)/a**2) + source_error/a``.
    """

    if not 0 < ideal_acceptance <= 1:
        raise ValueError("ideal_acceptance must lie in (0,1]")
    if initial_queries < 0:
        raise ValueError("initial_queries must be nonnegative")
    if maximum_fiber_ratio < 0 or source_error_per_round < 0:
        raise ValueError("error inputs must be nonnegative")
    acceptance = ideal_acceptance
    survival = 1 - acceptance
    challenge = maximum_fiber_ratio * (
        Fraction(initial_queries, 1) / acceptance
        + survival / acceptance**2
    )
    source = source_error_per_round / acceptance
    return min(Fraction(1), challenge + source)


def growing_query_qrom_retry_error(
    ideal_acceptance: Fraction,
    initial_queries: int,
    maximum_point_probability: Fraction,
) -> float:
    """Closed quantum-retry bound from tight adaptive reprogramming.

    With ``p=maximum_point_probability``, round ``i`` (starting at zero)
    contributes the exact one-reprogramming error
    ``sqrt((initial_queries+i)*p) + (initial_queries+i)*p/2`` from
    GHHM21, Theorem 1, equation (2).  Jensen's inequality for the geometric
    failure count gives the closed upper bound returned here.  The result is
    clipped at one because it bounds trace distance.
    """

    if not 0 < ideal_acceptance <= 1:
        raise ValueError("ideal_acceptance must lie in (0,1]")
    if initial_queries < 0:
        raise ValueError("initial_queries must be nonnegative")
    if not 0 <= maximum_point_probability <= 1:
        raise ValueError("maximum_point_probability must lie in [0,1]")
    acceptance = float(ideal_acceptance)
    survival = 1.0 - acceptance
    point_probability = float(maximum_point_probability)
    square_root_series = (
        sqrt(point_probability)
        / acceptance
        * sqrt(initial_queries + survival / acceptance)
    )
    linear_series = point_probability / 2.0 * (
        initial_queries / acceptance + survival / acceptance**2
    )
    return min(1.0, square_root_series + linear_series)


def sequential_stage_error(stage_errors: Sequence[Fraction]) -> Fraction:
    """Failure probability of sequential conditional stage couplings.

    If stage ``j`` can be coupled except with conditional probability
    ``e_j``, all stages agree with probability at least ``prod(1-e_j)``.
    """

    if any(not 0 <= error <= 1 for error in stage_errors):
        raise ValueError("stage errors must lie in [0,1]")
    success = Fraction(1)
    for error in stage_errors:
        success *= 1 - error
    return 1 - success
