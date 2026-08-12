"""Measure secret dependence of naive pairwise support conditioning."""

from __future__ import annotations

import argparse
import csv
from dataclasses import asdict, dataclass
from fractions import Fraction
from itertools import product
from pathlib import Path
from typing import Sequence

from .counts import hybrid_l1_radius
from .distributions import uniform_set_tv_distance
from .shifts import integer_l1_shifts


@dataclass(frozen=True)
class DistributionRow:
    family: str
    dimension: int
    scale: int
    secret_l1_radius: int
    source_count: int
    shift_count: int
    minimum_pairwise_acceptance_exact: str
    minimum_pairwise_acceptance: float
    common_core_acceptance_exact: str
    common_core_acceptance: float
    maximum_naive_output_tv_exact: str
    maximum_naive_output_tv: float
    common_target_output_tv_exact: str


def _source_points(family: str, dimension: int, scale: int) -> set[tuple[int, ...]]:
    def member(point: tuple[int, ...]) -> bool:
        if family == "cube":
            return True
        if family == "cross_polytope":
            return sum(map(abs, point)) <= scale
        if family == "hexagon_blocks":
            return all(
                max(abs(point[i]), abs(point[i + 1]), abs(point[i] + point[i + 1]))
                <= scale
                for i in range(0, dimension, 2)
            )
        if family == "hybrid_full":
            return sum(map(abs, point)) <= hybrid_l1_radius(scale, dimension)
        raise ValueError(f"unsupported family {family}")

    return {
        point
        for point in product(range(-scale, scale + 1), repeat=dimension)
        if member(point)
    }


def analyze_family(
    family: str, dimension: int, scale: int, secret_l1_radius: int
) -> DistributionRow:
    source = _source_points(family, dimension, scale)
    shifts = list(integer_l1_shifts(dimension, secret_l1_radius))
    shifted_sources = []
    naive_outputs = []
    for shift in shifts:
        shifted = {
            tuple(point[i] + shift[i] for i in range(dimension)) for point in source
        }
        shifted_sources.append(shifted)
        naive_outputs.append(source.intersection(shifted))

    minimum_pairwise_count = min(map(len, naive_outputs))
    common_core = set.intersection(*shifted_sources)
    maximum_tv = max(
        uniform_set_tv_distance(naive_outputs[left], naive_outputs[right])
        for left in range(len(naive_outputs))
        for right in range(left, len(naive_outputs))
    )
    minimum_pairwise = Fraction(minimum_pairwise_count, len(source))
    common_acceptance = Fraction(len(common_core), len(source))
    return DistributionRow(
        family=family,
        dimension=dimension,
        scale=scale,
        secret_l1_radius=secret_l1_radius,
        source_count=len(source),
        shift_count=len(shifts),
        minimum_pairwise_acceptance_exact=(
            f"{minimum_pairwise.numerator}/{minimum_pairwise.denominator}"
        ),
        minimum_pairwise_acceptance=float(minimum_pairwise),
        common_core_acceptance_exact=(
            f"{common_acceptance.numerator}/{common_acceptance.denominator}"
        ),
        common_core_acceptance=float(common_acceptance),
        maximum_naive_output_tv_exact=f"{maximum_tv.numerator}/{maximum_tv.denominator}",
        maximum_naive_output_tv=float(maximum_tv),
        common_target_output_tv_exact="0/1",
    )


def run_experiment(
    dimension: int, scale: int, secret_l1_radius: int
) -> list[DistributionRow]:
    families = ["cube", "cross_polytope", "hybrid_full"]
    if dimension % 2 == 0:
        families.append("hexagon_blocks")
    return [
        analyze_family(family, dimension, scale, secret_l1_radius)
        for family in families
    ]


def write_outputs(rows: Sequence[DistributionRow], prefix: Path) -> None:
    csv_path = prefix.with_suffix(".csv")
    markdown_path = prefix.with_suffix(".md")
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(asdict(rows[0]).keys()))
        writer.writeheader()
        for row in rows:
            writer.writerow(asdict(row))
    lines = [
        "# Pairwise conditioning versus a common FSwA target\n\n",
        "Naive output for shift `u` is uniform on `S intersection (S+u)`. "
        "These supports depend on `u`. The common-target construction instead "
        "uses the intersection of all shifted sources and has exact output "
        "distance zero between secrets.\n\n",
        "| family | n | t | #S | min pairwise A | common A | max naive TV | common TV |\n",
        "|---|---:|---:|---:|---:|---:|---:|---:|\n",
    ]
    for row in rows:
        lines.append(
            f"| {row.family} | {row.dimension} | {row.scale} | {row.source_count} | "
            f"{row.minimum_pairwise_acceptance_exact} | "
            f"{row.common_core_acceptance_exact} | "
            f"{row.maximum_naive_output_tv_exact} | 0/1 |\n"
        )
    markdown_path.write_text("".join(lines), encoding="utf-8")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dimension", type=int, default=2)
    parser.add_argument("--scale", type=int, default=8)
    parser.add_argument("--secret-l1", type=int, default=2)
    parser.add_argument(
        "--output-prefix", type=Path, default=Path("results") / "distribution_distance"
    )
    args = parser.parse_args(argv)
    rows = run_experiment(args.dimension, args.scale, args.secret_l1)
    write_outputs(rows, args.output_prefix)
    print(f"wrote {len(rows)} distribution rows under {args.output_prefix.parent}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
