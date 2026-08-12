from __future__ import annotations

from fractions import Fraction
from itertools import product

import pytest

from ehrhart_fswa.counts import (
    cross_polytope_lattice_count,
    cross_polytope_overlap_count,
)
from ehrhart_fswa.majorization import (
    balancing_neighbors,
    balancing_increment,
    balancing_increment_channels,
    balanced_shift,
    classify_sharp_arcs,
    sharp_equal_radius_constant,
    concentrated_equal_radius_lens_count,
    finite_lee_radial_correlation,
    finite_lee_kernel_correlation,
    lee_shell_partitions,
    lens_shell_stability_audit,
    lifted_balancing_increment,
    majorization_distance,
    majorizes,
    mixed_forward_difference_support,
    parity_interval_count,
    qary_lee_lens_count,
    residual_norm_histogram,
    radial_equality_certificate,
    two_coordinate_lens_count,
    unequal_lee_lens_count,
)


def _partitions(total: int, dimension: int) -> list[tuple[int, ...]]:
    return sorted(
        {
            tuple(sorted(values, reverse=True))
            for values in product(range(total + 1), repeat=dimension)
            if sum(values) == total
        },
        reverse=True,
    )


def _brute_unequal_lens(
    left_radius: int, right_radius: int, shift: tuple[int, ...]
) -> int:
    bound = max(left_radius, right_radius + sum(abs(value) for value in shift))
    return sum(
        sum(abs(value) for value in point) <= left_radius
        and sum(abs(value + delta) for value, delta in zip(point, shift, strict=True))
        <= right_radius
        for point in product(range(-bound, bound + 1), repeat=len(shift))
    )


@pytest.mark.parametrize(
    ("left_radius", "right_radius", "shift"),
    [
        (0, 0, (0, 0)),
        (1, 2, (2, 0)),
        (2, 1, (1, 1)),
        (3, 4, (3, 1)),
        (3, 2, (-2, 1, 0)),
    ],
)
def test_unequal_lee_lens_matches_brute_force(
    left_radius: int, right_radius: int, shift: tuple[int, ...]
) -> None:
    assert unequal_lee_lens_count(left_radius, right_radius, shift) == (
        _brute_unequal_lens(left_radius, right_radius, shift)
    )


def test_parity_interval_chambers_match_direct_enumeration() -> None:
    for left_radius in range(-1, 8):
        for right_radius in range(-1, 8):
            for center in range(-10, 11):
                for parity in (0, 1):
                    expected = sum(
                        abs(value) <= left_radius
                        and abs(value + center) <= right_radius
                        and value % 2 == parity
                        for value in range(-20, 21)
                    )
                    assert parity_interval_count(
                        left_radius, right_radius, center, parity
                    ) == expected


def test_exact_balancing_kernel_matches_all_two_dimensional_lenses() -> None:
    comparisons = 0
    for left_radius in range(9):
        for right_radius in range(9):
            for high in range(2, 11):
                for low in range(high - 1):
                    if high < low + 2:
                        continue
                    source = unequal_lee_lens_count(
                        left_radius, right_radius, (high, low)
                    )
                    target = unequal_lee_lens_count(
                        left_radius, right_radius, (high - 1, low + 1)
                    )
                    assert two_coordinate_lens_count(
                        left_radius, right_radius, high, low
                    ) == source
                    channels = balancing_increment_channels(
                        left_radius, right_radius, high, low
                    )
                    assert all(channel >= 0 for channel in channels)
                    difference = high - low
                    for parity in (0, 1):
                        endpoint_switch = parity_interval_count(
                            left_radius, right_radius, difference - 2, parity
                        ) - parity_interval_count(
                            left_radius, right_radius, difference, parity
                        )
                        assert endpoint_switch in (0, 1)
                    assert balancing_increment(
                        left_radius, right_radius, high, low
                    ) == target - source == sum(channels)
                    comparisons += 1
    assert comparisons == 3_645

    # A wider endpoint-only audit protects the universal unequal-radius
    # claim without paying for full two-dimensional enumeration.
    endpoint_comparisons = 0
    for left_radius in range(33):
        for right_radius in range(33):
            for difference in range(2, 65):
                for parity in (0, 1):
                    switch = parity_interval_count(
                        left_radius,
                        right_radius,
                        difference - 2,
                        parity,
                    ) - parity_interval_count(
                        left_radius,
                        right_radius,
                        difference,
                        parity,
                    )
                    assert switch in (0, 1)
                    endpoint_comparisons += 1
    assert endpoint_comparisons == 137_214

    # Gap one is not a transfer edge: the putative move only swaps the two
    # coordinates and must remain in the same symmetry orbit.
    for left_radius in range(9):
        for right_radius in range(9):
            for low in range(20):
                assert unequal_lee_lens_count(
                    left_radius, right_radius, (low + 1, low)
                ) == unequal_lee_lens_count(
                    left_radius, right_radius, (low, low + 1)
                )


