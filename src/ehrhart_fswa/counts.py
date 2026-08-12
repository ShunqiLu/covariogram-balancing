"""Exact lattice-point and translated-overlap counts.

The overlap convention is

    N_P(t, u) = |{x in Z^n : x in tP and x + u in tP}|.

This equals ``|S_t intersection (S_t - u)|``.
"""

from __future__ import annotations

from functools import lru_cache
from math import comb
from typing import Sequence


def _validate_radius_dimension(radius: int, dimension: int) -> None:
    if radius < 0:
        raise ValueError("radius must be nonnegative")
    if dimension < 1:
        raise ValueError("dimension must be positive")


def cube_lattice_count(radius: int, dimension: int) -> int:
    """Return ``|[-radius, radius]^dimension intersection Z^dimension|``."""

    _validate_radius_dimension(radius, dimension)
    return (2 * radius + 1) ** dimension


def cube_overlap_count(radius: int, shift: Sequence[int]) -> int:
    """Exact translated overlap for an integer cube."""

    _validate_radius_dimension(radius, len(shift))
    side = 2 * radius + 1
    result = 1
    for coordinate in shift:
        result *= max(0, side - abs(int(coordinate)))
    return result


def cross_polytope_lattice_count(radius: int, dimension: int) -> int:
    """Count integer points in ``{x : ||x||_1 <= radius}``.

    The exact Ehrhart polynomial is

        sum_{j=0}^{min(dimension, radius)} 2^j C(dimension,j) C(radius,j).
    """

    _validate_radius_dimension(radius, dimension)
    return sum(
        2**j * comb(dimension, j) * comb(radius, j)
        for j in range(min(dimension, radius) + 1)
    )


def cross_polytope_overlap_count(radius: int, shift: Sequence[int]) -> int:
    """Exact translated overlap for an integer cross-polytope.

    The implementation multiplies per-coordinate bivariate generating
    functions, retaining only coefficients with both degrees at most
    ``radius``. Symmetry under signed coordinate permutations is cached.
    """

    _validate_radius_dimension(radius, len(shift))
    canonical_shift = tuple(sorted((abs(int(x)) for x in shift), reverse=True))
    return _cross_polytope_overlap_canonical(radius, canonical_shift)


def hybrid_l1_radius(coordinate_radius: int, dimension: int) -> int:
    """Return ``floor(coordinate_radius * sqrt(dimension))`` exactly."""

    from math import isqrt

    _validate_radius_dimension(coordinate_radius, dimension)
    return isqrt(coordinate_radius * coordinate_radius * dimension)


def truncated_l1_lattice_count(
    coordinate_radius: int, dimension: int, l1_radius: int
) -> int:
    """Count ``|x_i| <= coordinate_radius`` and ``||x||_1 <= l1_radius``.

    The generating function is

    ``(1 + 2 z + ... + 2 z^coordinate_radius)^dimension``.

    A sliding window evaluates its coefficients through degree ``l1_radius``
    in ``O(dimension * l1_radius)`` integer operations.
    """

    _validate_radius_dimension(coordinate_radius, dimension)
    if l1_radius < 0:
        raise ValueError("l1_radius must be nonnegative")
    effective_l1_radius = min(l1_radius, coordinate_radius * dimension)
    return _truncated_l1_lattice_count_cached(
        coordinate_radius, dimension, effective_l1_radius
    )


@lru_cache(maxsize=None)
def _truncated_l1_lattice_count_cached(
    coordinate_radius: int, dimension: int, l1_radius: int
) -> int:
    coefficients = [0] * (l1_radius + 1)
    coefficients[0] = 1
    for _ in range(dimension):
        prefix = [0]
        running = 0
        for coefficient in coefficients:
            running += coefficient
            prefix.append(running)
        updated = [0] * (l1_radius + 1)
        for degree in range(l1_radius + 1):
            lower = max(0, degree - coordinate_radius)
            positive_part = prefix[degree] - prefix[lower]
            updated[degree] = coefficients[degree] + 2 * positive_part
        coefficients = updated
    return sum(coefficients)


def hybrid_lattice_count(coordinate_radius: int, dimension: int) -> int:
    """Count the PATRONUS-style hybrid ``B_inf(r) intersect B_1(r sqrt(n))``."""

    return truncated_l1_lattice_count(
        coordinate_radius,
        dimension,
        hybrid_l1_radius(coordinate_radius, dimension),
    )


def hybrid_overlap_count(coordinate_radius: int, shift: Sequence[int]) -> int:
    """Exact translated overlap for the PATRONUS-style hybrid polytope."""

    _validate_radius_dimension(coordinate_radius, len(shift))
    canonical_shift = tuple(sorted((abs(int(x)) for x in shift), reverse=True))
    return _hybrid_overlap_canonical(
        coordinate_radius,
        hybrid_l1_radius(coordinate_radius, len(shift)),
        canonical_shift,
    )


@lru_cache(maxsize=None)
def _hybrid_overlap_canonical(
    coordinate_radius: int,
    l1_radius: int,
    canonical_shift: tuple[int, ...],
) -> int:
    if sum(canonical_shift) > 2 * l1_radius:
        return 0

    coefficients: dict[tuple[int, int], int] = {(0, 0): 1}
    for coordinate_shift in canonical_shift:
        coordinate_terms: dict[tuple[int, int], int] = {}
        lower = max(-coordinate_radius, -coordinate_radius - coordinate_shift)
        upper = min(coordinate_radius, coordinate_radius - coordinate_shift)
        for value in range(lower, upper + 1):
            degree = (abs(value), abs(value + coordinate_shift))
            coordinate_terms[degree] = coordinate_terms.get(degree, 0) + 1

        updated: dict[tuple[int, int], int] = {}
        for (left_degree, right_degree), coefficient in coefficients.items():
            for (
                left_increment,
                right_increment,
            ), multiplicity in coordinate_terms.items():
                new_left = left_degree + left_increment
                new_right = right_degree + right_increment
                if new_left <= l1_radius and new_right <= l1_radius:
                    key = (new_left, new_right)
                    updated[key] = updated.get(key, 0) + coefficient * multiplicity
        coefficients = updated
        if not coefficients:
            return 0
    return sum(coefficients.values())


