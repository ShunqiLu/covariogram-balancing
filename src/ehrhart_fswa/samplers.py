"""Exact rank/unrank samplers backed by lattice-point counts.

These routines provide a reproducible uniform-sampling reference. They are not
claimed to be constant-time or side-channel hardened.
"""

from __future__ import annotations

from random import Random
from typing import Sequence

from .counts import truncated_l1_lattice_count


def _completion_count(
    coordinate_radius: int, remaining_dimension: int, remaining_l1: int
) -> int:
    if remaining_l1 < 0:
        return 0
    if remaining_dimension == 0:
        return 1
    return truncated_l1_lattice_count(
        coordinate_radius, remaining_dimension, remaining_l1
    )


def unrank_truncated_l1(
    rank: int, coordinate_radius: int, dimension: int, l1_radius: int
) -> tuple[int, ...]:
    """Map an integer rank bijectively to a truncated-l1 lattice point."""

    total = truncated_l1_lattice_count(coordinate_radius, dimension, l1_radius)
    if not 0 <= rank < total:
        raise ValueError(f"rank must lie in [0,{total})")
    point = []
    remaining_l1 = l1_radius
    for index in range(dimension):
        remaining_dimension = dimension - index - 1
        for value in range(-coordinate_radius, coordinate_radius + 1):
            completions = _completion_count(
                coordinate_radius,
                remaining_dimension,
                remaining_l1 - abs(value),
            )
            if rank < completions:
                point.append(value)
                remaining_l1 -= abs(value)
                break
            rank -= completions
        else:
            raise AssertionError("count/unrank inconsistency")
    return tuple(point)


def rank_truncated_l1(
    point: Sequence[int], coordinate_radius: int, l1_radius: int
) -> int:
    """Return the inverse lexicographic rank of a truncated-l1 point."""

    dimension = len(point)
    if dimension < 1:
        raise ValueError("point must have positive dimension")
    if any(abs(int(value)) > coordinate_radius for value in point):
        raise ValueError("point exceeds the coordinate bound")
    if sum(abs(int(value)) for value in point) > l1_radius:
        raise ValueError("point exceeds the l1 bound")
    rank = 0
    remaining_l1 = l1_radius
    for index, raw_value in enumerate(point):
        value = int(raw_value)
        remaining_dimension = dimension - index - 1
        for earlier in range(-coordinate_radius, value):
            rank += _completion_count(
                coordinate_radius,
                remaining_dimension,
                remaining_l1 - abs(earlier),
            )
        remaining_l1 -= abs(value)
    return rank


def sample_truncated_l1(
    rng: Random, coordinate_radius: int, dimension: int, l1_radius: int
) -> tuple[int, ...]:
    """Draw exactly uniformly using one uniform rank."""

    total = truncated_l1_lattice_count(coordinate_radius, dimension, l1_radius)
    return unrank_truncated_l1(
        rng.randrange(total), coordinate_radius, dimension, l1_radius
    )
