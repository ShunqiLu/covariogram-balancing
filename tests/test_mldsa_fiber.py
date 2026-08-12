from __future__ import annotations

from collections import Counter

from ehrhart_fswa.mldsa_case import PARAMETER_SETS
from ehrhart_fswa.mldsa_fiber import (
    Q,
    analyze_fiber_parameter_set,
    commitment_hash_input_length_bytes,
    commitment_fiber_upper_bound,
    defect_tail_log2,
    highbits,
    highbits_max_bucket_size,
    global_xof_source_hit_upper_bound,
    matrix_rank_mod,
    ntt_rank_defect,
    rank_bucket_fiber_upper_bound,
    rank_count_rectangular,
    w1encode_length_bytes,
)


def test_highbits_bucket_bound_includes_exceptional_residue() -> None:
    q, gamma2 = 17, 2
    counts = Counter(highbits(value, q, gamma2) for value in range(q))
    assert max(counts.values()) == highbits_max_bucket_size(q, gamma2) == 5
    assert sorted(counts.values()) == [4, 4, 4, 5]


def test_fips_mask_and_challenge_input_lengths_are_disjoint() -> None:
    assert [w1encode_length_bytes(parameters) for parameters in PARAMETER_SETS] == [
        768,
        768,
        1024,
    ]
    assert [
        commitment_hash_input_length_bytes(parameters)
        for parameters in PARAMETER_SETS
    ] == [832, 832, 1088]
    assert 66 not in {832, 1088}
    assert 128 not in {66, 832, 1088}
    assert global_xof_source_hit_upper_bound(2**64) < 2.0**-191


def test_modular_rank_and_ntt_defect() -> None:
    assert matrix_rank_mod(((1, 2), (2, 4)), 5) == 1
    lanes = (
        ((1, 0), (0, 1)),
        ((1, 2), (2, 4)),
        ((0, 0), (0, 0)),
    )
    assert ntt_rank_defect(lanes, 5) == 0 + 1 + 2


def test_rectangular_rank_counts_partition_all_matrices() -> None:
    q, rows, columns = 5, 3, 2
    assert sum(
        rank_count_rectangular(q, rows, columns, rank)
        for rank in range(columns + 1)
    ) == (
        q ** (rows * columns)
    )


def test_general_rank_bucket_bound_on_a_small_quantized_map() -> None:
    q = 5
    fibers: Counter[tuple[int, int, int]] = Counter()
    for left in range(q):
        for right in range(q):
            exact = (left, right, (left + right) % q)
            quantized = (exact[0] // 2, exact[1] // 2, exact[2] // 2)
            fibers[quantized] += 1
    # Every scalar quantizer bucket contains at most two field elements and
    # the 3-by-2 map has full column rank.
    assert max(fibers.values()) <= rank_bucket_fiber_upper_bound(q, 2, 2, 2)


def test_uniform_rank_bucket_bound_is_sharp_for_a_projection() -> None:
    q, dimension, rank, bucket = 5, 3, 2, 2
    fibers: Counter[tuple[int, int]] = Counter()
    for first in range(q):
        for second in range(q):
            for _free in range(q):
                fibers[(first // bucket, second // bucket)] += 1
    assert max(fibers.values()) == rank_bucket_fiber_upper_bound(
        q, dimension, rank, bucket
    )


def test_standardized_fiber_margins_are_positive_and_ordered() -> None:
    rows = [analyze_fiber_parameter_set(parameters) for parameters in PARAMETER_SETS]
    assert [row.defect_budget_for_qh_2pow64_tv_2pow_minus128 for row in rows] == [
        51,
        272,
        400,
    ]
    assert all(row.random_matrix_bad_probability_bits > 200 for row in rows)
    assert rows[0].zero_defect_min_entropy_bits > 470
    assert rows[1].zero_defect_min_entropy_bits > 1_280
    assert rows[2].zero_defect_min_entropy_bits > 1_790
    assert all(row.budget_endpoint_accepted_law_exponent > 128 for row in rows)
    assert all(row.single_xof_source_term_exponent > 191 for row in rows)
    assert all(row.single_xof_combined_distance_exponent > 128 for row in rows)
    assert all(row.classical_retry_combined_distance_exponent > 128 for row in rows)
    assert all(
        row.classical_retry_combined_distance_exponent
        <= row.single_xof_combined_distance_exponent + 1e-10
        for row in rows
    )
    assert [
        row.qrom_defect_budget_for_q0_2pow64_tv_2pow_minus128 for row in rows
    ] == [27, 240, 368]
    assert all(
        row.qrom_budget_endpoint_restart_state_exponent > 128 for row in rows
    )
    assert all(row.qrom_random_matrix_bad_probability_bits > 280 for row in rows)


def test_fiber_bound_is_clipped_by_source_size() -> None:
    parameters = PARAMETER_SETS[0]
    assert commitment_fiber_upper_bound(
        parameters, parameters.response_dimension, Q
    ) == (
        2 * parameters.gamma1
    ) ** parameters.response_dimension


def test_defect_tail_decreases_with_the_allowed_budget() -> None:
    assert defect_tail_log2(17, 3, 2, 3, 2) < defect_tail_log2(
        17, 3, 2, 3, 1
    )
