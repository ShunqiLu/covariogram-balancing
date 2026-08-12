"""Probe fixed-shift Ehrhart structure using exact finite differences."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Sequence

from .counts import (
    cross_polytope_overlap_count,
    cube_overlap_count,
    hexagon_overlap_count,
    hybrid_lattice_count,
)
from .polytope import rational_half_square, rational_octagon
from .quasipolynomial import (
    QuasiPolynomialCandidate,
    constituent_formula,
    discover_from_counter,
)


@dataclass(frozen=True)
class Study:
    name: str
    family: str
    dimension: int
    shift: tuple[int, ...]
    counter: Callable[[int], int]


def evidence_status(study: Study) -> str:
    """Separate theorem-backed rows from finite interpolation evidence."""

    if study.family in {"cube", "cross_polytope", "hexagon"}:
        return "proved by formula/theorem"
    if study.family == "hybrid_H" and study.dimension == 4:
        return "proved integral Ehrhart case"
    if study.family == "hybrid_H_irrational":
        return "finite fit only; global quasi-polynomial is disproved"
    return "finite fit and holdout checks only"


def default_studies() -> list[Study]:
    half_square = rational_half_square()
    octagon = rational_octagon()
    return [
        Study("cube_n4_axis2", "cube", 4, (2, 0, 0, 0),
              lambda t: cube_overlap_count(t, (2, 0, 0, 0))),
        Study("cube_n4_split11", "cube", 4, (1, 1, 0, 0),
              lambda t: cube_overlap_count(t, (1, 1, 0, 0))),
        Study("cross_n2_axis2", "cross_polytope", 2, (2, 0),
              lambda t: cross_polytope_overlap_count(t, (2, 0))),
        Study("cross_n2_split11", "cross_polytope", 2, (1, 1),
              lambda t: cross_polytope_overlap_count(t, (1, 1))),
        Study("cross_n4_axis2", "cross_polytope", 4, (2, 0, 0, 0),
              lambda t: cross_polytope_overlap_count(t, (2, 0, 0, 0))),
        Study("cross_n4_split11", "cross_polytope", 4, (1, 1, 0, 0),
              lambda t: cross_polytope_overlap_count(t, (1, 1, 0, 0))),
        Study("hex_n2_axis2", "hexagon", 2, (2, 0),
              lambda t: hexagon_overlap_count(t, (2, 0))),
        Study("hex_n2_diagonal11", "hexagon", 2, (1, 1),
              lambda t: hexagon_overlap_count(t, (1, 1))),
        Study("hex_n2_root11", "hexagon", 2, (1, -1),
              lambda t: hexagon_overlap_count(t, (1, -1))),
        Study("rational_half_square_axis1", "rational_half_square", 2, (1, 0),
              lambda t: half_square.overlap_count(t, (1, 0))),
        Study("rational_octagon_axis1", "rational_octagon", 2, (1, 0),
              lambda t: octagon.overlap_count(t, (1, 0))),
        Study("hybrid_H_n4_count", "hybrid_H", 4, (0, 0, 0, 0),
              lambda t: hybrid_lattice_count(t, 4)),
        Study("hybrid_H_n2_irrational_count", "hybrid_H_irrational", 2,
              (0, 0), lambda t: hybrid_lattice_count(t, 2)),
    ]


def run_studies(
    studies: Sequence[Study], checked_through: int
) -> list[tuple[Study, QuasiPolynomialCandidate | None]]:
    results = []
    for study in studies:
        candidate, _ = discover_from_counter(
            study.counter, degree=study.dimension, checked_through=checked_through
        )
        results.append((study, candidate))
    return results


def write_report(
    results: Sequence[tuple[Study, QuasiPolynomialCandidate | None]], path: Path
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Fixed-shift Ehrhart structure probe\n\n",
        "Each candidate is determined from exact counts and checked on every "
        "integer scale in the stated interval. This is a finite computational "
        "check, not by itself a proof for all scales. The evidence column states "
        "whether a separate proof is supplied in the manuscript. `C(k,j)` "
        "denotes a binomial coefficient.\n\n",
        "| study | family | n | u | degree | period | onset | checked through | evidence |\n",
        "|---|---|---:|---|---:|---:|---:|---:|---|\n",
    ]
    for study, candidate in results:
        if candidate is None:
            lines.append(
                f"| {study.name} | {study.family} | {study.dimension} | "
                f"`{study.shift}` | -- | -- | -- | -- | {evidence_status(study)} |\n"
            )
        else:
            lines.append(
                f"| {study.name} | {study.family} | {study.dimension} | "
                f"`{study.shift}` | {candidate.degree} | {candidate.period} | "
                f"{candidate.onset} | {candidate.checked_through} | "
                f"{evidence_status(study)} |\n"
            )
    lines.append("\n## Exact Newton-basis candidates\n\n")
    for study, candidate in results:
        lines.append(f"### {study.name}\n\n")
        if candidate is None:
            lines.append("No candidate was found within the search bounds.\n\n")
            continue
        for constituent in candidate.constituents:
            condition = (
                "all residues" if candidate.period == 1
                else f"t mod {candidate.period} = {constituent.residue}"
            )
            lines.append(
                f"- `{condition}`: `N(t) = "
                f"{constituent_formula(constituent, candidate.period)}`\n"
            )
        lines.append("\n")
    path.write_text("".join(lines), encoding="utf-8")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checked-through", type=int, default=40)
    parser.add_argument(
        "--output", type=Path, default=Path("results") / "quasipolynomials.md"
    )
    args = parser.parse_args(argv)
    results = run_studies(default_studies(), args.checked_through)
    write_report(results, args.output)
    found = sum(candidate is not None for _, candidate in results)
    print(f"found {found}/{len(results)} candidates; wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