def test_lifted_balancing_kernel_matches_high_dimensional_dp() -> None:
    comparisons = 0
    for dimension in range(2, 6):
        for total in range(9):
            for partition in _partitions(total, dimension):
                for donor_index in range(dimension):
                    for recipient_index in range(dimension):
                        if partition[donor_index] < partition[recipient_index] + 2:
                            continue
                        target = list(partition)
                        target[donor_index] -= 1
                        target[recipient_index] += 1
                        for left_radius in range(6):
                            for right_radius in range(6):
                                direct = unequal_lee_lens_count(
                                    left_radius, right_radius, target
                                ) - unequal_lee_lens_count(
                                    left_radius, right_radius, partition
                                )
                                assert lifted_balancing_increment(
                                    left_radius,
                                    right_radius,
                                    partition,
                                    donor_index,
                                    recipient_index,
                                ) == direct
                                comparisons += 1
    assert comparisons == 16_740


def test_residual_histogram_sums_to_the_residual_lens() -> None:
    for left_radius in range(6):
        for right_radius in range(6):
            for shift in ((0,), (3,), (2, 1), (3, 1, 0)):
                assert sum(
                    residual_norm_histogram(
                        left_radius, right_radius, shift
                    ).values()
                ) == unequal_lee_lens_count(left_radius, right_radius, shift)


def test_near_equal_radius_local_increment_has_a_single_linear_formula() -> None:
    comparisons = 0
    for left_radius in range(21):
        for right_radius in range(21):
            if abs(left_radius - right_radius) > 1:
                continue
            for high in range(2, 30):
                for low in range(high - 1):
                    assert balancing_increment(
                        left_radius, right_radius, high, low
                    ) == max(
                        0,
                        left_radius + right_radius - high - low + 1,
                    ) // (
                        2
                        if abs(left_radius - right_radius) == 1
                        and high - low == 2
                        else 1
                    )
                    comparisons += 1
    assert comparisons == 24_766


def test_majorization_distance_is_the_shortest_transfer_distance() -> None:
    comparisons = 0
    for dimension in range(2, 6):
        for total in range(10):
            partitions = lee_shell_partitions(total, dimension)
            for source in partitions:
                distances = {source: 0}
                frontier = [source]
                while frontier:
                    current = frontier.pop(0)
                    for target in balancing_neighbors(current):
                        if target not in distances:
                            distances[target] = distances[current] + 1
                            frontier.append(target)
                for target in partitions:
                    if not majorizes(source, target):
                        continue
                    assert majorization_distance(source, target) == distances[target]
                    comparisons += 1
    assert comparisons == 1_317


def test_equal_radius_stability_and_sharp_constant() -> None:
    audited_edges = 0
    for dimension in range(2, 7):
        for radius in range(1, 9):
            for total in range(2, 2 * radius + 1):
                audit = lens_shell_stability_audit(
                    radius, radius, total, dimension
                )
                assert not audit.zero_edges
                assert audit.minimum_positive_increment == (
                    sharp_equal_radius_constant(
                        radius, total, dimension
                    )
                )
                for edge in audit.minimizers:
                    assert majorization_distance(edge.source, edge.target) == 1
                audited_edges += audit.edge_count
    assert audited_edges == 11_215


