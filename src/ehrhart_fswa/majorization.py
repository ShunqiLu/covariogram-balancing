"""Majorization certificates for discrete Lee-ball correlations."""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from itertools import product
from typing import Sequence

from ehrhart_fswa.counts import cross_polytope_lattice_count


def canonical_shift(shift: Sequence[int]) -> tuple[int, ...]:
    """Return the decreasing absolute-coordinate partition of ``shift``."""

    if not shift:
        raise ValueError("shift must have positive dimension")
    return tuple(sorted((abs(int(value)) for value in shift), reverse=True))


def majorizes(left: Sequence[int], right: Sequence[int]) -> bool:
    """Return whether ``left`` majorizes ``right`` after absolute sorting."""

    left_partition = canonical_shift(left)
    right_partition = canonical_shift(right)
    if len(left_partition) != len(right_partition):
        raise ValueError("majorization requires equal dimensions")
    if sum(left_partition) != sum(right_partition):
        return False
    left_prefix = 0
    right_prefix = 0
    for left_value, right_value in zip(
        left_partition[:-1], right_partition[:-1], strict=True
    ):
        left_prefix += left_value
        right_prefix += right_value
        if left_prefix < right_prefix:
            return False
    return True


def majorization_distance(left: Sequence[int], right: Sequence[int]) -> int:
    """Return the minimum number of unit balancing transfers from left to right.

    The arguments are compared after decreasing absolute sorting.  The
    distance is defined only in the directed majorization order.  For
    comparable integer partitions it is one half of their sorted L1
    distance.
    """

    left_partition = canonical_shift(left)
    right_partition = canonical_shift(right)
    if not majorizes(left_partition, right_partition):
        raise ValueError("left must majorize right at the same weight")
    distance_sum = sum(
        abs(left_value - right_value)
        for left_value, right_value in zip(
            left_partition, right_partition, strict=True
        )
    )
    if distance_sum % 2:
        raise AssertionError("equal-weight integer partitions have even L1 distance")
    return distance_sum // 2


def lee_shell_partitions(total_weight: int, dimension: int) -> tuple[tuple[int, ...], ...]:
    """Enumerate decreasing nonnegative partitions on one Lee shell."""

    if total_weight < 0:
        raise ValueError("total_weight must be nonnegative")
    if dimension < 1:
        raise ValueError("dimension must be positive")

    def generate(
        remaining: int, coordinates_left: int, upper_bound: int
    ) -> tuple[tuple[int, ...], ...]:
        if coordinates_left == 0:
            return ((),) if remaining == 0 else ()
        results: list[tuple[int, ...]] = []
        for value in range(min(remaining, upper_bound), -1, -1):
            results.extend(
                (value,) + suffix
                for suffix in generate(
                    remaining - value, coordinates_left - 1, value
                )
            )
        return tuple(results)

    return generate(total_weight, dimension, total_weight)


def balancing_neighbors(shift: Sequence[int]) -> tuple[tuple[int, ...], ...]:
    """Return all distinct partitions reached by one unit balancing move."""

    source = canonical_shift(shift)
    targets: set[tuple[int, ...]] = set()
    for donor_index, donor in enumerate(source):
        for recipient_index, recipient in enumerate(source):
            if donor_index == recipient_index or donor < recipient + 2:
                continue
            target = list(source)
            target[donor_index] -= 1
            target[recipient_index] += 1
            targets.add(tuple(sorted(target, reverse=True)))
    return tuple(sorted(targets, reverse=True))


@dataclass(frozen=True)
class WeightedBalancingEdge:
    """One directed edge of a lens-weighted majorization graph."""

    source: tuple[int, ...]
    target: tuple[int, ...]
    increment: int


@dataclass(frozen=True)
class ShellStabilityAudit:
    """Exact edge statistics for one finite majorization shell."""

    vertex_count: int
    edge_count: int
    minimum_positive_increment: int | None
    minimizers: tuple[WeightedBalancingEdge, ...]
    zero_edges: tuple[WeightedBalancingEdge, ...]


