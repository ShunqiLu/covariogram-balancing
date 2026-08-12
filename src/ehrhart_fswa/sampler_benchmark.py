"""Benchmark exact reference samplers on one CPU."""

from __future__ import annotations

import argparse
import csv
from dataclasses import asdict, dataclass
from math import log2
from pathlib import Path
from random import Random
from statistics import mean, median
from time import perf_counter_ns
from typing import Callable, Sequence

from .counts import (
    cross_polytope_lattice_count,
    cube_lattice_count,
    hybrid_l1_radius,
    hybrid_lattice_count,
)
from .samplers import sample_truncated_l1


@dataclass(frozen=True)
class SamplerRow:
    family: str
    dimension: int
    scale: int
    lattice_point_count: int
    entropy_bits: float
    samples: int
    mean_microseconds: float
    median_microseconds: float
    p95_microseconds: float
    constant_time_claim: bool


def _percentile(values: list[float], fraction: float) -> float:
    ordered = sorted(values)
    return ordered[min(int(fraction * len(ordered)), len(ordered) - 1)]


def _benchmark(
    family: str,
    dimension: int,
    scale: int,
    point_count: int,
    sampler: Callable[[], tuple[int, ...]],
    samples: int,
) -> SamplerRow:
    timings = []
    for _ in range(samples):
        started = perf_counter_ns()
        point = sampler()
        elapsed = perf_counter_ns() - started
        if len(point) != dimension:
            raise AssertionError("sampler returned the wrong dimension")
        timings.append(elapsed / 1_000)
    return SamplerRow(
        family=family,
        dimension=dimension,
        scale=scale,
        lattice_point_count=point_count,
        entropy_bits=log2(point_count),
        samples=samples,
        mean_microseconds=mean(timings),
        median_microseconds=median(timings),
        p95_microseconds=_percentile(timings, 0.95),
        constant_time_claim=False,
    )


def run_benchmark(
    dimensions: Sequence[int], scale: int, samples: int, seed: int
) -> list[SamplerRow]:
    rng = Random(seed)
    rows = []
    for dimension in dimensions:

        def sample_cube(dimension: int = dimension) -> tuple[int, ...]:
            return tuple(rng.randint(-scale, scale) for _ in range(dimension))

        cube_count = cube_lattice_count(scale, dimension)
        rows.append(
            _benchmark(
                "cube",
                dimension,
                scale,
                cube_count,
                sample_cube,
                samples,
            )
        )

        cross_count = cross_polytope_lattice_count(scale, dimension)

        def sample_cross(dimension: int = dimension) -> tuple[int, ...]:
            return sample_truncated_l1(rng, scale, dimension, scale)

        rows.append(
            _benchmark(
                "cross_polytope_rank",
                dimension,
                scale,
                cross_count,
                sample_cross,
                samples,
            )
        )

        hybrid_l1 = hybrid_l1_radius(scale, dimension)
        hybrid_count = hybrid_lattice_count(scale, dimension)

        def sample_hybrid(
            dimension: int = dimension, hybrid_l1: int = hybrid_l1
        ) -> tuple[int, ...]:
            return sample_truncated_l1(rng, scale, dimension, hybrid_l1)

        rows.append(
            _benchmark(
                "hybrid_H_rank",
                dimension,
                scale,
                hybrid_count,
                sample_hybrid,
                samples,
            )
        )
    return rows


def write_outputs(rows: Sequence[SamplerRow], prefix: Path) -> None:
    csv_path = prefix.with_suffix(".csv")
    markdown_path = prefix.with_suffix(".md")
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(asdict(rows[0]).keys()))
        writer.writeheader()
        for row in rows:
            writer.writerow(asdict(row))
    lines = [
        "# Exact reference sampler benchmark\n\n",
        "These are reproducible Python reference timings, not constant-time "
        "implementation claims. Rank samplers are exactly uniform by a "
        "count/unrank bijection.\n\n",
        "| family | n | t | #points | entropy bits | median us | p95 us | CT claim |\n",
        "|---|---:|---:|---:|---:|---:|---:|---|\n",
    ]
    for row in rows:
        lines.append(
            f"| {row.family} | {row.dimension} | {row.scale} | "
            f"{row.lattice_point_count} | {row.entropy_bits:.3f} | "
            f"{row.median_microseconds:.3f} | {row.p95_microseconds:.3f} | no |\n"
        )
    markdown_path.write_text("".join(lines), encoding="utf-8")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dimensions", nargs="+", type=int, default=[4, 8, 16])
    parser.add_argument("--scale", type=int, default=16)
    parser.add_argument("--samples", type=int, default=500)
    parser.add_argument("--seed", type=int, default=20260802)
    parser.add_argument(
        "--output-prefix", type=Path, default=Path("results") / "sampler_benchmark"
    )
    args = parser.parse_args(argv)
    rows = run_benchmark(args.dimensions, args.scale, args.samples, args.seed)
    write_outputs(rows, args.output_prefix)
    print(f"wrote {len(rows)} sampler rows under {args.output_prefix.parent}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
