"""Run exact worst-shift baseline comparisons."""

from __future__ import annotations

import argparse
import csv
from dataclasses import asdict, dataclass
from fractions import Fraction
from math import isqrt, log2
from pathlib import Path
from time import perf_counter
from typing import Callable, Iterable, Sequence

from .counts import (
    block_hexagon_lattice_count,
    block_hexagon_overlap_count,
    cross_polytope_lattice_count,
    cross_polytope_overlap_count,
    cube_lattice_count,
    cube_overlap_count,
    hybrid_lattice_count,
    hybrid_max_l2_squared,
    hybrid_overlap_count,
)
from .shifts import integer_l1_shifts


@dataclass(frozen=True)
class ExperimentRow:
    family: str
    dimension: int
    norm_budget: int
    scale: int
    actual_max_l2_squared: int
    secret_l1_radius: int
    shift_count: int
    worst_shift: str
    lattice_point_count: int
    log2_lattice_point_count: float
    overlap_count: int
    acceptance_exact: str
    acceptance: float
    expected_trials: float
    elapsed_seconds: float


def _worst_overlap(
    overlap_counter: Callable[[int, Sequence[int]], int],
    scale: int,
    shifts: Iterable[tuple[int, ...]],
) -> tuple[int, tuple[int, ...], int]:
    worst_count: int | None = None
    worst_shift: tuple[int, ...] | None = None
    shift_count = 0
    for shift in shifts:
        shift_count += 1
        overlap = overlap_counter(scale, shift)
        if (
            worst_count is None
            or overlap < worst_count
            or (
                overlap == worst_count and shift < worst_shift  # type: ignore[operator]
            )
        ):
            worst_count = overlap
            worst_shift = shift
    if worst_count is None or worst_shift is None:
        raise ValueError("the shift set must not be empty")
    return worst_count, worst_shift, shift_count


def _make_row(
    *,
    family: str,
    dimension: int,
    norm_budget: int,
    scale: int,
    actual_max_l2_squared: int,
    secret_l1_radius: int,
    point_count: int,
    overlap_counter: Callable[[int, Sequence[int]], int],
) -> ExperimentRow:
    started = perf_counter()
    overlap, shift, shift_count = _worst_overlap(
        overlap_counter,
        scale,
        integer_l1_shifts(dimension, secret_l1_radius),
    )
    elapsed = perf_counter() - started
    acceptance = Fraction(overlap, point_count)
    return ExperimentRow(
        family=family,
        dimension=dimension,
        norm_budget=norm_budget,
        scale=scale,
        actual_max_l2_squared=actual_max_l2_squared,
        secret_l1_radius=secret_l1_radius,
        shift_count=shift_count,
        worst_shift="(" + ",".join(map(str, shift)) + ")",
        lattice_point_count=point_count,
        log2_lattice_point_count=log2(point_count),
        overlap_count=overlap,
        acceptance_exact=f"{acceptance.numerator}/{acceptance.denominator}",
        acceptance=float(acceptance),
        expected_trials=float(1 / acceptance) if acceptance else float("inf"),
        elapsed_seconds=elapsed,
    )


def run_baseline(
    dimensions: Sequence[int], budgets: Sequence[int], secret_l1_radius: int
) -> list[ExperimentRow]:
    """Compare exact worst-shift overlaps under a common Euclidean budget."""

    rows: list[ExperimentRow] = []
    for dimension in dimensions:
        if dimension < 1:
            raise ValueError("dimensions must be positive")
        for budget in budgets:
            if budget < 1:
                raise ValueError("norm budgets must be positive")

            product_scale = isqrt((budget * budget) // dimension)
            rows.append(
                _make_row(
                    family="cube",
                    dimension=dimension,
                    norm_budget=budget,
                    scale=product_scale,
                    actual_max_l2_squared=dimension * product_scale * product_scale,
                    secret_l1_radius=secret_l1_radius,
                    point_count=cube_lattice_count(product_scale, dimension),
                    overlap_counter=cube_overlap_count,
                )
            )

            rows.append(
                _make_row(
                    family="cross_polytope",
                    dimension=dimension,
                    norm_budget=budget,
                    scale=budget,
                    actual_max_l2_squared=budget * budget,
                    secret_l1_radius=secret_l1_radius,
                    point_count=cross_polytope_lattice_count(budget, dimension),
                    overlap_counter=cross_polytope_overlap_count,
                )
            )

            hybrid_scale = 0
            while hybrid_max_l2_squared(hybrid_scale + 1, dimension) <= budget * budget:
                hybrid_scale += 1
            rows.append(
                _make_row(
                    family="hybrid_H",
                    dimension=dimension,
                    norm_budget=budget,
                    scale=hybrid_scale,
                    actual_max_l2_squared=hybrid_max_l2_squared(
                        hybrid_scale, dimension
                    ),
                    secret_l1_radius=secret_l1_radius,
                    point_count=hybrid_lattice_count(hybrid_scale, dimension),
                    overlap_counter=hybrid_overlap_count,
                )
            )

            if dimension % 2 == 0:
                rows.append(
                    _make_row(
                        family="hexagon_blocks",
                        dimension=dimension,
                        norm_budget=budget,
                        scale=product_scale,
                        actual_max_l2_squared=dimension * product_scale * product_scale,
                        secret_l1_radius=secret_l1_radius,
                        point_count=block_hexagon_lattice_count(
                            product_scale, dimension
                        ),
                        overlap_counter=block_hexagon_overlap_count,
                    )
                )
    return rows


def write_csv(rows: Sequence[ExperimentRow], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(asdict(rows[0]).keys()))
        writer.writeheader()
        for row in rows:
            writer.writerow(asdict(row))


def write_markdown(rows: Sequence[ExperimentRow], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    header = (
        "| family | n | R | t | max ||z||_2^2 | #S | worst u | "
        "acceptance (exact) | acceptance | E[trials] |\n"
    )
    divider = "|---|---:|---:|---:|---:|---:|---|---:|---:|---:|\n"
    lines = [
        "# Exact finite-dimensional baseline\n\n",
        "Worst case over all integer shifts with the configured `l1` radius. "
        "Families are compared under the same Euclidean norm budget `R`; "
        "the reported actual squared maximum records integer rounding.\n\n",
        header,
        divider,
    ]
    for row in rows:
        lines.append(
            f"| {row.family} | {row.dimension} | {row.norm_budget} | {row.scale} | "
            f"{row.actual_max_l2_squared} | {row.lattice_point_count} | "
            f"`{row.worst_shift}` | {row.acceptance_exact} | "
            f"{row.acceptance:.8f} | {row.expected_trials:.6f} |\n"
        )
    path.write_text("".join(lines), encoding="utf-8")


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dimensions", nargs="+", type=int, default=[2, 4, 8])
    parser.add_argument("--budgets", nargs="+", type=int, default=[8, 12, 16])
    parser.add_argument("--secret-l1", type=int, default=2)
    parser.add_argument(
        "--output-prefix", type=Path, default=Path("results") / "baseline"
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    rows = run_baseline(args.dimensions, args.budgets, args.secret_l1)
    csv_path = args.output_prefix.with_suffix(".csv")
    markdown_path = args.output_prefix.with_suffix(".md")
    write_csv(rows, csv_path)
    write_markdown(rows, markdown_path)
    print(f"wrote {len(rows)} exact rows to {csv_path} and {markdown_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
