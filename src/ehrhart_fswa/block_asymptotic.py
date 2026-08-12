"""Exact data for the fixed-block exponential-loss theorem."""

from __future__ import annotations

import argparse
import csv
import sys
from dataclasses import asdict, dataclass
from fractions import Fraction
from math import comb, exp, log
from pathlib import Path
from typing import Literal, Sequence

from .counts import (
    cross_polytope_lattice_count,
    cube_lattice_count,
    hexagon_lattice_count,
)

if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)

BlockFamily = Literal["cube", "cross", "hexagon"]


def base_count(family: BlockFamily, block_dimension: int, scale: int) -> int:
    if scale < 0:
        return 0
    if family == "cube":
        return cube_lattice_count(scale, block_dimension)
    if family == "cross":
        return cross_polytope_lattice_count(scale, block_dimension)
    if family == "hexagon":
        if block_dimension != 2:
            raise ValueError("hexagon blocks have dimension two")
        return hexagon_lattice_count(scale)
    raise ValueError(f"unknown family {family}")


def fixed_block_acceptance(
    family: BlockFamily, block_dimension: int, blocks: int, scale: int, erosion: int
) -> Fraction:
    """Return ``(L(scale-erosion)/L(scale))**blocks`` exactly."""

    if blocks < 1 or erosion < 0:
        raise ValueError("blocks must be positive and erosion nonnegative")
    denominator = base_count(family, block_dimension, scale)
    numerator = base_count(family, block_dimension, scale - erosion)
    return Fraction(numerator, denominator) ** blocks


def hstar_acceptance_bounds(
    block_dimension: int, blocks: int, scale: int, erosion: int
) -> tuple[Fraction, Fraction]:
    """Return the universal finite bounds from the Ehrhart h-star expansion."""

    if block_dimension < 1 or blocks < 1 or erosion < 0:
        raise ValueError("dimensions and blocks must be positive, erosion nonnegative")
    if scale < erosion + block_dimension:
        raise ValueError("h-star bounds require scale >= erosion + block_dimension")
    lower_one_block = Fraction(
        comb(scale - erosion, block_dimension), comb(scale, block_dimension)
    )
    upper_one_block = Fraction(
        comb(scale - erosion + block_dimension, block_dimension),
        comb(scale + block_dimension, block_dimension),
    )
    return lower_one_block**blocks, upper_one_block**blocks


def hstar_vector_from_ehrhart_values(values: Sequence[int]) -> tuple[int, ...]:
    """Recover ``h*`` from ``L(0), ..., L(b)`` in the binomial basis."""

    if not values or any(value < 0 for value in values):
        raise ValueError("nonnegative Ehrhart values are required")
    dimension = len(values) - 1
    hstar: list[int] = []
    for scale, value in enumerate(values):
        explained = sum(
            coefficient * comb(scale + dimension - index, dimension)
            for index, coefficient in enumerate(hstar)
        )
        hstar.append(value - explained)
    return tuple(hstar)


def hstar_erosion_ratio(hstar: Sequence[int], scale: int, erosion: int) -> Fraction:
    """Evaluate the exact h-star barycentric erosion identity."""

    if not hstar or any(value < 0 for value in hstar):
        raise ValueError("a nonnegative h-star vector is required")
    dimension = len(hstar) - 1
    if scale < erosion + dimension or erosion < 0:
        raise ValueError("requires scale >= erosion + dimension")
    denominator = sum(
        value * comb(scale + dimension - index, dimension)
        for index, value in enumerate(hstar)
    )
    numerator = sum(
        value * comb(scale - erosion + dimension - index, dimension)
        for index, value in enumerate(hstar)
    )
    return Fraction(numerator, denominator)


def hstar_degree_bounds(
    hstar: Sequence[int], scale: int, erosion: int
) -> tuple[Fraction, Fraction]:
    """Return the degree-sensitive one-block bounds for an h-star vector."""

    if not hstar or any(value < 0 for value in hstar) or not any(hstar):
        raise ValueError("a nonzero nonnegative h-star vector is required")
    dimension = len(hstar) - 1
    if erosion < 0 or scale < erosion + dimension:
        raise ValueError("requires scale >= erosion + dimension")
    degree = max(index for index, value in enumerate(hstar) if value)
    lower = Fraction(
        comb(scale - erosion + dimension - degree, dimension),
        comb(scale + dimension - degree, dimension),
    )
    upper = Fraction(
        comb(scale - erosion + dimension, dimension),
        comb(scale + dimension, dimension),
    )
    return lower, upper


