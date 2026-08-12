"""Certify arbitrary-shift cross-polytope generating functions."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterator, Sequence, cast

from .counts import cross_polytope_overlap_count
from .generating_functions import cross_lens_generating_function


def integer_partitions_at_most(total: int, length: int) -> Iterator[tuple[int, ...]]:
    """Yield nonincreasing nonnegative partitions of size at most ``total``."""

    def recurse(
        prefix: list[int], maximum: int, remaining: int
    ) -> Iterator[tuple[int, ...]]:
        if len(prefix) == length:
            yield tuple(prefix)
            return
        for value in range(min(maximum, remaining), -1, -1):
            prefix.append(value)
            yield from recurse(prefix, value, remaining - value)
            prefix.pop()

    yield from recurse([], total, total)


def run_certification(
    dimension: int, max_shift_l1: int, checked_through: int
) -> list[dict[str, object]]:
    records = []
    for shift in integer_partitions_at_most(max_shift_l1, dimension):
        generating_function = cross_lens_generating_function(shift)
        for radius in range(checked_through + 1):
            exact = cross_polytope_overlap_count(radius, shift)
            generated = generating_function.rectangle_sum(radius)
            if exact != generated:
                raise AssertionError(
                    f"generating-function mismatch for u={shift}, t={radius}: "
                    f"{generated} != {exact}"
                )
        records.append(
            {
                "dimension": dimension,
                "shift_partition": list(shift),
                "shift_l1": sum(shift),
                "denominator": f"(1-X*Y)^{dimension}",
                "numerator_terms": [
                    list(term) for term in generating_function.numerator_terms
                ],
                "overlap_formula": generating_function.eventual_binomial_formula(),
                "checked_t_min": 0,
                "checked_t_max": checked_through,
            }
        )
    return records


def write_markdown(records: Sequence[dict[str, object]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Arbitrary-shift cross-polytope generating functions\n\n",
        "For each signed-permutation class `u`, the exact bivariate generating "
        "function is `P_u(X,Y)/(1-XY)^d`. In the formulas, `C(a,d)_+` is zero "
        "when `a < d`. Every formula was compared with the independent dynamic "
        "program on the stated scale interval.\n\n",
        "| shift partition | l1 | numerator terms | exact overlap formula |\n",
        "|---|---:|---:|---|\n",
    ]
    for record in records:
        partition = cast(list[int], record["shift_partition"])
        numerator_terms = cast(list[list[int]], record["numerator_terms"])
        lines.append(
            f"| `{tuple(partition)}` | {record['shift_l1']} | "
            f"{len(numerator_terms)} | `{record['overlap_formula']}` |\n"
        )
    path.write_text("".join(lines), encoding="utf-8")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dimension", type=int, default=4)
    parser.add_argument("--max-shift-l1", type=int, default=6)
    parser.add_argument("--checked-through", type=int, default=30)
    parser.add_argument(
        "--output-prefix", type=Path, default=Path("results") / "cross_arbitrary"
    )
    args = parser.parse_args(argv)
    records = run_certification(args.dimension, args.max_shift_l1, args.checked_through)
    json_path = args.output_prefix.with_suffix(".json")
    markdown_path = args.output_prefix.with_suffix(".md")
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(records, indent=2), encoding="utf-8")
    write_markdown(records, markdown_path)
    print(
        f"certified {len(records)} shift classes; wrote {json_path} and {markdown_path}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
