"""Exact multi-threshold, multi-dimensional common-support sensitivity data.

The scale for each (dimension, threshold) pair is the first scale at which the
cube reaches the threshold.  Every family is then evaluated at that identical
integer scale.  This avoids an unproved monotonicity assumption for hybrid
ratios while adding an exact 0.99 sensitivity layer and a three-metric Pareto
audit.
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import asdict, dataclass, replace
from fractions import Fraction
from math import sqrt
from pathlib import Path
from typing import Sequence

from .fswa import Family, common_core_metrics
from .parameter_experiment import _parse_fraction, optimize_family

FAMILIES: tuple[Family, ...] = (
    "cube",
    "cross_polytope",
    "hexagon_blocks",
    "hybrid_full",
    "hybrid_blocks_4",
    "hybrid_blocks_8",
)


@dataclass(frozen=True)
class SensitivityRow:
    dimension: int
    secret_l1_radius: int
    anchor_threshold: str
    cube_first_feasible_scale: int
    family: str
    acceptance_exact: str
    acceptance: float
    reciprocal_acceptance: float
    target_count: int
    target_support_log_cardinality: int
    target_coordinate_box_upper_bound: int
    target_max_l2_squared: int
    target_max_l2: float
    pareto_optimal: bool


def _valid(family: Family, dimension: int) -> bool:
    if family == "hexagon_blocks":
        return dimension % 2 == 0
    if family == "hybrid_blocks_4":
        return dimension % 4 == 0
    if family == "hybrid_blocks_8":
        return dimension % 8 == 0
    return True


def _dominates(left: SensitivityRow, right: SensitivityRow) -> bool:
    weak = (
        Fraction(left.acceptance_exact) >= Fraction(right.acceptance_exact)
        and left.target_max_l2_squared <= right.target_max_l2_squared
        and left.target_support_log_cardinality
        <= right.target_support_log_cardinality
    )
    strict = (
        Fraction(left.acceptance_exact) > Fraction(right.acceptance_exact)
        or left.target_max_l2_squared < right.target_max_l2_squared
        or left.target_support_log_cardinality
        < right.target_support_log_cardinality
    )
    return weak and strict


def run_sensitivity(
    dimensions: Sequence[int],
    secret_l1_radius: int,
    thresholds: Sequence[Fraction],
) -> list[SensitivityRow]:
    rows: list[SensitivityRow] = []
    for dimension in dimensions:
        for threshold in thresholds:
            anchor = optimize_family(
                "cube", dimension, secret_l1_radius, [threshold]
            )[0].source_scale
            group: list[SensitivityRow] = []
            for family in FAMILIES:
                if not _valid(family, dimension):
                    continue
                metrics = common_core_metrics(
                    family, dimension, anchor, secret_l1_radius
                )
                reciprocal = Fraction(
                    metrics.source_count, metrics.target_count
                )
                target_coordinate_radius = max(anchor - secret_l1_radius, 0)
                group.append(
                    SensitivityRow(
                        dimension=dimension,
                        secret_l1_radius=secret_l1_radius,
                        anchor_threshold=(
                            f"{threshold.numerator}/{threshold.denominator}"
                        ),
                        cube_first_feasible_scale=anchor,
                        family=family,
                        acceptance_exact=(
                            f"{metrics.acceptance.numerator}/"
                            f"{metrics.acceptance.denominator}"
                        ),
                        acceptance=float(metrics.acceptance),
                        reciprocal_acceptance=float(reciprocal),
                        target_count=metrics.target_count,
                        target_support_log_cardinality=(
                            metrics.target_count - 1
                        ).bit_length(),
                        target_coordinate_box_upper_bound=(
                            dimension
                            * (2 * target_coordinate_radius).bit_length()
                        ),
                        target_max_l2_squared=metrics.target_max_l2_squared,
                        target_max_l2=sqrt(metrics.target_max_l2_squared),
                        pareto_optimal=False,
                    )
                )
            group = [
                replace(
                    row,
                    pareto_optimal=not any(
                        _dominates(other, row) for other in group if other is not row
                    ),
                )
                for row in group
            ]
            rows.extend(group)
    return rows


def write_csv(rows: Sequence[SensitivityRow], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(asdict(rows[0]).keys()))
        writer.writeheader()
        writer.writerows(asdict(row) for row in rows)


def write_markdown(rows: Sequence[SensitivityRow], path: Path) -> None:
    lines = [
        "# Exact common-support sensitivity and Pareto audit\n\n",
        "For each dimension and rational threshold, the common integer scale "
        "is the first scale at which the cube reaches that threshold. All "
        "families are evaluated exactly at the same scale. This is a "
        "sensitivity comparison, not a claim that the scale is first feasible "
        "for a non-cube family. `pareto` uses three directions: maximize exact "
        "acceptance, minimize exact squared maximum norm, and minimize the "
        "optimal fixed-length rank payload.\n\n",
        "| n | anchor A | scale | family | A | 1/A | max l2 | optimal "
        "rank bits | box upper bound | Pareto |\n",
        "|---:|---:|---:|---|---:|---:|---:|---:|---:|:---:|\n",
    ]
    for row in rows:
        lines.append(
            f"| {row.dimension} | {row.anchor_threshold} | "
            f"{row.cube_first_feasible_scale} | {row.family} | "
            f"{row.acceptance:.12f} | {row.reciprocal_acceptance:.6f} | "
            f"{row.target_max_l2:.4f} | "
            f"{row.target_support_log_cardinality} | "
            f"{row.target_coordinate_box_upper_bound} | "
            f"{'yes' if row.pareto_optimal else 'no'} |\n"
        )
    path.write_text("".join(lines), encoding="utf-8")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dimensions", nargs="+", type=int, default=[8, 16, 32])
    parser.add_argument("--secret-l1", type=int, default=2)
    parser.add_argument(
        "--thresholds",
        nargs="+",
        type=_parse_fraction,
        default=[
            Fraction(1, 2),
            Fraction(3, 4),
            Fraction(9, 10),
            Fraction(99, 100),
        ],
    )
    parser.add_argument(
        "--output-prefix",
        type=Path,
        default=Path("results") / "common_core_sensitivity",
    )
    args = parser.parse_args(argv)
    rows = run_sensitivity(args.dimensions, args.secret_l1, args.thresholds)
    write_csv(rows, args.output_prefix.with_suffix(".csv"))
    write_markdown(rows, args.output_prefix.with_suffix(".md"))
    print(f"wrote {len(rows)} exact sensitivity rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
