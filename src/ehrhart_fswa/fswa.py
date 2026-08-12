"""Exact bridge from lattice geometry to a uniform FSwA rejection experiment.

For a source support ``S`` and a finite secret-shift set ``U``, define the
common target

    T = intersection_{u in U} (S + u).

If ``z`` is uniform on ``S + u`` and is accepted exactly when ``z in T``, then
the acceptance probability is ``|T|/|S|`` for every secret shift and the
conditional output is exactly uniform on ``T``.  This is stronger than, and
must not be confused with, the minimum pairwise overlap ratio.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Literal

from .counts import (
    block_hexagon_lattice_count,
    block_cross_polytope_lattice_count,
    cross_polytope_lattice_count,
    cube_lattice_count,
    hexagon_lattice_count,
    hybrid_l1_radius,
    hybrid_lattice_count,
    hybrid_max_l2_squared,
    truncated_l1_lattice_count,
    truncated_l1_max_l2_squared,
)

Family = Literal[
    "cube",
    "cross_polytope",
    "hexagon_blocks",
    "hybrid_full",
    "hybrid_blocks_4",
    "hybrid_blocks_8",
    "cross_blocks_2",
    "cross_blocks_4",
    "cross_blocks_8",
]


@dataclass(frozen=True)
class CommonCoreMetrics:
    family: Family
    dimension: int
    source_scale: int
    secret_l1_radius: int
    source_count: int
    target_count: int
    acceptance: Fraction
    expected_trials: Fraction | None
    source_max_l2_squared: int
    target_max_l2_squared: int


def _hybrid_block_dimension(family: Family, dimension: int) -> int:
    if family == "hybrid_full":
        return dimension
    if family == "hybrid_blocks_4":
        return 4
    if family == "hybrid_blocks_8":
        return 8
    raise ValueError(f"{family} is not a hybrid family")


def _cross_block_dimension(family: Family) -> int:
    if family == "cross_blocks_2":
        return 2
    if family == "cross_blocks_4":
        return 4
    if family == "cross_blocks_8":
        return 8
    raise ValueError(f"{family} is not a cross-block family")


def _validate_family_dimension(family: Family, dimension: int) -> None:
    if dimension < 1:
        raise ValueError("dimension must be positive")
    if family == "hexagon_blocks" and dimension % 2:
        raise ValueError("hexagon blocks require an even dimension")
    if family.startswith("hybrid_"):
        block_dimension = _hybrid_block_dimension(family, dimension)
        if dimension % block_dimension:
            raise ValueError(f"dimension must be divisible by {block_dimension}")
    if family.startswith("cross_blocks_"):
        block_dimension = _cross_block_dimension(family)
        if dimension % block_dimension:
            raise ValueError(f"dimension must be divisible by {block_dimension}")


def common_core_metrics(
    family: Family,
    dimension: int,
    source_scale: int,
    secret_l1_radius: int,
) -> CommonCoreMetrics:
    """Compute exact common-target rejection metrics for an l1 secret set."""

    _validate_family_dimension(family, dimension)
    if source_scale < 0:
        raise ValueError("source_scale must be nonnegative")
    if secret_l1_radius < 0:
        raise ValueError("secret_l1_radius must be nonnegative")

    target_scale = source_scale - secret_l1_radius
    if family == "cube":
        source_count = cube_lattice_count(source_scale, dimension)
        target_count = (
            cube_lattice_count(target_scale, dimension) if target_scale >= 0 else 0
        )
        source_norm = dimension * source_scale**2
        target_norm = dimension * max(target_scale, 0) ** 2
    elif family == "cross_polytope":
        source_count = cross_polytope_lattice_count(source_scale, dimension)
        target_count = (
            cross_polytope_lattice_count(target_scale, dimension)
            if target_scale >= 0
            else 0
        )
        source_norm = source_scale**2
        target_norm = max(target_scale, 0) ** 2
    elif family.startswith("cross_blocks_"):
        block_dimension = _cross_block_dimension(family)
        blocks = dimension // block_dimension
        source_count = block_cross_polytope_lattice_count(
            source_scale, dimension, block_dimension
        )
        target_count = (
            block_cross_polytope_lattice_count(target_scale, dimension, block_dimension)
            if target_scale >= 0
            else 0
        )
        source_norm = blocks * source_scale**2
        target_norm = blocks * max(target_scale, 0) ** 2
    elif family == "hexagon_blocks":
        source_count = block_hexagon_lattice_count(source_scale, dimension)
        target_count = (
            block_hexagon_lattice_count(target_scale, dimension)
            if target_scale >= 0
            else 0
        )
        source_norm = dimension * source_scale**2
        target_norm = dimension * max(target_scale, 0) ** 2
    else:
        block_dimension = _hybrid_block_dimension(family, dimension)
        blocks = dimension // block_dimension
        source_block_count = hybrid_lattice_count(source_scale, block_dimension)
        source_count = source_block_count**blocks
        source_block_norm = hybrid_max_l2_squared(source_scale, block_dimension)
        source_norm = blocks * source_block_norm

        source_l1 = hybrid_l1_radius(source_scale, block_dimension)
        target_coordinate_radius = source_scale - secret_l1_radius
        target_l1_radius = source_l1 - secret_l1_radius
        if target_coordinate_radius < 0 or target_l1_radius < 0:
            target_count = 0
            target_norm = 0
        else:
            target_block_count = truncated_l1_lattice_count(
                target_coordinate_radius,
                block_dimension,
                target_l1_radius,
            )
            target_count = target_block_count**blocks
            target_block_norm = truncated_l1_max_l2_squared(
                target_coordinate_radius,
                block_dimension,
                target_l1_radius,
            )
            target_norm = blocks * target_block_norm

    acceptance = Fraction(target_count, source_count)
    expected_trials = Fraction(source_count, target_count) if target_count else None
    return CommonCoreMetrics(
        family=family,
        dimension=dimension,
        source_scale=source_scale,
        secret_l1_radius=secret_l1_radius,
        source_count=source_count,
        target_count=target_count,
        acceptance=acceptance,
        expected_trials=expected_trials,
        source_max_l2_squared=source_norm,
        target_max_l2_squared=target_norm,
    )
