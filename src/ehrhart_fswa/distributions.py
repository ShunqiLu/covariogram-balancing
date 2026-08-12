"""Exact finite-set distribution distances for rejection experiments."""

from __future__ import annotations

from fractions import Fraction
from typing import AbstractSet, Hashable


def uniform_set_tv_distance(
    left: AbstractSet[Hashable], right: AbstractSet[Hashable]
) -> Fraction:
    """Total variation distance between uniforms on two nonempty finite sets."""

    if not left or not right:
        raise ValueError("uniform distributions require nonempty supports")
    intersection = sum(item in right for item in left)
    return Fraction(
        max(len(left), len(right)) - intersection, max(len(left), len(right))
    )


def subset_uniform_tv_distance(subset_size: int, superset_size: int) -> Fraction:
    """TV distance between a uniform superset and a uniform nested subset."""

    if not 0 < subset_size <= superset_size:
        raise ValueError("sizes must satisfy 0 < subset_size <= superset_size")
    return Fraction(superset_size - subset_size, superset_size)