@dataclass(frozen=True)
class RadialLensWitness:
    """One positive mixed-difference term in a radial equality audit."""

    left_radius: int
    right_radius: int
    coefficient: int
    lens_increment: int


@dataclass(frozen=True)
class RadialEqualityCertificate:
    """Exact nonnegative decomposition of a radial correlation deficit."""

    total_increment: int
    witnesses: tuple[RadialLensWitness, ...]

    @property
    def is_equality(self) -> bool:
        """Return whether every active lens chamber has zero increment."""

        return self.total_increment == 0


def lens_shell_stability_audit(
    left_radius: int, right_radius: int, total_weight: int, dimension: int
) -> ShellStabilityAudit:
    """Construct and audit the weighted majorization graph of one Lee shell.

    This is an output-sensitive exact enumeration routine, intended for
    theorem discovery and finite certificates.  It makes no polynomial-time
    claim when the dimension is part of the input.
    """

    partitions = lee_shell_partitions(total_weight, dimension)
    edges: list[WeightedBalancingEdge] = []
    for source in partitions:
        source_count = unequal_lee_lens_count(
            left_radius, right_radius, source
        )
        for target in balancing_neighbors(source):
            increment = unequal_lee_lens_count(
                left_radius, right_radius, target
            ) - source_count
            if increment < 0:
                raise AssertionError("lens weights must increase under balancing")
            edges.append(WeightedBalancingEdge(source, target, increment))
    positive_increments = tuple(
        edge.increment for edge in edges if edge.increment > 0
    )
    minimum = min(positive_increments, default=None)
    return ShellStabilityAudit(
        vertex_count=len(partitions),
        edge_count=len(edges),
        minimum_positive_increment=minimum,
        minimizers=tuple(edge for edge in edges if edge.increment == minimum),
        zero_edges=tuple(edge for edge in edges if edge.increment == 0),
    )


def sharp_equal_radius_constant(
    radius: int, total_weight: int, dimension: int
) -> int:
    """Return the proved sharp equal-radius shell stability constant.

    The closed form is the sharp evaluation of the minimum positive balancing
    increment.  Its domain is the nontrivial active shell
    ``2 <= total_weight <= 2 * radius``.  Exact graph audits recompute the
    minimum independently of this formula.
    """

    if radius < 1:
        raise ValueError("radius must be positive")
    if dimension < 2:
        raise ValueError("dimension must be at least two")
    if not 2 <= total_weight <= 2 * radius:
        raise ValueError("the formula requires 2 <= total_weight <= 2 * radius")
    if dimension == 2:
        return 2 * radius - total_weight + 1

    def lee_ball_count(residual_radius: int, residual_dimension: int) -> int:
        if residual_dimension == 0:
            return 1
        return cross_polytope_lattice_count(
            residual_radius, residual_dimension
        )

    if total_weight == 2:
        return lee_ball_count(radius - 1, dimension - 1)
    if total_weight == 3:
        return (
            lee_ball_count(radius - 1, dimension - 1)
            - lee_ball_count(radius - 1, dimension - 3)
        ) // 2
    residual_radius = radius - (total_weight + 1) // 2
    value = lee_ball_count(residual_radius, dimension - 2)
    if total_weight % 2:
        value += lee_ball_count(residual_radius, dimension - 3)
    return value