def test_axial_residual_edge_attains_sharp_constant() -> None:
    # Covers every active shell s >= 2, matching the strengthened attaining
    # statement of the Lee sharp theorem (s = 2, 3 included).
    checked = 0
    for dimension in range(3, 8):
        for radius in range(2, 10):
            for total in range(2, 2 * radius + 1):
                source = tuple(
                    sorted((total - 2, 2, *([0] * (dimension - 2))), reverse=True)
                )
                target = tuple(
                    sorted(
                        (total - 2, 1, 1, *([0] * (dimension - 3))),
                        reverse=True,
                    )
                )
                increment = unequal_lee_lens_count(
                    radius, radius, target
                ) - unequal_lee_lens_count(radius, radius, source)
                assert increment == sharp_equal_radius_constant(
                    radius, total, dimension
                )
                checked += 1
    assert checked == 400


def test_classification_matches_exhaustive_minimizer_audit() -> None:
    # The complete classification of minimizing arcs: interior shells carry
    # exactly the balanced-gap axial family, and the two outermost shells
    # acquire the described boundary arcs.  Verified against the exact
    # weighted-graph audit.
    shells = 0
    for dimension in range(3, 7):
        for radius in range(2, 7):
            for total in range(4, 2 * radius + 1):
                audit = lens_shell_stability_audit(
                    radius, radius, total, dimension
                )
                actual = {
                    (edge.source, edge.target) for edge in audit.minimizers
                }
                predicted = set(
                    classify_sharp_arcs(radius, total, dimension)
                )
                assert actual == predicted, (dimension, radius, total)
                shells += 1
    assert shells == 100


def test_interior_shell_multiplicity_is_dimension_and_radius_free() -> None:
    # On interior shells the sharp layer has exactly floor(s/2) - 1 arcs.
    for dimension in range(3, 7):
        for radius in range(3, 7):
            for total in range(4, 2 * radius - 1):
                arcs = classify_sharp_arcs(radius, total, dimension)
                assert len(arcs) == total // 2 - 1


def test_exact_outer_arc_weights() -> None:
    # Lemma: every zero-residual arc has weight sum_k S_m(k) (H - 2k)_+,
    # independently of its gap, and the concentrated c = 1 gap-two arc has
    # weight sum_k L_{m-1}(k) (H - 2k)_+.
    def sphere_count(m: int, k: int) -> int:
        if m == 0:
            return 1 if k == 0 else 0
        return cross_polytope_lattice_count(k, m) - (
            cross_polytope_lattice_count(k - 1, m) if k >= 1 else 0
        )

    def ball_count(m: int, k: int) -> int:
        if m == 0:
            return 1
        return cross_polytope_lattice_count(k, m)

    for dimension in (3, 4, 5):
        m = dimension - 2
        for radius in range(2, 7):
            for total in range(4, 2 * radius + 1):
                height = 2 * radius - total + 1
                weight_zero = sum(
                    sphere_count(m, k) * max(height - 2 * k, 0)
                    for k in range(radius + 1)
                )
                donor = total
                while donor - (total - donor) >= 2:
                    recipient = total - donor
                    source = tuple(
                        sorted(
                            (donor, recipient) + (0,) * (dimension - 2),
                            reverse=True,
                        )
                    )
                    target = tuple(
                        sorted(
                            (donor - 1, recipient + 1)
                            + (0,) * (dimension - 2),
                            reverse=True,
                        )
                    )
                    increment = unequal_lee_lens_count(
                        radius, radius, target
                    ) - unequal_lee_lens_count(radius, radius, source)
                    assert increment == weight_zero
                    donor -= 1
                if total % 2 == 1 and total >= 5:
                    low = (total - 3) // 2
                    source = tuple(
                        sorted(
                            (1, low + 2, low) + (0,) * (dimension - 3),
                            reverse=True,
                        )
                    )
                    target = tuple(
                        sorted(
                            (1, low + 1, low + 1) + (0,) * (dimension - 3),
                            reverse=True,
                        )
                    )
                    increment = unequal_lee_lens_count(
                        radius, radius, target
                    ) - unequal_lee_lens_count(radius, radius, source)
                    weight_one = sum(
                        ball_count(m - 1, k) * max(height - 2 * k, 0)
                        for k in range(radius + 1)
                    )
                    assert increment == weight_one


