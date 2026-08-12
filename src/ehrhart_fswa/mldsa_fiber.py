"""Public-matrix commitment-fiber certificates for the ML-DSA z layer."""

from __future__ import annotations

import argparse
import csv
from dataclasses import asdict, dataclass
from math import log2, prod
from pathlib import Path
from typing import Sequence

from ehrhart_fswa.mldsa_case import (
    MLDSAParameters,
    PARAMETER_SETS,
    analyze_parameter_set,
)


Q = 8_380_417
N = 256


def w1encode_length_bytes(parameters: MLDSAParameters) -> int:
    """Return the exact FIPS 204 w1Encode output length in bytes."""

    maximum = (Q - 1) // (2 * parameters.gamma2) - 1
    return 32 * parameters.k * maximum.bit_length()


def commitment_hash_input_length_bytes(parameters: MLDSAParameters) -> int:
    """Return ``len(mu || w1Encode(w1))`` for one parameter set."""

    return 64 + w1encode_length_bytes(parameters)


def global_xof_source_hit_upper_bound(prior_queries: int) -> float:
    """Classical ideal-XOF source-hit bound for a hidden 256-bit K."""

    if prior_queries < 0:
        raise ValueError("prior_queries must be nonnegative")
    return prior_queries * (2.0**-256 + 2.0**-512)


def centered_mod(value: int, modulus: int) -> int:
    """Return the representative in ``(-modulus/2, modulus/2]``."""

    if modulus <= 0 or modulus % 2:
        raise ValueError("modulus must be positive and even")
    residue = value % modulus
    if residue > modulus // 2:
        residue -= modulus
    return residue


def highbits(value: int, q: int, gamma2: int) -> int:
    """Reference FIPS 204 Decompose/HighBits for one coefficient."""

    alpha = 2 * gamma2
    if q <= 1 or gamma2 <= 0 or (q - 1) % alpha:
        raise ValueError("require 2*gamma2 to divide q-1")
    positive = value % q
    low = centered_mod(positive, alpha)
    if positive - low == q - 1:
        return 0
    return (positive - low) // alpha


def highbits_max_bucket_size(q: int, gamma2: int) -> int:
    """Return the maximum number of residues with one HighBits value."""

    alpha = 2 * gamma2
    if q <= 1 or gamma2 <= 0 or (q - 1) % alpha:
        raise ValueError("require 2*gamma2 to divide q-1")
    # q = m*alpha+1: m output buckets split q residues, and the exceptional
    # Decompose branch puts the unique surplus residue into bucket zero.
    return alpha + 1


def matrix_rank_mod(matrix: Sequence[Sequence[int]], q: int) -> int:
    """Compute matrix rank over the prime field F_q."""

    if q <= 1 or not matrix or not matrix[0]:
        raise ValueError("require a nonempty matrix and q > 1")
    columns = len(matrix[0])
    if any(len(row) != columns for row in matrix):
        raise ValueError("matrix rows must have equal length")
    work = [[entry % q for entry in row] for row in matrix]
    rank = 0
    for column in range(columns):
        pivot = next(
            (row for row in range(rank, len(work)) if work[row][column]), None
        )
        if pivot is None:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        inverse = pow(work[rank][column], -1, q)
        work[rank] = [(entry * inverse) % q for entry in work[rank]]
        for row in range(len(work)):
            if row == rank or not work[row][column]:
                continue
            factor = work[row][column]
            work[row] = [
                (left - factor * right) % q
                for left, right in zip(work[row], work[rank], strict=True)
            ]
        rank += 1
        if rank == len(work):
            break
    return rank


def ntt_rank_defect(
    matrix_lanes: Sequence[Sequence[Sequence[int]]], q: int = Q
) -> int:
    """Sum the column-rank deficiencies of rectangular NTT matrix lanes."""

    if not matrix_lanes:
        raise ValueError("at least one NTT lane is required")
    rows = len(matrix_lanes[0])
    if rows == 0 or not matrix_lanes[0][0]:
        raise ValueError("matrix block must be nonempty")
    columns = len(matrix_lanes[0][0])
    if rows < columns:
        raise ValueError("the matrix must have at least as many rows as columns")
    defect = 0
    for lane in matrix_lanes:
        if len(lane) != rows or any(len(row) != columns for row in lane):
            raise ValueError("every NTT lane must have the same rectangular shape")
        defect += columns - matrix_rank_mod(lane, q)
    return defect


