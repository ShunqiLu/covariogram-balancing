"""Small exact oracles for the exogenous-shift certificate and its boundary."""

from __future__ import annotations

from collections import Counter
from fractions import Fraction
from typing import Mapping, Sequence

Point = tuple[int, ...]
ProbabilityMass = Mapping[Point, Fraction]


def _add(left: Point, right: Point) -> Point:
    if len(left) != len(right):
        raise ValueError("point and shift dimensions must agree")
    return tuple(x + y for x, y in zip(left, right, strict=True))


def translate(source: frozenset[Point], shift: Point) -> frozenset[Point]:
    return frozenset(_add(point, shift) for point in source)


def common_target(
    source: frozenset[Point], shifts: Sequence[Point]
) -> frozenset[Point]:
    """Return ``intersection_u (source + u)`` exactly."""

    if not source or not shifts:
        raise ValueError("source and shifts must be nonempty")
    translated = [translate(source, shift) for shift in shifts]
    return frozenset.intersection(*translated)


def maximal_common_subdistribution(
    laws: Sequence[ProbabilityMass],
) -> tuple[Fraction, dict[Point, Fraction], tuple[dict[Point, Fraction], ...]]:
    """Return the maximum common acceptance, output law, and exact filters.

    For input laws ``mu_i``, the accepted submass is the pointwise minimum
    ``m(z) = min_i mu_i(z)``.  Its total mass is the largest common acceptance
    attainable simultaneously by shift-specific randomized filters.
    """

    if not laws:
        raise ValueError("at least one probability law is required")
    for law in laws:
        if any(mass < 0 for mass in law.values()) or sum(law.values()) != 1:
            raise ValueError("every law must be a probability mass function")

    support = set().union(*(law.keys() for law in laws))
    common_mass = {
        point: min(law.get(point, Fraction(0)) for law in laws) for point in support
    }
    common_mass = {point: mass for point, mass in common_mass.items() if mass > 0}
    acceptance = sum(common_mass.values(), start=Fraction(0))
    if acceptance == 0:
        return Fraction(0), {}, tuple({} for _ in laws)

    output_law = {
        point: mass / acceptance for point, mass in sorted(common_mass.items())
    }
    filters = tuple(
        {point: common_mass[point] / law[point] for point in sorted(common_mass)}
        for law in laws
    )
    return acceptance, output_law, filters


def exogenous_membership_law(
    source: frozenset[Point], shift: Point, target: frozenset[Point]
) -> dict[Point, Fraction]:
    """Conditional law after a fixed shift and deterministic target filter."""

    accepted = translate(source, shift) & target
    if not accepted:
        return {}
    mass = Fraction(1, len(accepted))
    return {point: mass for point in sorted(accepted)}


def endogenous_membership_law(
    source: frozenset[Point],
    shift_by_source: Mapping[Point, Point],
    target: frozenset[Point],
) -> dict[Point, Fraction]:
    """Conditional law when the shift is a deterministic function of source."""

    if set(shift_by_source) != set(source):
        raise ValueError("shift_by_source must define exactly one shift per source")
    counts = Counter(
        response
        for point in source
        if (response := _add(point, shift_by_source[point])) in target
    )
    total = sum(counts.values())
    if total == 0:
        return {}
    return {point: Fraction(count, total) for point, count in sorted(counts.items())}