def classify_sharp_arcs(
    radius: int, total_weight: int, dimension: int
) -> tuple[tuple[tuple[int, ...], tuple[int, ...]], ...]:
    """Return every minimizing arc of one equal-radius active Lee shell.

    This is the proved complete classification: on interior shells
    (``H = 2 * radius - total_weight + 1 >= 3``) the minimizers are exactly
    the balanced-gap axial family, all gap-two transfers with residual mass
    concentrated in one coordinate of size at least two; on the two
    outermost shells the two-coordinate boundary arcs (and, for
    ``H = 2``, the concentrated ``c = 1`` member) join the family.  Arcs
    are returned as sorted ``(source, target)`` pairs, one per
    signed-permutation orbit.  The domain is ``dimension >= 3`` and
    ``4 <= total_weight <= 2 * radius``.
    """

    if dimension < 3:
        raise ValueError("the classification requires dimension >= 3")
    if not 4 <= total_weight <= 2 * radius:
        raise ValueError(
            "the classification requires 4 <= total_weight <= 2 * radius"
        )
    shell_height = 2 * radius - total_weight + 1
    padding = (0,) * (dimension - 3)
    arcs: set[tuple[tuple[int, ...], tuple[int, ...]]] = set()

    concentration = total_weight - 2
    transfer_low = 0
    while concentration >= 2:
        source = tuple(
            sorted(
                (concentration, transfer_low + 2, transfer_low) + padding,
                reverse=True,
            )
        )
        target = tuple(
            sorted(
                (concentration, transfer_low + 1, transfer_low + 1) + padding,
                reverse=True,
            )
        )
        arcs.add((source, target))
        concentration -= 2
        transfer_low += 1

    if shell_height <= 2:
        donor = total_weight
        while donor - (total_weight - donor) >= 2:
            recipient = total_weight - donor
            source = tuple(
                sorted((donor, recipient) + (0,) * (dimension - 2),
                       reverse=True)
            )
            target = tuple(
                sorted((donor - 1, recipient + 1) + (0,) * (dimension - 2),
                       reverse=True)
            )
            arcs.add((source, target))
            donor -= 1
    if shell_height == 2 and total_weight % 2 == 1 and total_weight >= 5:
        transfer_low = (total_weight - 3) // 2
        source = tuple(
            sorted((1, transfer_low + 2, transfer_low) + padding,
                   reverse=True)
        )
        target = tuple(
            sorted((1, transfer_low + 1, transfer_low + 1) + padding,
                   reverse=True)
        )
        arcs.add((source, target))
    return tuple(sorted(arcs))


def mixed_forward_difference_support(
    kernel: Sequence[Sequence[int]],
) -> tuple[tuple[int, int, int], ...]:
    """Return the positive mixed forward differences of a finite kernel.

    ``kernel[r][s]`` represents ``H(r, s)`` and the array is extended by
    zero outside its rectangular support.  The routine validates exactly the
    cone used by the Lee-radial rearrangement theorem.
    """

    if not kernel or not kernel[0]:
        raise ValueError("kernel must be a nonempty rectangle")
    column_count = len(kernel[0])
    if any(len(row) != column_count for row in kernel):
        raise ValueError("kernel rows must have equal length")
    if any(value < 0 for row in kernel for value in row):
        raise ValueError("kernel must be nonnegative")

    def value(row: int, column: int) -> int:
        if row >= len(kernel) or column >= column_count:
            return 0
        return int(kernel[row][column])

    support: list[tuple[int, int, int]] = []
    for row in range(len(kernel)):
        for column in range(column_count):
            difference = (
                value(row, column)
                - value(row + 1, column)
                - value(row, column + 1)
                + value(row + 1, column + 1)
            )
            if difference < 0:
                raise ValueError("kernel has a negative mixed forward difference")
            if difference:
                support.append((row, column, difference))
    return tuple(support)


def finite_lee_kernel_correlation(
    kernel: Sequence[Sequence[int]], shift: Sequence[int]
) -> int:
    """Evaluate a finite Lee-radial kernel by its orthant decomposition."""

    partition = canonical_shift(shift)
    return sum(
        coefficient
        * unequal_lee_lens_count(
            left_radius, right_radius, partition
        )
        for left_radius, right_radius, coefficient in (
            mixed_forward_difference_support(kernel)
        )
    )


