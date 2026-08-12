"""Exact fresh-challenge geometry for the standardized ML-DSA z-norm layer.

The powered factors are the ideal acceptances, and hence the denominators in
the paper's classical-ROM freshness bound.  The companion ``mldsa_fiber``
module supplies a public-matrix commitment-fiber certificate.  Neither module
models the rejection probability of the complete signing loop.
"""

from __future__ import annotations

import argparse
import csv
import sys
from dataclasses import asdict, dataclass
from fractions import Fraction
from pathlib import Path
from typing import Sequence


# Exact fractions below may contain more than Python's default 4,300 digits.
if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)


@dataclass(frozen=True)
class MLDSAParameters:
    name: str
    k: int
    ell: int
    tau: int
    eta: int
    beta: int
    gamma1: int
    gamma2: int
    fips_pdf_average_repetitions: float
    potential_updates_average_repetitions: float

    @property
    def response_dimension(self) -> int:
        return 256 * self.ell


PARAMETER_SETS: tuple[MLDSAParameters, ...] = (
    MLDSAParameters(
        "ML-DSA-44", 4, 4, 39, 2, 78, 2**17, (8_380_417 - 1) // 88, 4.25, 4.36
    ),
    MLDSAParameters(
        "ML-DSA-65", 6, 5, 49, 4, 196, 2**19, (8_380_417 - 1) // 32, 5.10, 5.14
    ),
    MLDSAParameters(
        "ML-DSA-87", 8, 7, 60, 2, 120, 2**19, (8_380_417 - 1) // 32, 3.85, 3.91
    ),
)


@dataclass(frozen=True)
class MLDSACaseRow:
    parameter_set: str
    response_dimension: int
    tau: int
    eta: int
    beta: int
    gamma1: int
    source_coefficient_count: int
    maximal_common_coefficient_count: int
    fips_z_coefficient_count: int
    maximal_acceptance_expression: str
    maximal_acceptance_exact: str
    maximal_acceptance: float
    maximal_reciprocal_geometric_factor: float
    fips_z_acceptance_expression: str
    fips_z_acceptance_exact: str
    fips_z_acceptance: float
    fips_z_reciprocal_geometric_factor: float
    fips_pdf_average_repetitions_all_checks: float
    potential_updates_average_repetitions_all_checks: float


def interval_common_target(
    gamma1: int, beta: int
) -> tuple[tuple[int, int], tuple[int, int]]:
    """Return maximal and FIPS symmetric targets for one coefficient.

    ``ExpandMask`` samples the integer interval ``[-gamma1+1, gamma1]``.
    Intersecting all of its shifts by integers in ``[-beta,beta]`` gives the
    maximal (asymmetric) common interval.  FIPS 204 instead checks the strict
    symmetric condition ``|z| < gamma1-beta``.
    """

    if gamma1 <= 0 or not 0 <= beta < gamma1:
        raise ValueError("require gamma1 > beta >= 0")
    maximal = (-gamma1 + 1 + beta, gamma1 - beta)
    fips = (-gamma1 + beta + 1, gamma1 - beta - 1)
    return maximal, fips