def hstar_mean(hstar: Sequence[int]) -> Fraction:
    """Return the mean of the normalized h-star coefficient distribution."""

    if not hstar or any(value < 0 for value in hstar) or not any(hstar):
        raise ValueError("a nonzero nonnegative h-star vector is required")
    total = sum(hstar)
    return Fraction(sum(index * value for index, value in enumerate(hstar)), total)


def hstar_mlr_dominates(left: Sequence[int], right: Sequence[int]) -> bool:
    """Return whether ``left`` dominates ``right`` in h-star likelihood ratio.

    The orientation matches the paper: more mass at larger indices means a
    no-larger finite erosion ratio at every admissible scale and erosion.
    Cross products avoid division and handle zero coefficients exactly.
    """

    if not left or len(left) != len(right):
        raise ValueError("h-star vectors must have the same positive length")
    if any(value < 0 for value in (*left, *right)):
        raise ValueError("h-star coefficients must be nonnegative")
    if not any(left) or not any(right):
        raise ValueError("h-star vectors must have positive total mass")
    return all(
        left[i] * right[j] <= left[j] * right[i]
        for i in range(len(left))
        for j in range(i + 1, len(left))
    )


@dataclass(frozen=True)
class BlockRow:
    family: str
    block_dimension: int
    ambient_dimension: int
    blocks: int
    erosion: int
    regime: str
    scale: int
    one_block_ratio: str
    acceptance_expression: str
    acceptance_exact: str
    acceptance: float
    negative_log_acceptance: float
    theorem_limit: float | None


def run_table() -> list[BlockRow]:
    rows = []
    families: tuple[tuple[BlockFamily, int], ...] = (("cross", 4), ("hexagon", 2))
    for family, block_dimension in families:
        for ambient_dimension in (16, 32, 64, 128, 256):
            if ambient_dimension % block_dimension:
                continue
            blocks = ambient_dimension // block_dimension
            for regime, scale in (
                ("fixed t=32", 32),
                ("linear t=n", ambient_dimension),
            ):
                numerator = base_count(family, block_dimension, scale - 2)
                denominator = base_count(family, block_dimension, scale)
                acceptance = Fraction(numerator, denominator) ** blocks
                rows.append(
                    BlockRow(
                        family,
                        block_dimension,
                        ambient_dimension,
                        blocks,
                        2,
                        regime,
                        scale,
                        f"{numerator}/{denominator}",
                        f"({numerator}/{denominator})^{blocks}",
                        f"{acceptance.numerator}/{acceptance.denominator}",
                        float(acceptance),
                        -log(float(acceptance)),
                        None if regime.startswith("fixed") else exp(-2),
                    )
                )
    return rows


def write_outputs(rows: Sequence[BlockRow], prefix: Path) -> None:
    prefix.parent.mkdir(parents=True, exist_ok=True)
    with prefix.with_suffix(".csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(asdict(rows[0]).keys()))
        writer.writeheader()
        for row in rows:
            writer.writerow(asdict(row))
    lines = [
        "# Fixed-block exponential-loss data\n\n",
        "Every value is an exact power of a one-block Ehrhart ratio; literal "
        "reduced fractions are in the CSV. For the linear regime `t=n` and "
        "erosion `s=2`, the theorem predicts the family-independent limit "
        "`exp(-2)=0.135335283237...`.\n\n",
        "| family | b | n | regime | t | exact expression | A |\n",
        "|---|---:|---:|---|---:|---|---:|\n",
    ]
    for row in rows:
        lines.append(
            f"| {row.family} | {row.block_dimension} | {row.ambient_dimension} | "
            f"{row.regime} | {row.scale} | `{row.acceptance_expression}` | "
            f"{row.acceptance:.12f} |\n"
        )
    prefix.with_suffix(".md").write_text("".join(lines), encoding="utf-8")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-prefix", type=Path, default=Path("results") / "block_asymptotic"
    )
    args = parser.parse_args(argv)
    rows = run_table()
    write_outputs(rows, args.output_prefix)
    print(f"wrote {len(rows)} fixed-block rows to {args.output_prefix}.[csv|md]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