def test_cube_sharp_arc_is_unique() -> None:
    # Corollary: the cube sharp layer is a single arc on every active shell.
    for dimension in (3, 4, 5):
        for radius in range(1, 6):
            height = 2 * radius + 1

            def cube_covariogram(shift: tuple[int, ...]) -> int:
                value = 1
                for entry in shift:
                    value *= max(height - entry, 0)
                return value

            for total in range(2, height + 1):
                best = None
                minimizers = set()
                for source in lee_shell_partitions(total, dimension):
                    for target in balancing_neighbors(source):
                        increment = cube_covariogram(
                            target
                        ) - cube_covariogram(source)
                        if best is None or increment < best:
                            best = increment
                            minimizers = {(source, target)}
                        elif increment == best:
                            minimizers.add((source, target))
                canonical_source = tuple(
                    sorted(
                        (total - 2, 2) + (0,) * (dimension - 2), reverse=True
                    )
                )
                canonical_target = tuple(
                    sorted(
                        (total - 2, 1, 1) + (0,) * (dimension - 3),
                        reverse=True,
                    )
                )
                assert minimizers == {(canonical_source, canonical_target)}


def test_pair_rigidity_matches_predicted_extremal_pairs() -> None:
    # Theorem (rigidity of stability extremizers): the deficit of a
    # comparable pair equals kappa * d_M iff the pair is a single
    # minimizing arc, or H <= 2 and both endpoints lie on the
    # two-coordinate boundary path.
    pairs = 0
    for dimension in (3, 4, 5):
        for radius in range(2, 6):
            for total in range(4, 2 * radius + 1):
                height = 2 * radius - total + 1
                kappa = sharp_equal_radius_constant(radius, total, dimension)
                sharp_arcs = set(
                    classify_sharp_arcs(radius, total, dimension)
                )
                parts = lee_shell_partitions(total, dimension)
                lens = {
                    p: unequal_lee_lens_count(radius, radius, p)
                    for p in parts
                }
                for lam in parts:
                    for mu in parts:
                        if lam == mu or not majorizes(lam, mu):
                            continue
                        distance = majorization_distance(lam, mu)
                        deficit = lens[mu] - lens[lam]
                        attains = deficit == kappa * distance
                        if distance == 1:
                            predicted = (lam, mu) in sharp_arcs
                        else:
                            predicted = (
                                height <= 2
                                and sum(1 for x in lam if x > 0) <= 2
                                and sum(1 for x in mu if x > 0) <= 2
                            )
                        assert attains == predicted, (
                            dimension,
                            radius,
                            total,
                            lam,
                            mu,
                        )
                        pairs += 1
                        if attains and distance >= 2:
                            assert height <= 2
    assert pairs == 2515


def test_integer_stability_accumulates_along_majorization_distance() -> None:
    comparisons = 0
    for dimension in range(2, 6):
        for radius in range(1, 8):
            for total in range(2 * radius + 1):
                partitions = lee_shell_partitions(total, dimension)
                shell_constant = None
                if total >= 2:
                    shell_constant = lens_shell_stability_audit(
                        radius, radius, total, dimension
                    ).minimum_positive_increment
                values = {
                    partition: unequal_lee_lens_count(
                        radius, radius, partition
                    )
                    for partition in partitions
                }
                for source in partitions:
                    for target in partitions:
                        if not majorizes(source, target):
                            continue
                        assert values[target] - values[source] >= (
                            majorization_distance(source, target)
                        )
                        if source != target:
                            assert shell_constant is not None
                            assert values[target] - values[source] >= (
                                shell_constant
                                * majorization_distance(source, target)
                            )
                        comparisons += 1
    assert comparisons == 18_678


def _kernel_from_mixed_differences(
    differences: tuple[tuple[int, ...], ...]
) -> tuple[tuple[int, ...], ...]:
    return tuple(
        tuple(
            sum(
                differences[left_radius][right_radius]
                for left_radius in range(row, len(differences))
                for right_radius in range(column, len(differences[0]))
            )
            for column in range(len(differences[0]))
        )
        for row in range(len(differences))
    )