def radial_equality_certificate(
    kernel: Sequence[Sequence[int]],
    concentrated_shift: Sequence[int],
    balanced_shift_value: Sequence[int],
) -> RadialEqualityCertificate:
    """Certify equality or strictness for one ordered pair of shifts.

    ``concentrated_shift`` must majorize ``balanced_shift_value``.  Each
    returned witness has a positive mixed-difference coefficient and a
    nonnegative lens increment.  Therefore equality holds if and only if
    every witness has zero ``lens_increment``.
    """

    source = canonical_shift(concentrated_shift)
    target = canonical_shift(balanced_shift_value)
    if not majorizes(source, target):
        raise ValueError("the first shift must majorize the second")
    witnesses = tuple(
        RadialLensWitness(
            left_radius=left_radius,
            right_radius=right_radius,
            coefficient=coefficient,
            lens_increment=(
                unequal_lee_lens_count(left_radius, right_radius, target)
                - unequal_lee_lens_count(left_radius, right_radius, source)
            ),
        )
        for left_radius, right_radius, coefficient in (
            mixed_forward_difference_support(kernel)
        )
    )
    if any(witness.lens_increment < 0 for witness in witnesses):
        raise AssertionError("majorization requires nonnegative lens increments")
    return RadialEqualityCertificate(
        total_increment=sum(
            witness.coefficient * witness.lens_increment
            for witness in witnesses
        ),
        witnesses=witnesses,
    )


def qary_lee_lens_count(
    modulus: int,
    left_radius: int,
    right_radius: int,
    shift: Sequence[int],
) -> int:
    """Brute-force a finite q-ary Lee lens for boundary falsification.

    This intentionally small-parameter routine lives outside the main
    infinite-lattice theorem.  It is used to detect where wrap-around breaks
    the integer-lattice transfer law.
    """

    if modulus < 2:
        raise ValueError("modulus must be at least two")
    if left_radius < 0 or right_radius < 0:
        return 0
    coordinates = tuple(int(value) % modulus for value in shift)
    if not coordinates:
        raise ValueError("shift must have positive dimension")

    def lee_norm(vector: Sequence[int]) -> int:
        return sum(
            min(value % modulus, (-value) % modulus) for value in vector
        )

    return sum(
        lee_norm(point) <= left_radius
        and lee_norm(
            tuple(
                value + delta
                for value, delta in zip(point, coordinates, strict=True)
            )
        )
        <= right_radius
        for point in product(range(modulus), repeat=len(coordinates))
    )


def balanced_shift(total_weight: int, dimension: int) -> tuple[int, ...]:
    """Return the unique decreasing balanced partition of a Lee weight."""

    if total_weight < 0:
        raise ValueError("total_weight must be nonnegative")
    if dimension < 1:
        raise ValueError("dimension must be positive")
    quotient, remainder = divmod(total_weight, dimension)
    return (quotient + 1,) * remainder + (quotient,) * (dimension - remainder)


def unequal_lee_lens_count(
    left_radius: int, right_radius: int, shift: Sequence[int]
) -> int:
    """Count an unequal-radius Lee lens exactly by a bivariate DP."""

    if left_radius < 0 or right_radius < 0:
        return 0
    partition = canonical_shift(shift)
    if sum(partition) > left_radius + right_radius:
        return 0
    return _unequal_lee_lens_count_cached(left_radius, right_radius, partition)


def parity_interval_count(
    left_radius: int, right_radius: int, center: int, parity: int
) -> int:
    """Count one parity class in an intersection of two integer intervals.

    More precisely, this returns the number of integers ``value`` satisfying

    ``abs(value) <= left_radius``, ``abs(value + center) <= right_radius``,
    and ``value == parity (mod 2)``.

    The function is the atomic chamber count in the parity-rectangle model of
    a two-dimensional Lee lens.  A negative radius represents an empty
    residual ball, consistently with :func:`unequal_lee_lens_count`.
    """

    if parity not in (0, 1):
        raise ValueError("parity must be zero or one")
    if left_radius < 0 or right_radius < 0:
        return 0
    lower = max(-left_radius, -center - right_radius)
    upper = min(left_radius, -center + right_radius)
    if lower > upper:
        return 0
    first = lower + ((parity - lower) % 2)
    if first > upper:
        return 0
    return (upper - first) // 2 + 1


def two_coordinate_lens_count(
    left_radius: int, right_radius: int, high: int, low: int
) -> int:
    """Evaluate a two-coordinate Lee lens through its parity rectangles.

    The shift is ``(high, low)``.  Signs do not matter, so both coordinates
    are replaced by their absolute values.  The change of variables
    ``r=x+y`` and ``w=x-y`` maps the two diamonds to rectangles, with the
    sole lattice constraint ``r == w (mod 2)``.
    """

    high = abs(int(high))
    low = abs(int(low))
    coordinate_sum = high + low
    coordinate_difference = high - low
    return sum(
        parity_interval_count(
            left_radius, right_radius, coordinate_sum, parity
        )
        * parity_interval_count(
            left_radius, right_radius, coordinate_difference, parity
        )
        for parity in (0, 1)
    )


