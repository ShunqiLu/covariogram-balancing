from __future__ import annotations

from collections import defaultdict
from fractions import Fraction

from ehrhart_fswa.rom_interface import (
    fiber_hit_bound,
    freshness_certificate,
    max_fiber_size,
    prequery_hit_probability,
    transcript_averaged_fiber_bound,
)


def _tv(left: dict[tuple[int, int], Fraction], right: dict[tuple[int, int], Fraction]) -> Fraction:
    support = set(left) | set(right)
    distance = Fraction()
    for point in support:
        distance += abs(left.get(point, Fraction()) - right.get(point, Fraction()))
    return distance / Fraction(2)


def test_fiber_and_hit_bounds_are_exact_on_a_small_source() -> None:
    source = tuple(range(8))
    commitment = lambda y: y % 3
    queried = {0, 2}
    assert max_fiber_size(source, commitment) == 3
    assert prequery_hit_probability(source, commitment, queried) == Fraction(5, 8)
    assert fiber_hit_bound(8, len(queried), 3) == Fraction(3, 4)


def test_fresh_query_conditioned_law_obeys_eta_over_a_bound() -> None:
    # S={0,1,2,3}, challenge bits {0,1}, and shifts phi(c)=c.
    # Input 0 is already queried with H(0)=0; input 1 is fresh uniform.
    source = tuple(range(4))
    target = {1, 2, 3}
    real: defaultdict[tuple[int, int], Fraction] = defaultdict(Fraction)
    accepted_probability = Fraction()
    for y in source:
        oracle_input = y % 2
        challenge_probabilities = {0: Fraction(1)} if oracle_input == 0 else {
            0: Fraction(1, 2),
            1: Fraction(1, 2),
        }
        for challenge, challenge_probability in challenge_probabilities.items():
            response = y + challenge
            mass = Fraction(1, len(source)) * challenge_probability
            if response in target:
                real[(challenge, response)] += mass
                accepted_probability += mass
    real_conditioned = {
        point: mass / accepted_probability for point, mass in real.items()
    }
    ideal = {
        (challenge, response): Fraction(1, 2 * len(target))
        for challenge in (0, 1)
        for response in target
    }

    eta = Fraction(1, 2)
    certificate = freshness_certificate(4, 3, eta)
    assert abs(accepted_probability - certificate.ideal_acceptance) <= eta
    assert _tv(real_conditioned, ideal) <= certificate.accepted_transcript_tv_bound


def test_adaptive_transcript_fiber_bound_is_probability_weighted() -> None:
    cases = (
        (Fraction(1, 4), 16, 1, 2),
        (Fraction(3, 4), 16, 3, 4),
    )
    assert transcript_averaged_fiber_bound(cases) == Fraction(19, 32)