def test_general_radial_kernel_matches_direct_sum_and_recovers_support() -> None:
    differences = (
        (0, 2, 0, 1),
        (3, 0, 0, 0),
        (0, 0, 4, 0),
    )
    kernel = _kernel_from_mixed_differences(differences)
    assert mixed_forward_difference_support(kernel) == (
        (0, 1, 2),
        (0, 3, 1),
        (1, 0, 3),
        (2, 2, 4),
    )
    shift = (2, 1)
    direct = 0
    for point in product(range(-3, 4), repeat=2):
        left_norm = sum(abs(value) for value in point)
        right_norm = sum(
            abs(value + delta)
            for value, delta in zip(point, shift, strict=True)
        )
        if left_norm < len(kernel) and right_norm < len(kernel[0]):
            direct += kernel[left_norm][right_norm]
    assert finite_lee_kernel_correlation(kernel, shift) == direct


def test_radial_equality_certificate_is_an_exact_if_and_only_if() -> None:
    source = (2, 0)
    target = (1, 1)
    equality_kernel = _kernel_from_mixed_differences(
        (
            (0, 0, 1, 0),
            (0, 0, 0, 0),
        )
    )
    equality = radial_equality_certificate(
        equality_kernel, source, target
    )
    assert equality.is_equality
    assert equality.total_increment == 0
    assert all(witness.lens_increment == 0 for witness in equality.witnesses)

    strict_kernel = _kernel_from_mixed_differences(
        (
            (0, 0, 0),
            (0, 1, 0),
            (0, 0, 0),
        )
    )
    strict = radial_equality_certificate(strict_kernel, source, target)
    assert not strict.is_equality
    assert strict.total_increment == (
        finite_lee_kernel_correlation(strict_kernel, target)
        - finite_lee_kernel_correlation(strict_kernel, source)
    )
    assert any(witness.lens_increment > 0 for witness in strict.witnesses)


def test_radial_kernel_cone_validation() -> None:
    with pytest.raises(ValueError):
        mixed_forward_difference_support(((1, 0), (0, 1)))
    with pytest.raises(ValueError):
        mixed_forward_difference_support(((1, 0), (1,)))


def test_qary_wraparound_has_a_small_explicit_order_reversal() -> None:
    source = qary_lee_lens_count(6, 1, 3, (3, 1))
    target = qary_lee_lens_count(6, 1, 3, (2, 2))
    assert source == 3
    assert target == 2
    assert source > target


def test_no_qary_reversal_occurs_below_the_wraparound_boundary() -> None:
    comparisons = 0
    for modulus in range(3, 6):
        coordinate_cap = modulus // 2
        for dimension in range(2, 4):
            diameter = dimension * coordinate_cap
            for total in range(diameter + 1):
                partitions = tuple(
                    partition
                    for partition in lee_shell_partitions(total, dimension)
                    if partition[0] <= coordinate_cap
                )
                for source in partitions:
                    for target in partitions:
                        if source == target or not majorizes(source, target):
                            continue
                        for left_radius in range(diameter + 1):
                            for right_radius in range(diameter + 1):
                                assert qary_lee_lens_count(
                                    modulus,
                                    left_radius,
                                    right_radius,
                                    source,
                                ) <= qary_lee_lens_count(
                                    modulus,
                                    left_radius,
                                    right_radius,
                                    target,
                                )
                                comparisons += 1
    assert comparisons == 344


def test_unequal_radius_lenses_are_schur_concave_exhaustively() -> None:
    comparisons = 0
    for dimension in range(2, 5):
        for total in range(8):
            partitions = _partitions(total, dimension)
            for left in partitions:
                for right in partitions:
                    if not majorizes(left, right):
                        continue
                    for left_radius in range(6):
                        for right_radius in range(6):
                            comparisons += 1
                            assert unequal_lee_lens_count(
                                left_radius, right_radius, left
                            ) <= unequal_lee_lens_count(
                                left_radius, right_radius, right
                            )
    assert comparisons == 10_476


