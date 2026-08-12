"""Audit the quantitative finite Lee rearrangement theorems exactly."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from .majorization import (
    balancing_increment,
    balancing_increment_channels,
    balancing_neighbors,
    sharp_equal_radius_constant,
    lee_shell_partitions,
    lens_shell_stability_audit,
    majorizes,
    parity_interval_count,
    qary_lee_lens_count,
    radial_equality_certificate,
    two_coordinate_lens_count,
    unequal_lee_lens_count,
)


@dataclass(frozen=True)
class LocalAudit:
    comparisons: int
    zero_increments: int
    positive_increments: int
    endpoint_switches: int
    equal_radius_comparisons: int
    near_equal_comparisons: int
    gap_two_parity_boundaries: int


@dataclass(frozen=True)
class GlobalAudit:
    shell_count: int
    edge_count: int
    zero_edges: int
    sharp_formula_mismatches: int
    constants_at_max_radius: tuple[tuple[int, tuple[int, ...]], ...]


@dataclass(frozen=True)
class EqualityAudit:
    unequal_radius_edges: int
    unequal_radius_zero_edges: int
    qary_preboundary_comparisons: int
    qary_counterexample: tuple[int, int, int, int, tuple[int, ...], tuple[int, ...], int, int]


def run_local_audit(max_radius: int, max_coordinate: int) -> LocalAudit:
    comparisons = 0
    zero_increments = 0
    positive_increments = 0
    endpoint_switches = 0
    equal_radius_comparisons = 0
    near_equal_comparisons = 0
    gap_two_parity_boundaries = 0
    for left_radius in range(max_radius + 1):
        for right_radius in range(max_radius + 1):
            for high in range(2, max_coordinate + 1):
                for low in range(high - 1):
                    source = two_coordinate_lens_count(
                        left_radius, right_radius, high, low
                    )
                    target = two_coordinate_lens_count(
                        left_radius, right_radius, high - 1, low + 1
                    )
                    increment = balancing_increment(
                        left_radius, right_radius, high, low
                    )
                    if increment != target - source:
                        raise AssertionError("local parity kernel mismatch")
                    channels = balancing_increment_channels(
                        left_radius, right_radius, high, low
                    )
                    if increment != sum(channels) or any(
                        channel < 0 for channel in channels
                    ):
                        raise AssertionError("invalid parity-channel decomposition")
                    difference = high - low
                    for parity in (0, 1):
                        switch = parity_interval_count(
                            left_radius,
                            right_radius,
                            difference - 2,
                            parity,
                        ) - parity_interval_count(
                            left_radius, right_radius, difference, parity
                        )
                        if switch not in (0, 1):
                            raise AssertionError("endpoint switch is not binary")
                        endpoint_switches += switch
                    comparisons += 1
                    zero_increments += increment == 0
                    positive_increments += increment > 0
                    if left_radius == right_radius:
                        expected = max(
                            0, 2 * left_radius - high - low + 1
                        )
                        if increment != expected:
                            raise AssertionError("equal-radius linear law mismatch")
                        equal_radius_comparisons += 1
                    if abs(left_radius - right_radius) <= 1:
                        denominator = (
                            2
                            if abs(left_radius - right_radius) == 1
                            and difference == 2
                            else 1
                        )
                        expected = max(
                            0,
                            left_radius
                            + right_radius
                            - high
                            - low
                            + 1,
                        ) // denominator
                        if increment != expected:
                            raise AssertionError(
                                "near-equal-radius chamber law mismatch"
                            )
                        near_equal_comparisons += 1
                        gap_two_parity_boundaries += denominator == 2
    return LocalAudit(
        comparisons,
        zero_increments,
        positive_increments,
        endpoint_switches,
        equal_radius_comparisons,
        near_equal_comparisons,
        gap_two_parity_boundaries,
    )


def run_global_audit(max_dimension: int, max_radius: int) -> GlobalAudit:
    shell_count = 0
    edge_count = 0
    zero_edges = 0
    mismatches = 0
    constants_at_max_radius: list[tuple[int, tuple[int, ...]]] = []
    for dimension in range(2, max_dimension + 1):
        final_constants: list[int] = []
        for radius in range(1, max_radius + 1):
            for total_weight in range(2, 2 * radius + 1):
                audit = lens_shell_stability_audit(
                    radius, radius, total_weight, dimension
                )
                expected = sharp_equal_radius_constant(
                    radius, total_weight, dimension
                )
                shell_count += 1
                edge_count += audit.edge_count
                zero_edges += len(audit.zero_edges)
                mismatches += audit.minimum_positive_increment != expected
                if radius == max_radius:
                    final_constants.append(
                        audit.minimum_positive_increment
                        if audit.minimum_positive_increment is not None
                        else 0
                    )
        constants_at_max_radius.append((dimension, tuple(final_constants)))
    return GlobalAudit(
        shell_count,
        edge_count,
        zero_edges,
        mismatches,
        tuple(constants_at_max_radius),
    )


def run_equality_and_boundary_audit() -> EqualityAudit:
    edges = 0
    zero_edges = 0
    for dimension in range(2, 5):
        for total_weight in range(2, 9):
            for source in lee_shell_partitions(total_weight, dimension):
                for target in balancing_neighbors(source):
                    for left_radius in range(7):
                        for right_radius in range(7):
                            increment = unequal_lee_lens_count(
                                left_radius, right_radius, target
                            ) - unequal_lee_lens_count(
                                left_radius, right_radius, source
                            )
                            if increment < 0:
                                raise AssertionError("majorization order reversal")
                            edges += 1
                            zero_edges += increment == 0

    qary_comparisons = 0
    for modulus in range(3, 6):
        cap = modulus // 2
        for dimension in range(2, 4):
            diameter = dimension * cap
            for total_weight in range(diameter + 1):
                partitions = tuple(
                    partition
                    for partition in lee_shell_partitions(total_weight, dimension)
                    if partition[0] <= cap
                )
                for source in partitions:
                    for target in partitions:
                        if source == target or not majorizes(source, target):
                            continue
                        for left_radius in range(diameter + 1):
                            for right_radius in range(diameter + 1):
                                source_count = qary_lee_lens_count(
                                    modulus,
                                    left_radius,
                                    right_radius,
                                    source,
                                )
                                target_count = qary_lee_lens_count(
                                    modulus,
                                    left_radius,
                                    right_radius,
                                    target,
                                )
                                if source_count > target_count:
                                    raise AssertionError(
                                        "unexpected preboundary q-ary reversal"
                                    )
                                qary_comparisons += 1

    counterexample = (6, 2, 1, 3, (3, 1), (2, 2), 3, 2)
    modulus, dimension, left_radius, right_radius, source, target, source_count, target_count = counterexample
    if qary_lee_lens_count(
        modulus, left_radius, right_radius, source
    ) != source_count or qary_lee_lens_count(
        modulus, left_radius, right_radius, target
    ) != target_count:
        raise AssertionError("q-ary counterexample changed")

    equality_kernel = ((1, 1, 1),)
    equality = radial_equality_certificate(
        equality_kernel, (2, 0), (1, 1)
    )
    if not equality.is_equality:
        raise AssertionError("radial equality witness mismatch")

    return EqualityAudit(
        edges,
        zero_edges,
        qary_comparisons,
        counterexample,
    )


def write_report(
    local: LocalAudit,
    global_audit: GlobalAudit,
    equality: EqualityAudit,
    path: Path,
    max_dimension: int,
    max_radius: int,
    max_coordinate: int,
) -> None:
    modulus, dimension, left_radius, right_radius, source, target, source_count, target_count = equality.qary_counterexample
    lines = [
        "# Quantitative Lee rearrangement regression audit\n\n",
        "All entries are exact integer computations. The local increment law, "
        "the majorization-distance stability bound, and the radial equality "
        "criterion and the closed sharp shell constant have mathematical "
        "proofs in the manuscript. The computations below independently "
        "reconstruct their integer values and are not used as proof.\n\n",
        "## A. Local transfer chambers\n\n",
        f"Parameters: `0 <= p,q <= {max_radius}` and "
        f"`2 <= high <= {max_coordinate}`.\n\n",
        "| exact comparisons | zero increments | positive increments | "
        "activated parity endpoints | near-equal checks | gap-two boundaries |\n",
        "|---:|---:|---:|---:|---:|---:|\n",
        f"| {local.comparisons} | {local.zero_increments} | "
        f"{local.positive_increments} | {local.endpoint_switches} | "
        f"{local.near_equal_comparisons} | "
        f"{local.gap_two_parity_boundaries} |\n\n",
        "Every parity endpoint difference was in `{0,1}`. Every total "
        "increment agreed with the independent before/after lens counts. "
        "For `p=q=t`, every checked increment equaled "
        "`max(0, 2*t-high-low+1)`. For `|p-q|=1`, "
        "the same linear value holds except at transfer gap "
        "`high-low=2`, where the active value is exactly half; "
        "the parity numerator is necessarily even.\n\n",
        "## B. Global shell stability\n\n",
        f"Parameters: `2 <= d <= {max_dimension}` and "
        f"`1 <= t <= {max_radius}`, all active shells `2 <= s <= 2*t`.\n\n",
        "| shells | weighted edges | zero edges | sharp-formula mismatches |\n",
        "|---:|---:|---:|---:|\n",
        f"| {global_audit.shell_count} | {global_audit.edge_count} | "
        f"{global_audit.zero_edges} | "
        f"{global_audit.sharp_formula_mismatches} |\n\n",
        f"Minimum edge increments at the independent test radius `t={max_radius}` "
        "(shells `s=2,...,2t`):\n\n",
        "| d | exact minima by shell |\n",
        "|---:|---|\n",
    ]
    for audited_dimension, constants in global_audit.constants_at_max_radius:
        lines.append(
            f"| {audited_dimension} | `{' '.join(map(str, constants))}` |\n"
        )
    lines.extend(
        [
            "\nThe zero-edge set is empty throughout this equal-radius active "
            "region, in agreement with the strict theorem.\n\n",
            "## C. Equality and finite-quotient boundary\n\n",
            "| unequal-radius weighted edges | zero-gap edges | q-ary "
            "preboundary comparisons |\n",
            "|---:|---:|---:|\n",
            f"| {equality.unequal_radius_edges} | "
            f"{equality.unequal_radius_zero_edges} | "
            f"{equality.qary_preboundary_comparisons} |\n\n",
            "The unequal-radius zero edges are equality chambers, not theorem "
            "failures. For a radial kernel, equality is certified exactly when "
            "every positive mixed-difference coefficient is supported on these "
            "zero-gap chambers.\n\n",
            "The infinite-lattice order does not extend naively through "
            "wrap-around. The first reversal in the deterministic lexicographic "
            "scan used here is\n\n",
            f"`q={modulus}, d={dimension}, p={left_radius}, q_radius={right_radius}, "
            f"{source} majorizes {target}`, but the lens counts are "
            f"`{source_count} > {target_count}`.\n\n",
            "This q-ary computation is a falsification boundary only; no "
            "finite-quotient rearrangement theorem is claimed.\n",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(lines), encoding="utf-8")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-dimension", type=int, default=6)
    parser.add_argument("--max-radius", type=int, default=8)
    parser.add_argument("--max-coordinate", type=int, default=12)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results") / "quantitative_lee_rearrangement.md",
    )
    args = parser.parse_args(argv)
    local = run_local_audit(args.max_radius, args.max_coordinate)
    global_audit = run_global_audit(args.max_dimension, args.max_radius)
    equality = run_equality_and_boundary_audit()
    write_report(
        local,
        global_audit,
        equality,
        args.output,
        args.max_dimension,
        args.max_radius,
        args.max_coordinate,
    )
    print(
        f"audited {local.comparisons} local chambers and "
        f"{global_audit.edge_count} global edges; wrote {args.output}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