def balancing_increment_channels(
    left_radius: int, right_radius: int, high: int, low: int
) -> tuple[int, int]:
    """Return the even and odd increments of one Robin Hood transfer.

    The source shift is ``(high, low)`` and the target is
    ``(high - 1, low + 1)``.  Thus ``high >= low + 2`` is required.  The sum
    ``R = high + low`` stays fixed while the difference ``D = high - low``
    decreases by two.  Channel ``epsilon`` is exactly

    ``n_epsilon(R) * (n_epsilon(D - 2) - n_epsilon(D))``.

    Returning the channels separately makes the local equality condition
    executable: the transfer has zero increment exactly when both entries
    vanish.
    """

    high = abs(int(high))
    low = abs(int(low))
    if high < low + 2:
        raise ValueError("a balancing transfer requires high >= low + 2")
    coordinate_sum = high + low
    coordinate_difference = high - low
    return tuple(
        parity_interval_count(
            left_radius, right_radius, coordinate_sum, parity
        )
        * (
            parity_interval_count(
                left_radius, right_radius, coordinate_difference - 2, parity
            )
            - parity_interval_count(
                left_radius, right_radius, coordinate_difference, parity
            )
        )
        for parity in (0, 1)
    )


def balancing_increment(
    left_radius: int, right_radius: int, high: int, low: int
) -> int:
    """Return the exact two-coordinate lens gain under one balancing move."""

    return sum(
        balancing_increment_channels(left_radius, right_radius, high, low)
    )


def residual_norm_histogram(
    left_radius: int, right_radius: int, shift: Sequence[int]
) -> dict[tuple[int, int], int]:
    """Return the exact bivariate norm histogram for residual coordinates.

    Entry ``(r, s)`` counts residual vectors ``y`` with
    ``||y||_1 = r`` and ``||y + shift||_1 = s``.  Only entries inside the
    supplied radii are retained.  The empty residual shift has the single
    state ``(0, 0)``.
    """

    if left_radius < 0 or right_radius < 0:
        return {}
    partition = tuple(sorted((abs(int(value)) for value in shift), reverse=True))
    states: dict[tuple[int, int], int] = {(0, 0): 1}
    for coordinate_shift in partition:
        coordinate_terms: dict[tuple[int, int], int] = {}
        lower = max(-left_radius, -coordinate_shift - right_radius)
        upper = min(left_radius, -coordinate_shift + right_radius)
        for value in range(lower, upper + 1):
            degree = (abs(value), abs(value + coordinate_shift))
            coordinate_terms[degree] = coordinate_terms.get(degree, 0) + 1

        updated: dict[tuple[int, int], int] = {}
        for (left_degree, right_degree), multiplicity in states.items():
            for (left_step, right_step), step_multiplicity in coordinate_terms.items():
                new_left = left_degree + left_step
                new_right = right_degree + right_step
                if new_left <= left_radius and new_right <= right_radius:
                    key = (new_left, new_right)
                    updated[key] = updated.get(key, 0) + (
                        multiplicity * step_multiplicity
                    )
        states = updated
        if not states:
            break
    return states


def lifted_balancing_increment(
    left_radius: int,
    right_radius: int,
    shift: Sequence[int],
    donor_index: int,
    recipient_index: int,
) -> int:
    """Lift the two-coordinate increment law to an arbitrary dimension.

    The returned integer is computed as a nonnegative convolution of the
    local parity kernel with the bivariate norm histogram of all untouched
    coordinates.  Indices refer to the supplied coordinate order.
    """

    coordinates = tuple(abs(int(value)) for value in shift)
    if not coordinates:
        raise ValueError("shift must have positive dimension")
    if donor_index == recipient_index:
        raise ValueError("donor and recipient indices must differ")
    if not (0 <= donor_index < len(coordinates)) or not (
        0 <= recipient_index < len(coordinates)
    ):
        raise IndexError("coordinate index out of range")
    high = coordinates[donor_index]
    low = coordinates[recipient_index]
    if high < low + 2:
        raise ValueError("a balancing transfer requires donor >= recipient + 2")
    residual_shift = tuple(
        value
        for index, value in enumerate(coordinates)
        if index not in (donor_index, recipient_index)
    )
    histogram = residual_norm_histogram(
        left_radius, right_radius, residual_shift
    )
    return sum(
        multiplicity
        * balancing_increment(
            left_radius - left_degree,
            right_radius - right_degree,
            high,
            low,
        )
        for (left_degree, right_degree), multiplicity in histogram.items()
    )


