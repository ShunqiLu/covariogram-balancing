"""Sharp transfer-edge tables for K_{alpha,beta}=alpha C_3+beta B_infinity^3.

The output is an exact integer table on every fully active L1 shell in
dimension three.  It is intentionally separate from the manuscript so that
candidate phase statements can be checked before being promoted to the paper.
"""

from __future__ import annotations

from pathlib import Path

from polytope_transfer_phase_scan import (
    cross_covariogram,
    l1_plus_linf,
    transfer_edges,
)


def sharp_row(a: int, b: int, shell: int) -> tuple[int, list[tuple[tuple[int, ...], tuple[int, ...]]]]:
    body = l1_plus_linf(3, a, b)
    weighted = []
    for source, target in transfer_edges(shell, 3):
        old = cross_covariogram(body.points, body.points, source)
        new = cross_covariogram(body.points, body.points, target)
        weighted.append((new - old, source, target))
    sharp = min(weight for weight, _, _ in weighted)
    minimizers = [(source, target) for weight, source, target in weighted if weight == sharp]
    return sharp, minimizers


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    destination = root / "results" / "minkowski_sum_phase_table.md"
    lines = [
        "# Sharp balancing edges for $K_{\\alpha,\\beta}=\\alpha C_3+\\beta B_\\infty^3$ in $\\mathbb Z^3$\n",
        "For each parameter pair, shells $2\\le s\\le2(a+b)$ are fully active.  "
        "Every entry below comes from all exact Robin Hood edges on that shell.\n",
        "| $(\\alpha,\\beta)$ | $s$ | $\\kappa_{\\alpha,\\beta}(s)$ | all minimizing edge orbits |",
        "|---:|---:|---:|:---|",
    ]
    for a in range(0, 4):
        for b in range(0, 4):
            if a + b == 0:
                continue
            for shell in range(2, 2 * (a + b) + 1):
                sharp, minimizers = sharp_row(a, b, shell)
                edge_text = "; ".join(f"`${source}\\to{target}`" for source, target in minimizers)
                lines.append(f"| $({a},{b})$ | {shell} | {sharp} | {edge_text} |")

    # Independent finite regression of the proved outer-shell formula for the
    # first mixed family.  The proof is in polytope_extension_theory.md; these
    # assertions protect the implementation and table transcription only.
    for b in range(1, 9):
        shell = 2 * (b + 1)
        sharp, minimizers = sharp_row(1, b, shell)
        expected = (
            tuple(sorted((2 * b - 2, 3, 1), reverse=True)),
            tuple(sorted((2 * b - 2, 2, 2), reverse=True)),
        )
        assert sharp == 5
        assert minimizers == [expected]

    lines.extend(
        [
            "\n## Complete edge table for the first nontrivial mixed body $K_{1,1}$\n",
            "The lattice body is the disjoint-state union of the central cube "
            "$[-1,1]^3$ and six $3\\times3$ cap layers, and contains 81 points.\n",
            "| shell | edge | old overlap | new overlap | increment |",
            "|---:|:---|---:|---:|---:|",
        ]
    )
    body = l1_plus_linf(3, 1, 1)
    for shell in range(2, 5):
        for source, target in transfer_edges(shell, 3):
            old = cross_covariogram(body.points, body.points, source)
            new = cross_covariogram(body.points, body.points, target)
            lines.append(f"| {shell} | `${source}\\to{target}` | {old} | {new} | {new-old} |")

    destination.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {destination}")


if __name__ == "__main__":
    main()