def truncated_l1_max_l2_squared(
    coordinate_radius: int, dimension: int, l1_radius: int
) -> int:
    """Exact maximum squared Euclidean norm in a truncated integer l1 ball."""

    _validate_radius_dimension(coordinate_radius, dimension)
    if l1_radius < 0:
        raise ValueError("l1_radius must be nonnegative")
    if coordinate_radius == 0:
        return 0
    available = min(l1_radius, coordinate_radius * dimension)
    full_coordinates, remainder = divmod(available, coordinate_radius)
    if full_coordinates >= dimension:
        return dimension * coordinate_radius * coordinate_radius
    return (
        full_coordinates * coordinate_radius * coordinate_radius + remainder * remainder
    )


def hybrid_max_l2_squared(coordinate_radius: int, dimension: int) -> int:
    """Exact lattice maximum squared norm of the hybrid polytope."""

    return truncated_l1_max_l2_squared(
        coordinate_radius,
        dimension,
        hybrid_l1_radius(coordinate_radius, dimension),
    )


@lru_cache(maxsize=None)
def _cross_polytope_overlap_canonical(
    radius: int, canonical_shift: tuple[int, ...]
) -> int:
    if sum(canonical_shift) > 2 * radius:
        return 0

    # Keys are the accumulated (||x||_1, ||x+u||_1) bidegrees.
    coefficients: dict[tuple[int, int], int] = {(0, 0): 1}
    for coordinate_shift in canonical_shift:
        coordinate_terms: dict[tuple[int, int], int] = {}
        lower = max(-radius, -radius - coordinate_shift)
        upper = min(radius, radius - coordinate_shift)
        for value in range(lower, upper + 1):
            degree = (abs(value), abs(value + coordinate_shift))
            coordinate_terms[degree] = coordinate_terms.get(degree, 0) + 1

        updated: dict[tuple[int, int], int] = {}
        for (left_degree, right_degree), coefficient in coefficients.items():
            for (
                left_increment,
                right_increment,
            ), multiplicity in coordinate_terms.items():
                new_left = left_degree + left_increment
                new_right = right_degree + right_increment
                if new_left <= radius and new_right <= radius:
                    key = (new_left, new_right)
                    updated[key] = updated.get(key, 0) + coefficient * multiplicity
        coefficients = updated
        if not coefficients:
            return 0

    return sum(coefficients.values())


def _in_hexagon(radius: int, point: tuple[int, int]) -> bool:
    x, y = point
    return max(abs(x), abs(y), abs(x + y)) <= radius


def hexagon_lattice_count(radius: int) -> int:
    """Count points in ``|x|, |y|, |x+y| <= radius``."""

    _validate_radius_dimension(radius, 2)
    return 3 * radius * radius + 3 * radius + 1


@lru_cache(maxsize=None)
def hexagon_overlap_count(radius: int, shift: tuple[int, int]) -> int:
    """Exact translated overlap for the two-dimensional hexagonal block."""

    _validate_radius_dimension(radius, 2)
    ux, uy = (int(shift[0]), int(shift[1]))
    count = 0
    for x in range(-radius, radius + 1):
        for y in range(-radius, radius + 1):
            if _in_hexagon(radius, (x, y)) and _in_hexagon(radius, (x + ux, y + uy)):
                count += 1
    return count


def block_hexagon_lattice_count(radius: int, dimension: int) -> int:
    """Count points in a Cartesian power of the two-dimensional hexagon."""

    _validate_radius_dimension(radius, dimension)
    if dimension % 2:
        raise ValueError("hexagonal block products require an even dimension")
    return hexagon_lattice_count(radius) ** (dimension // 2)


def block_hexagon_overlap_count(radius: int, shift: Sequence[int]) -> int:
    """Exact overlap for a Cartesian product of two-dimensional hexagons."""

    _validate_radius_dimension(radius, len(shift))
    if len(shift) % 2:
        raise ValueError("hexagonal block products require an even dimension")
    result = 1
    for offset in range(0, len(shift), 2):
        result *= hexagon_overlap_count(
            radius, (int(shift[offset]), int(shift[offset + 1]))
        )
    return result


def block_cross_polytope_lattice_count(
    radius: int, dimension: int, block_dimension: int
) -> int:
    """Count a Cartesian product of fixed-dimensional cross-polytopes."""

    _validate_radius_dimension(radius, dimension)
    if block_dimension < 1 or dimension % block_dimension:
        raise ValueError("block dimension must be positive and divide dimension")
    return cross_polytope_lattice_count(radius, block_dimension) ** (
        dimension // block_dimension
    )


def block_cross_polytope_overlap_count(
    radius: int, shift: Sequence[int], block_dimension: int
) -> int:
    """Exact overlap for a Cartesian product of cross-polytope blocks."""

    _validate_radius_dimension(radius, len(shift))
    if block_dimension < 1 or len(shift) % block_dimension:
        raise ValueError("block dimension must be positive and divide dimension")
    result = 1
    for offset in range(0, len(shift), block_dimension):
        result *= cross_polytope_overlap_count(
            radius, shift[offset : offset + block_dimension]
        )
    return result