def rank_bucket_fiber_upper_bound(
    q: int,
    domain_dimension: int,
    linear_rank: int,
    maximum_bucket_size: int,
    source_size: int | None = None,
) -> int:
    """Certificate for a coordinatewise-quantized finite-field linear map.

    A rank-``linear_rank`` map from ``F_q^domain_dimension`` has a set of
    ``linear_rank`` independent output coordinates.  Fixing their quantized
    values leaves at most ``maximum_bucket_size**linear_rank`` exact outputs,
    each with ``q**(domain_dimension-linear_rank)`` preimages.
    """

    if q <= 1 or domain_dimension < 0:
        raise ValueError("q must exceed one and the domain dimension be nonnegative")
    if not 0 <= linear_rank <= domain_dimension:
        raise ValueError("linear rank must lie between zero and the domain dimension")
    if maximum_bucket_size <= 0:
        raise ValueError("maximum bucket size must be positive")
    ambient_bound = (
        maximum_bucket_size**linear_rank
        * q ** (domain_dimension - linear_rank)
    )
    if source_size is None:
        return ambient_bound
    if source_size < 0:
        raise ValueError("source size must be nonnegative")
    return min(source_size, ambient_bound)


def commitment_fiber_upper_bound(
    parameters: MLDSAParameters, rank_defect: int, q: int = Q
) -> int:
    """Return ``min(|S|, B^(D-delta) q^delta)`` exactly."""

    dimension = parameters.response_dimension
    if not 0 <= rank_defect <= dimension:
        raise ValueError("rank_defect must lie between zero and D")
    bucket = highbits_max_bucket_size(q, parameters.gamma2)
    source_size = (2 * parameters.gamma1) ** dimension
    return rank_bucket_fiber_upper_bound(
        q,
        dimension,
        dimension - rank_defect,
        bucket,
        source_size,
    )


def rank_count_rectangular(q: int, rows: int, columns: int, rank: int) -> int:
    """Count ``rows``-by-``columns`` matrices of a given rank over F_q."""

    if (
        q <= 1
        or rows < 0
        or columns < 0
        or not 0 <= rank <= min(rows, columns)
    ):
        raise ValueError("invalid field size, matrix size, or rank")
    if rank == 0:
        return 1
    numerator = prod(
        (q**rows - q**i) * (q**columns - q**i) for i in range(rank)
    )
    denominator = prod(q**rank - q**i for i in range(rank))
    quotient, remainder = divmod(numerator, denominator)
    if remainder:
        raise ArithmeticError("rank-count formula was not integral")
    return quotient


def _logadd2(left: float, right: float) -> float:
    if left == float("-inf"):
        return right
    if right == float("-inf"):
        return left
    if left < right:
        left, right = right, left
    difference = right - left
    if difference < -1_070:
        return left
    return left + log2(1.0 + 2.0**difference)


def qrom_restart_distance_exponent(
    min_entropy_bits: float,
    acceptance: float,
    initial_queries: int,
) -> float:
    """Return ``-log2`` of the adaptive-reprogramming restart bound.

    The two terms are the Jensen-closed form of the geometrically weighted
    GHHM21 Theorem 1, equation (2), single-reprogramming errors.
    """

    if min_entropy_bits < 0:
        min_entropy_bits = 0.0
    if not 0 < acceptance <= 1:
        raise ValueError("acceptance must lie in (0,1]")
    if initial_queries < 0:
        raise ValueError("initial_queries must be nonnegative")
    survival = 1.0 - acceptance
    square_root_factor = (
        initial_queries + survival / acceptance
    ) ** 0.5 / acceptance
    linear_factor = 0.5 * (
        initial_queries / acceptance + survival / acceptance**2
    )
    square_root_log2 = (
        float("-inf")
        if square_root_factor == 0
        else -min_entropy_bits / 2 + log2(square_root_factor)
    )
    linear_log2 = (
        float("-inf")
        if linear_factor == 0
        else -min_entropy_bits + log2(linear_factor)
    )
    total_log2 = _logadd2(square_root_log2, linear_log2)
    return float("inf") if total_log2 == float("-inf") else -total_log2


def defect_tail_log2(
    q: int,
    rows: int,
    columns: int,
    lanes: int,
    maximum_allowed_defect: int,
) -> float:
    """Log2 probability that total defect exceeds a threshold.

    Every lane is an independent uniform square matrix.  The one-lane rank
    counts are exact; only the final log-domain evaluation is rounded.
    """

    if lanes <= 0 or maximum_allowed_defect < 0:
        raise ValueError("lanes must be positive and the threshold nonnegative")
    if rows < columns:
        raise ValueError("rows must be at least columns")
    total_log2 = rows * columns * log2(q)
    lane_log_probabilities = [
        log2(rank_count_rectangular(q, rows, columns, columns - defect))
        - total_log2
        for defect in range(columns + 1)
    ]
    distribution = [0.0]
    for _ in range(lanes):
        updated = [float("-inf")] * (len(distribution) + columns)
        for accumulated, log_probability in enumerate(distribution):
            for defect, lane_log_probability in enumerate(lane_log_probabilities):
                index = accumulated + defect
                updated[index] = _logadd2(
                    updated[index], log_probability + lane_log_probability
                )
        distribution = updated
    tail = float("-inf")
    for log_probability in distribution[maximum_allowed_defect + 1 :]:
        tail = _logadd2(tail, log_probability)
    return tail


