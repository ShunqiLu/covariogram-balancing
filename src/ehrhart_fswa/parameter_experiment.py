"""Exact common-core parameter optimization for uniform FSwA geometry."""

from __future__ import annotations

import argparse
import csv
from dataclasses import asdict, dataclass
from fractions import Fraction
from math import isqrt, log2, sqrt
from pathlib import Path
from typing import Sequence

from .fswa import CommonCoreMetrics, Family, common_core_metrics

FAMILIES: tuple[Family, ...] = (
    "cube",
    "cross_polytope",
    "cross_blocks_2",
    "cross_blocks_4",
    "cross_blocks_8",
    "hexagon_blocks",
    "hybrid_full",
    "hybrid_blocks_4",
    "hybrid_blocks_8",
)


@dataclass(frozen=True)
class OptimizedRow:
    family: str
    geometry_class: str
    source_constraint: str
    dimension: int
    secret_l1_radius: int
    required_acceptance: str
    source_scale: int
    acceptance_expression: str
    acceptance_exact: str
    acceptance: float
    reciprocal_acceptance_exact: str
    reciprocal_acceptance: float
    source_count: int
    target_count: int
    target_entropy_bits: float
    target_support_log_cardinality: int
    target_coordinate_box_upper_bound: int
    source_max_l2_squared: int
    target_max_l2_squared: int
    target_max_l2: float


def _constraint_and_expression(metrics: CommonCoreMetrics) -> tuple[str, str]:
    """Return explicit shape constraints and a compact exact count ratio."""

    family = metrics.family
    d = metrics.dimension
    t = metrics.source_scale
    s = metrics.secret_l1_radius
    if family == "cube":
        return f"||x||_inf <= {t}", f"({2*(t-s)+1}/{2*t+1})^{d}"
    if family == "cross_polytope":
        return f"||x||_1 <= {t}", f"L_{d}({t-s})/L_{d}({t})"
    if family.startswith("cross_blocks_"):
        block = int(family.rsplit("_", 1)[1])
        blocks = d // block
        return (
            f"{blocks} blocks: ||x_block||_1 <= {t}",
            f"(L_{block}({t-s})/L_{block}({t}))^{blocks}",
        )
    if family == "hexagon_blocks":
        blocks = d // 2
        return (
            f"{blocks} blocks: |x|,|y|,|x+y| <= {t}",
            f"(H({t-s})/H({t}))^{blocks}",
        )
    block = d if family == "hybrid_full" else int(family.rsplit("_", 1)[1])
    blocks = d // block
    source_l1 = isqrt(t * t * block)
    target_coordinate = t - s
    target_l1 = source_l1 - s
    prefix = "" if blocks == 1 else f"{blocks} blocks: "
    return (
        f"{prefix}||x_block||_inf <= {t}, ||x_block||_1 <= {source_l1}",
        f"(C_{block}({target_coordinate},{target_l1})/"
        f"C_{block}({t},{source_l1}))^{blocks}",
    )


def _valid_family_dimension(family: Family, dimension: int) -> bool:
    if family == "hexagon_blocks":
        return dimension % 2 == 0
    if family == "hybrid_blocks_4":
        return dimension % 4 == 0
    if family == "hybrid_blocks_8":
        return dimension % 8 == 0
    if family == "cross_blocks_2":
        return dimension % 2 == 0
    if family == "cross_blocks_4":
        return dimension % 4 == 0
    if family == "cross_blocks_8":
        return dimension % 8 == 0
    return True


def _row(metrics: CommonCoreMetrics, threshold: Fraction) -> OptimizedRow:
    target_coordinate_radius = max(metrics.source_scale - metrics.secret_l1_radius, 0)
    bits_per_coordinate = (2 * target_coordinate_radius).bit_length()
    expected = metrics.expected_trials
    if expected is None:
        raise ValueError("an optimized row must have nonzero acceptance")
    geometry_class = "integral_rational"
    if metrics.family.startswith("hybrid_"):
        if metrics.family == "hybrid_full":
            block_dimension = metrics.dimension
        else:
            block_dimension = int(metrics.family.rsplit("_", 1)[1])
        if isqrt(block_dimension) ** 2 != block_dimension:
            geometry_class = "irrational_sqrt_threshold"
    source_constraint, acceptance_expression = _constraint_and_expression(metrics)
    return OptimizedRow(
        family=metrics.family,
        geometry_class=geometry_class,
        source_constraint=source_constraint,
        dimension=metrics.dimension,
        secret_l1_radius=metrics.secret_l1_radius,
        required_acceptance=f"{threshold.numerator}/{threshold.denominator}",
        source_scale=metrics.source_scale,
        acceptance_expression=acceptance_expression,
        acceptance_exact=(
            f"{metrics.acceptance.numerator}/{metrics.acceptance.denominator}"
        ),
        acceptance=float(metrics.acceptance),
        reciprocal_acceptance_exact=f"{expected.numerator}/{expected.denominator}",
        reciprocal_acceptance=float(expected),
        source_count=metrics.source_count,
        target_count=metrics.target_count,
        target_entropy_bits=log2(metrics.target_count),
        target_support_log_cardinality=(metrics.target_count - 1).bit_length(),
        target_coordinate_box_upper_bound=metrics.dimension * bits_per_coordinate,
        source_max_l2_squared=metrics.source_max_l2_squared,
        target_max_l2_squared=metrics.target_max_l2_squared,
        target_max_l2=sqrt(metrics.target_max_l2_squared),
    )