@lru_cache(maxsize=None)
def _unequal_lee_lens_count_cached(
    left_radius: int, right_radius: int, partition: tuple[int, ...]
) -> int:
    states: dict[tuple[int, int], int] = {(0, 0): 1}
    for coordinate_shift in partition:
        coordinate_terms: dict[tuple[int, int], int] = {}
        lower = max(-left_radius, -coordinate_shift - right_radius)
        upper = min(left_radius, -coordinate_shift + right_radius)
        for value in range(lower, upper + 1):
            degree = (abs(value), abs(value + coordinate_shift))
            coordinate_terms[degree] = coordinate_terms.get(degree, 0) + 1

        updated: dict[tuple[int, int], int] = {}
        for (left_degree, right_degree), multiplicity in states.items():
            for (
                left_step,
                right_step,
            ), coordinate_multiplicity in coordinate_terms.items():
                new_left = left_degree + left_step
                new_right = right_degree + right_step
                if new_left <= left_radius and new_right <= right_radius:
                    key = (new_left, new_right)
                    updated[key] = updated.get(key, 0) + (
                        multiplicity * coordinate_multiplicity
                    )
        states = updated
        if not states:
            return 0
    return sum(states.values())


def concentrated_equal_radius_lens_count(
    radius: int, total_weight: int, dimension: int
) -> int:
    """Closed formula for the minimum equal-radius lens at fixed Lee weight."""

    if radius < 0:
        raise ValueError("radius must be nonnegative")
    if total_weight < 0:
        raise ValueError("total_weight must be nonnegative")
    if dimension < 2:
        raise ValueError("dimension must be at least two")

    half_weight, parity = divmod(total_weight, 2)
    reduced_radius = radius - half_weight
    if reduced_radius < 0:
        return 0
    full_ball = cross_polytope_lattice_count(reduced_radius, dimension)
    if parity == 0:
        return full_ball
    equator = cross_polytope_lattice_count(reduced_radius, dimension - 1)
    return full_ball - equator


def finite_lee_radial_correlation(
    left_profile: Sequence[int], right_profile: Sequence[int], shift: Sequence[int]
) -> int:
    """Correlate two finite nonincreasing Lee-radial profiles exactly.

    The sequences give values at radii ``0, 1, ...`` and are extended by zero.
    Layer-cake differences reduce the correlation to unequal-radius lens
    counts, directly mirroring the rearrangement theorem.
    """

    if not left_profile or not right_profile:
        raise ValueError("profiles must be nonempty")
    for profile in (left_profile, right_profile):
        if any(value < 0 for value in profile):
            raise ValueError("profiles must be nonnegative")
        if any(
            profile[index] < profile[index + 1] for index in range(len(profile) - 1)
        ):
            raise ValueError("profiles must be nonincreasing")
    partition = canonical_shift(shift)
    left_drops = tuple(
        value - (left_profile[index + 1] if index + 1 < len(left_profile) else 0)
        for index, value in enumerate(left_profile)
    )
    right_drops = tuple(
        value - (right_profile[index + 1] if index + 1 < len(right_profile) else 0)
        for index, value in enumerate(right_profile)
    )
    return sum(
        left_drop
        * right_drop
        * unequal_lee_lens_count(left_radius, right_radius, partition)
        for left_radius, left_drop in enumerate(left_drops)
        if left_drop
        for right_radius, right_drop in enumerate(right_drops)
        if right_drop
    )
