"""Exact arithmetic helpers for the classical-ROM freshness interface."""

from __future__ import annotations

from collections import Counter
from collections.abc import Callable, Collection, Hashable, Iterable, Sequence
from dataclasses import dataclass
from fractions import Fraction
from typing import TypeVar


SourcePoint = TypeVar("SourcePoint")
OracleInput = TypeVar("OracleInput", bound=Hashable)


@dataclass(frozen=True)
class FreshnessCertificate:
    ideal_acceptance: Fraction
    prequery_hit_probability: Fraction
    acceptance_deviation_bound: Fraction
    accepted_transcript_tv_bound: Fraction


def max_fiber_size(
    source: Sequence[SourcePoint],
    commitment: Callable[[SourcePoint], OracleInput],
) -> int:
    """Return ``max_x |{y: commitment(y)=x}|`` for a finite source."""

    if not source:
        raise ValueError("source must be nonempty")
    multiplicities = Counter(commitment(point) for point in source)
    return max(multiplicities.values())


def prequery_hit_probability(
    source: Sequence[SourcePoint],
    commitment: Callable[[SourcePoint], OracleInput],
    prequeried: Collection[OracleInput],
) -> Fraction:
    """Compute the exact hit probability for a uniform finite source."""

    if not source:
        raise ValueError("source must be nonempty")
    hits = sum(commitment(point) in prequeried for point in source)
    return Fraction(hits, len(source))


def fiber_hit_bound(
    source_size: int, prequery_count: int, maximum_fiber_size: int
) -> Fraction:
    """Return ``min(1, q_H M / |S|)`` from the fiber union bound."""

    if source_size <= 0:
        raise ValueError("source_size must be positive")
    if prequery_count < 0 or maximum_fiber_size < 0:
        raise ValueError("counts must be nonnegative")
    return min(
        Fraction(1),
        Fraction(prequery_count * maximum_fiber_size, source_size),
    )


def transcript_averaged_fiber_bound(
    cases: Iterable[tuple[Fraction, int, int, int]],
) -> Fraction:
    """Evaluate the adaptive-transcript fiber bound exactly.

    Each case is ``(probability, source_size, prequery_count,
    maximum_fiber_size)``.  Case probabilities must form a distribution.
    """

    total_probability = Fraction()
    expected_bound = Fraction()
    for probability, source_size, prequery_count, maximum_fiber_size in cases:
        if probability < 0:
            raise ValueError("case probabilities must be nonnegative")
        total_probability += probability
        expected_bound += probability * fiber_hit_bound(
            source_size, prequery_count, maximum_fiber_size
        )
    if total_probability != 1:
        raise ValueError("case probabilities must sum to one")
    return expected_bound


def freshness_certificate(
    source_size: int, target_size: int, prequery_hit: Fraction
) -> FreshnessCertificate:
    """Instantiate the theorem's ``eta`` and ``eta/a`` bounds exactly."""

    if source_size <= 0 or not 0 < target_size <= source_size:
        raise ValueError("require 0 < target_size <= source_size")
    if not 0 <= prequery_hit <= 1:
        raise ValueError("prequery_hit must be a probability")
    acceptance = Fraction(target_size, source_size)
    if prequery_hit >= acceptance:
        raise ValueError("the freshness theorem requires eta < a")
    return FreshnessCertificate(
        ideal_acceptance=acceptance,
        prequery_hit_probability=prequery_hit,
        acceptance_deviation_bound=prequery_hit,
        accepted_transcript_tv_bound=prequery_hit / acceptance,
    )