@dataclass(frozen=True)
class MLDSAFiberRow:
    parameter_set: str
    ell: int
    response_dimension: int
    gamma1: int
    gamma2: int
    highbits_max_bucket: int
    zero_defect_min_entropy_bits: float
    zero_defect_tv_exponent_before_queries: float
    defect_budget_for_qh_2pow64_tv_2pow_minus128: int
    budget_endpoint_accepted_law_exponent: float
    single_xof_source_term_exponent: float
    single_xof_combined_distance_exponent: float
    classical_retry_combined_distance_exponent: float
    qrom_zero_defect_restart_state_exponent: float
    qrom_defect_budget_for_q0_2pow64_tv_2pow_minus128: int
    qrom_budget_endpoint_restart_state_exponent: float
    qrom_random_matrix_bad_probability_log2: float
    qrom_random_matrix_bad_probability_bits: float
    random_matrix_bad_probability_log2: float
    random_matrix_bad_probability_bits: float
    zero_defect_probability: float


def analyze_fiber_parameter_set(parameters: MLDSAParameters) -> MLDSAFiberRow:
    dimension = parameters.response_dimension
    bucket = highbits_max_bucket_size(Q, parameters.gamma2)
    entropy = dimension * log2((2 * parameters.gamma1) / bucket)
    geometric = analyze_parameter_set(parameters)
    exponent = entropy + log2(geometric.fips_z_acceptance)
    defect_penalty = log2(Q / bucket)
    defect_budget = int((exponent - (128 + 64)) // defect_penalty)
    if defect_budget < 0:
        raise ValueError("parameter set has no 2^-128 accepted-law budget")
    endpoint_exponent = exponent - defect_budget * defect_penalty - 64
    source_hit = global_xof_source_hit_upper_bound(2**64)
    source_term = source_hit / geometric.fips_z_acceptance
    source_term_exponent = -log2(source_term)
    combined_exponent = -log2(2.0**-endpoint_exponent + source_term)
    endpoint_entropy = entropy - defect_budget * defect_penalty
    acceptance = geometric.fips_z_acceptance
    retry_challenge_term = 2.0**-endpoint_entropy * (
        2.0**64 / acceptance + (1.0 - acceptance) / acceptance**2
    )
    retry_combined_exponent = -log2(retry_challenge_term + source_term)
    # The quantum restart interface sums the exact one-reprogramming error
    # sqrt((q0+i)*2^-h) + (q0+i)*2^-h/2.  These columns use an independent
    # mask source, an atomic signing invocation, and q0 <= 2^64 before it.
    qrom_zero_exponent = qrom_restart_distance_exponent(
        entropy, acceptance, 2**64
    )
    qrom_defect_budget = -1
    qrom_endpoint_exponent = float("-inf")
    for defect in range(dimension + 1):
        candidate_exponent = qrom_restart_distance_exponent(
            entropy - defect * defect_penalty,
            acceptance,
            2**64,
        )
        if candidate_exponent < 128:
            break
        qrom_defect_budget = defect
        qrom_endpoint_exponent = candidate_exponent
    if qrom_defect_budget < 0:
        raise ValueError("parameter set has no 2^-128 QROM accepted-law budget")
    qrom_tail_log2 = defect_tail_log2(
        Q,
        parameters.k,
        parameters.ell,
        N,
        qrom_defect_budget,
    )
    tail_log2 = defect_tail_log2(
        Q,
        parameters.k,
        parameters.ell,
        N,
        defect_budget,
    )
    invertible_lane_probability = prod(
        1.0 - Q ** (-index)
        for index in range(
            parameters.k - parameters.ell + 1,
            parameters.k + 1,
        )
    )
    return MLDSAFiberRow(
        parameter_set=parameters.name,
        ell=parameters.ell,
        response_dimension=dimension,
        gamma1=parameters.gamma1,
        gamma2=parameters.gamma2,
        highbits_max_bucket=bucket,
        zero_defect_min_entropy_bits=entropy,
        zero_defect_tv_exponent_before_queries=exponent,
        defect_budget_for_qh_2pow64_tv_2pow_minus128=defect_budget,
        budget_endpoint_accepted_law_exponent=endpoint_exponent,
        single_xof_source_term_exponent=source_term_exponent,
        single_xof_combined_distance_exponent=combined_exponent,
        classical_retry_combined_distance_exponent=retry_combined_exponent,
        qrom_zero_defect_restart_state_exponent=qrom_zero_exponent,
        qrom_defect_budget_for_q0_2pow64_tv_2pow_minus128=qrom_defect_budget,
        qrom_budget_endpoint_restart_state_exponent=qrom_endpoint_exponent,
        qrom_random_matrix_bad_probability_log2=qrom_tail_log2,
        qrom_random_matrix_bad_probability_bits=-qrom_tail_log2,
        random_matrix_bad_probability_log2=tail_log2,
        random_matrix_bad_probability_bits=-tail_log2,
        zero_defect_probability=invertible_lane_probability**N,
    )


def run_fiber_cases() -> list[MLDSAFiberRow]:
    return [analyze_fiber_parameter_set(parameters) for parameters in PARAMETER_SETS]


def write_csv(rows: Sequence[MLDSAFiberRow], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(asdict(rows[0]).keys()))
        writer.writeheader()
        writer.writerows(asdict(row) for row in rows)


def write_markdown(rows: Sequence[MLDSAFiberRow], path: Path) -> None:
    lines = [
        "# ML-DSA public-matrix commitment-fiber certificate\n\n",
        "For the full public matrix, `delta(A)` is the sum of its 256 "
        "NTT-lane column-rank deficiencies.  FIPS 204 HighBits has "
        "maximum bucket size `B=2*gamma2+1`.  The deterministic certificate is\n\n",
        "`M_A <= min((2*gamma1)^D, B^(D-delta)*q^delta)` and "
        "`h_A >= max(0, D*log2(2*gamma1/B)-delta*log2(q/B))`.\n\n",
        "The table uses `q_H <= 2^64` and target accepted-law distance "
        "`2^-128`.  The global-XOF columns additionally use `q_R <= 2^64` "
        "and the source-hit bound `zeta <= q_R*(2^-256+2^-512)`.  The last "
        "probability is over independent uniform NTT "
        "entries for the full rectangular matrix (the ideal-XOF model for "
        "ExpandA).\n\n",
        "| set | B | h at delta=0 | TV exponent at delta=0 | max delta | "
        "endpoint exponent | source exponent | one-trial combined | "
        "retry combined | "
        "Pr[random delta > max] | Pr[delta=0] |\n",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|\n",
    ]
    for row in rows:
        lines.append(
            f"| {row.parameter_set} | {row.highbits_max_bucket} | "
            f"{row.zero_defect_min_entropy_bits:.3f} | "
            f"{row.zero_defect_tv_exponent_before_queries:.3f} | "
            f"{row.defect_budget_for_qh_2pow64_tv_2pow_minus128} | "
            f"{row.budget_endpoint_accepted_law_exponent:.3f} | "
            f"{row.single_xof_source_term_exponent:.3f} | "
            f"{row.single_xof_combined_distance_exponent:.3f} | "
            f"{row.classical_retry_combined_distance_exponent:.3f} | "
            f"< 2^-{row.random_matrix_bad_probability_bits:.3f} | "
        f"{row.zero_defect_probability:.12f} |\n"
        )
    lines.extend(
        [
            "\n## Independent-mask-source QROM certificate\n\n",
            "Geometrically summing the exact adaptive-reprogramming errors "
            "`sqrt((q0+i)*2^-h)+(q0+i)*2^-h/2`, the next table uses an "
            "atomic signing invocation, `q0 <= 2^64`, and "
            "the same `2^-128` final restart-state target.  It does not "
            "include the single-global-XOF source "
            "restriction.\n\n",
            "| set | zero-defect exponent | max delta | endpoint exponent | "
            "Pr[random delta > max] |\n",
            "|---|---:|---:|---:|---:|\n",
        ]
    )
    for row in rows:
        lines.append(
            f"| {row.parameter_set} | "
            f"{row.qrom_zero_defect_restart_state_exponent:.3f} | "
            f"{row.qrom_defect_budget_for_q0_2pow64_tv_2pow_minus128} | "
            f"{row.qrom_budget_endpoint_restart_state_exponent:.3f} | "
            f"< 2^-{row.qrom_random_matrix_bad_probability_bits:.3f} |\n"
        )
    path.write_text("".join(lines), encoding="utf-8")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-prefix", type=Path, default=Path("results") / "mldsa_fiber"
    )
    args = parser.parse_args(argv)
    rows = run_fiber_cases()
    write_csv(rows, args.output_prefix.with_suffix(".csv"))
    write_markdown(rows, args.output_prefix.with_suffix(".md"))
    print(f"wrote {len(rows)} ML-DSA fiber rows to {args.output_prefix}.[csv|md]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