def optimize_family(
    family: Family,
    dimension: int,
    secret_l1_radius: int,
    thresholds: Sequence[Fraction],
    *,
    max_scale: int = 10_000,
) -> list[OptimizedRow]:
    """Find the first integer scale meeting each threshold by exhaustive scan.

    No monotonicity assumption about lattice-point ratios is used.
    """

    if not thresholds:
        return []
    ordered = sorted(set(thresholds))
    if ordered[0] <= 0 or ordered[-1] >= 1:
        raise ValueError("acceptance thresholds must lie strictly between 0 and 1")
    unresolved = list(ordered)
    rows: dict[Fraction, OptimizedRow] = {}
    for scale in range(secret_l1_radius, max_scale + 1):
        metrics = common_core_metrics(family, dimension, scale, secret_l1_radius)
        while unresolved and metrics.acceptance >= unresolved[0]:
            threshold = unresolved.pop(0)
            rows[threshold] = _row(metrics, threshold)
        if not unresolved:
            return [rows[threshold] for threshold in thresholds]
    raise RuntimeError(
        f"{family} in dimension {dimension} did not reach all thresholds "
        f"through scale {max_scale}"
    )


def run_optimization(
    dimensions: Sequence[int],
    secret_l1_radius: int,
    thresholds: Sequence[Fraction],
) -> list[OptimizedRow]:
    rows: list[OptimizedRow] = []
    for dimension in dimensions:
        for family in FAMILIES:
            if _valid_family_dimension(family, dimension):
                rows.extend(
                    optimize_family(family, dimension, secret_l1_radius, thresholds)
                )
    return rows


def write_csv(rows: Sequence[OptimizedRow], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(asdict(rows[0]).keys()))
        writer.writeheader()
        for row in rows:
            writer.writerow(asdict(row))


def write_markdown(rows: Sequence[OptimizedRow], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Exact common-core FSwA parameter optimization\n\n",
        "For each family, this table gives the smallest integer source scale "
        "found by exhaustive scan whose exact common-core acceptance reaches "
        "the requested threshold. The secret support is the full integer "
        "`l1` ball of radius `secret_l1_radius` in the CSV. `L_b(t)` is the "
        "cross-polytope lattice count, `H(t)=3t^2+3t+1`, and `C_b(B,L)` "
        "counts `|x_i|<=B, ||x||_1<=L`. Each symbolic expression and the "
        "reduced fraction stored in the CSV are exact.\n\n",
        "The first bit column is the optimal fixed-length response-component "
        "payload `ceil(log2 |T|)`, attained by public rank/unrank; the second "
        "is a fixed-width coordinate payload. Both exclude headers, seeds, "
        "challenges, hints, framing and entropy-coder overhead.\n\n",
        "| family | n | source constraint | target A | scale | exact A | "
        "A (decimal) | 1/A | max target l2 | optimal rank bits | coordinate bits |\n",
        "|---|---:|---|---:|---:|---|---:|---:|---:|---:|---:|\n",
    ]
    for row in rows:
        lines.append(
            f"| {row.family} | {row.dimension} | `{row.source_constraint}` | "
            f"{row.required_acceptance} | {row.source_scale} | "
            f"`{row.acceptance_expression}` | {row.acceptance:.12f} | "
            f"{row.reciprocal_acceptance:.6f} | "
            f"{row.target_max_l2:.4f} | {row.target_support_log_cardinality} | "
            f"{row.target_coordinate_box_upper_bound} |\n"
        )
    path.write_text("".join(lines), encoding="utf-8")


def _parse_fraction(value: str) -> Fraction:
    result = Fraction(value)
    if not 0 < result < 1:
        raise argparse.ArgumentTypeError("threshold must lie strictly between 0 and 1")
    return result


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dimensions", nargs="+", type=int, default=[8, 16, 32])
    parser.add_argument("--secret-l1", type=int, default=2)
    parser.add_argument(
        "--thresholds",
        nargs="+",
        type=_parse_fraction,
        default=[Fraction(1, 2), Fraction(3, 4), Fraction(9, 10)],
    )
    parser.add_argument(
        "--output-prefix", type=Path, default=Path("results") / "common_core"
    )
    args = parser.parse_args(argv)
    rows = run_optimization(args.dimensions, args.secret_l1, args.thresholds)
    csv_path = args.output_prefix.with_suffix(".csv")
    markdown_path = args.output_prefix.with_suffix(".md")
    write_csv(rows, csv_path)
    write_markdown(rows, markdown_path)
    print(f"wrote {len(rows)} optimized rows to {csv_path} and {markdown_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