def analyze_parameter_set(parameters: MLDSAParameters) -> MLDSACaseRow:
    """Compute exact ideal fresh-challenge z-target factors."""

    if parameters.beta != parameters.tau * parameters.eta:
        raise ValueError("ML-DSA requires beta = tau * eta")
    dimension = parameters.response_dimension
    maximal, fips = interval_common_target(parameters.gamma1, parameters.beta)
    source_side = 2 * parameters.gamma1
    maximal_side = maximal[1] - maximal[0] + 1
    fips_side = fips[1] - fips[0] + 1
    maximal_acceptance = Fraction(maximal_side, source_side) ** dimension
    fips_acceptance = Fraction(fips_side, source_side) ** dimension
    return MLDSACaseRow(
        parameter_set=parameters.name,
        response_dimension=dimension,
        tau=parameters.tau,
        eta=parameters.eta,
        beta=parameters.beta,
        gamma1=parameters.gamma1,
        source_coefficient_count=source_side,
        maximal_common_coefficient_count=maximal_side,
        fips_z_coefficient_count=fips_side,
        maximal_acceptance_expression=(
            f"(({parameters.gamma1}-{parameters.beta})/{parameters.gamma1})"
            f"^{dimension}"
        ),
        maximal_acceptance_exact=(
            f"{maximal_acceptance.numerator}/{maximal_acceptance.denominator}"
        ),
        maximal_acceptance=float(maximal_acceptance),
        maximal_reciprocal_geometric_factor=float(1 / maximal_acceptance),
        fips_z_acceptance_expression=(
            f"((2*({parameters.gamma1}-{parameters.beta})-1)/"
            f"(2*{parameters.gamma1}))^{dimension}"
        ),
        fips_z_acceptance_exact=(
            f"{fips_acceptance.numerator}/{fips_acceptance.denominator}"
        ),
        fips_z_acceptance=float(fips_acceptance),
        fips_z_reciprocal_geometric_factor=float(1 / fips_acceptance),
        fips_pdf_average_repetitions_all_checks=(
            parameters.fips_pdf_average_repetitions
        ),
        potential_updates_average_repetitions_all_checks=(
            parameters.potential_updates_average_repetitions
        ),
    )


def run_cases() -> list[MLDSACaseRow]:
    return [analyze_parameter_set(parameters) for parameters in PARAMETER_SETS]


def write_csv(rows: Sequence[MLDSACaseRow], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(asdict(rows[0]).keys()))
        writer.writeheader()
        for row in rows:
            writer.writerow(asdict(row))


def write_markdown(rows: Sequence[MLDSACaseRow], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Exact fresh-challenge ML-DSA z-norm interface factors\n\n",
        "Scope: the exact powers below are the ideal z-target acceptances and "
        "the denominators that amplify the prequery-hit error in the paper's "
        "classical-ROM freshness theorem. The companion `mldsa_fiber.*` "
        "outputs certify the needed commitment min-entropy from the public "
        "matrix rank defect. These values "
        "are not complete-loop rejection probabilities; the FIPS average "
        "repetition factors use all signing checks. The full "
        "reduced fractions are in `mldsa_case.csv`.\n\n",
        "| set | d=256 ell | beta | gamma1 | maximal common factor | 1/G | "
        "FIPS symmetric-z factor | 1/G | FIPS PDF loop reps. | "
        "potential-update loop reps. |\n",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|\n",
    ]
    for row in rows:
        lines.append(
            f"| {row.parameter_set} | {row.response_dimension} | {row.beta} | "
            f"{row.gamma1} | `{row.maximal_acceptance_expression}` = "
            f"{row.maximal_acceptance:.12f} | "
            f"{row.maximal_reciprocal_geometric_factor:.6f} | "
            f"`{row.fips_z_acceptance_expression}` = "
            f"{row.fips_z_acceptance:.12f} | "
            f"{row.fips_z_reciprocal_geometric_factor:.6f} | "
            f"{row.fips_pdf_average_repetitions_all_checks:.2f} | "
            f"{row.potential_updates_average_repetitions_all_checks:.2f} |\n"
        )
    lines.extend(
        [
            "\nFor one coefficient the source interval is "
            "`[-gamma1+1, gamma1]`.  Its maximal common target over every "
            "integer offset in `[-beta,beta]` is "
            "`[-gamma1+1+beta, gamma1-beta]`, with `2(gamma1-beta)` points. "
            "The strict symmetric FIPS check uses one fewer point. The final "
            "two columns distinguish the complete-loop values printed in the 2024 FIPS 204 "
            "PDF from NIST's potential-updates spreadsheet retrieved on "
            "2026-08-02 (spreadsheet last updated 2026-07-31).\n"
        ]
    )
    path.write_text("".join(lines), encoding="utf-8")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-prefix", type=Path, default=Path("results") / "mldsa_case"
    )
    args = parser.parse_args(argv)
    rows = run_cases()
    write_csv(rows, args.output_prefix.with_suffix(".csv"))
    write_markdown(rows, args.output_prefix.with_suffix(".md"))
    print(f"wrote {len(rows)} ML-DSA rows to {args.output_prefix}.[csv|md]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