def test_fixed_weight_extremizers_and_closed_minimum() -> None:
    for dimension in range(2, 7):
        for total in range(11):
            concentrated = (total,) + (0,) * (dimension - 1)
            balanced = balanced_shift(total, dimension)
            for radius in range(9):
                values = [
                    cross_polytope_overlap_count(radius, partition)
                    for partition in _partitions(total, dimension)
                ]
                assert min(values) == cross_polytope_overlap_count(radius, concentrated)
                assert max(values) == cross_polytope_overlap_count(radius, balanced)
                assert min(values) == concentrated_equal_radius_lens_count(
                    radius, total, dimension
                )
                if total <= 2 * radius:
                    assert values.count(min(values)) == 1
                    assert values.count(max(values)) == 1


def test_nearly_equal_residual_radii_give_strict_balancing() -> None:
    for left_radius in range(10):
        for right_radius in range(10):
            if abs(left_radius - right_radius) > 1:
                continue
            for high in range(2, 10):
                for low in range(high - 1):
                    if high < low + 2 or high + low > left_radius + right_radius:
                        continue
                    assert unequal_lee_lens_count(
                        left_radius, right_radius, (high, low)
                    ) < unequal_lee_lens_count(
                        left_radius, right_radius, (high - 1, low + 1)
                    )


def test_majorization_validates_dimensions_and_weight() -> None:
    with pytest.raises(ValueError):
        majorizes((2, 0), (1, 1, 0))
    assert not majorizes((2, 0), (1, 0))


def test_finite_radial_correlation_matches_direct_sum() -> None:
    left_profile = (7, 4, 1)
    right_profile = (5, 3, 2, 1)
    shift = (2, 1)
    direct = 0
    for point in product(range(-2, 3), repeat=2):
        left_norm = sum(abs(value) for value in point)
        right_norm = sum(
            abs(value + delta) for value, delta in zip(point, shift, strict=True)
        )
        if left_norm < len(left_profile) and right_norm < len(right_profile):
            direct += left_profile[left_norm] * right_profile[right_norm]
    assert finite_lee_radial_correlation(left_profile, right_profile, shift) == direct


def test_strict_radial_rearrangement_beyond_ball_indicators() -> None:
    left_profile = (8, 7, 6, 5, 4, 3, 2, 1)
    right_profile = (16, 14, 12, 10, 8, 6, 4, 2)
    for dimension in range(2, 5):
        for total in range(1, 11):
            partitions = _partitions(total, dimension)
            for left in partitions:
                for right in partitions:
                    if left != right and majorizes(left, right):
                        assert finite_lee_radial_correlation(
                            left_profile, right_profile, left
                        ) < finite_lee_radial_correlation(
                            left_profile, right_profile, right
                        )


def test_radial_profile_validation() -> None:
    with pytest.raises(ValueError):
        finite_lee_radial_correlation((1, 2), (1,), (0, 0))
    with pytest.raises(ValueError):
        finite_lee_radial_correlation((1,), (-1,), (0, 0))


def test_concentrated_lens_decreases_with_shift_weight() -> None:
    for dimension in range(2, 7):
        for radius in range(1, 10):
            counts = [
                concentrated_equal_radius_lens_count(radius, weight, dimension)
                for weight in range(2 * radius + 1)
            ]
            assert all(left > right for left, right in zip(counts, counts[1:]))


def test_pairwise_and_common_first_order_constants() -> None:
    scale = 10_000
    for dimension in range(2, 6):
        for shift_weight in range(1, 6):
            source = cross_polytope_lattice_count(scale, dimension)
            pair = concentrated_equal_radius_lens_count(scale, shift_weight, dimension)
            common = cross_polytope_lattice_count(scale - shift_weight, dimension)
            scaled_pair_loss = scale * (1 - Fraction(pair, source))
            scaled_common_loss = scale * (1 - Fraction(common, source))
            assert abs(
                scaled_pair_loss - Fraction(dimension * shift_weight, 2)
            ) < Fraction(1, 20)
            assert abs(scaled_common_loss - dimension * shift_weight) < Fraction(1, 10)
