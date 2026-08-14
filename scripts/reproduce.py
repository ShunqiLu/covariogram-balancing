"""Reproduce the manuscript package and all archived result tables."""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from time import perf_counter


ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "paper"


def run(command: list[str], *, cwd: Path = ROOT, env: dict[str, str]) -> None:
    print(f"[{cwd}] {' '.join(command)}", flush=True)
    subprocess.run(command, cwd=cwd, env=env, check=True)


def module(name: str, *args: str) -> list[str]:
    return [sys.executable, "-m", name, *args]


def quick(env: dict[str, str]) -> None:
    run(module("pytest", "-q", "-p", "no:cacheprovider"), env=env)


def restore_article_locators(document: str) -> None:
    """Put back the letters of an article number that the bst discards.

    ``do.pages`` in ``sn-mathphys-num.bst`` keeps only the digits of a page
    field, so an electronic locator such as ``e70583`` is typeset as
    ``70583``.  Each such field is matched against the bibliography by its
    digits and restored.
    """
    bbl = PAPER / f"{document}.bbl"
    if not bbl.exists():
        return
    text = original = bbl.read_text(encoding="utf-8")
    for database in sorted(PAPER.glob("*.bib")):
        source = database.read_text(encoding="utf-8")
        for locator in re.findall(r"pages\s*=\s*\{([A-Za-z]+\d+)\}", source):
            digits = locator.lstrip("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")
            text = text.replace(f"\\bfpage{{{digits}}}", f"\\bfpage{{{locator}}}")
    if text != original:
        bbl.write_text(text, encoding="utf-8")


def latex(document: str, env: dict[str, str]) -> None:
    """Compile one document and fail if its bibliography did not resolve.

    Fed an auxiliary file without ``\\bibdata``, bibtex writes an empty
    bibliography and still exits successfully, so the citations are checked
    against the final log rather than against exit codes alone.
    """
    def pdflatex() -> None:
        run(
            ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", f"{document}.tex"],
            cwd=PAPER,
            env=env,
        )

    aux = PAPER / f"{document}.aux"
    pdflatex()
    if r"\bibdata" not in aux.read_text(encoding="utf-8", errors="ignore"):
        pdflatex()
    run(["bibtex", document], cwd=PAPER, env=env)
    restore_article_locators(document)
    pdflatex()
    pdflatex()
    log = (PAPER / f"{document}.log").read_text(encoding="utf-8", errors="ignore")
    unresolved = re.findall(r"Citation `([^']+)' on page \d+ undefined", log)
    if unresolved:
        raise RuntimeError(
            f"{document}.tex has {len(unresolved)} undefined citations, "
            f"beginning with {unresolved[0]!r}"
        )


def full(env: dict[str, str]) -> None:
    quick(env)
    commands = [
        module(
            "ehrhart_fswa.experiment",
            "--dimensions", "2", "4", "8",
            "--budgets", "8", "12", "16",
            "--secret-l1", "2",
        ),
        module("ehrhart_fswa.structure_experiment", "--checked-through", "80"),
        module("ehrhart_fswa.quantitative_rearrangement_experiment"),
        module(
            "ehrhart_fswa.generating_function_experiment",
            "--dimension", "4", "--max-shift-l1", "6",
            "--checked-through", "40",
        ),
        module(
            "ehrhart_fswa.parameter_experiment",
            "--dimensions", "8", "16", "32", "--secret-l1", "2",
        ),
        module(
            "ehrhart_fswa.sensitivity_experiment",
            "--dimensions", "8", "16", "32", "--secret-l1", "2",
        ),
        module(
            "ehrhart_fswa.distribution_experiment",
            "--dimension", "2", "--scale", "8", "--secret-l1", "2",
        ),
        module(
            "ehrhart_fswa.sampler_benchmark",
            "--dimensions", "4", "8", "16", "--scale", "16",
            "--samples", "500", "--seed", "20260802",
        ),
        module("ehrhart_fswa.mldsa_case"),
        module("ehrhart_fswa.mldsa_fiber"),
        module("ehrhart_fswa.mldsa_acvp_audit"),
        module("ehrhart_fswa.block_asymptotic"),
        module("ehrhart_fswa.performance_experiment"),
    ]
    for command in commands:
        run(command, env=env)

    # These exact scans served as falsification and discovery tools.  The
    # manuscript's polytope theorems are proved independently; rerunning the
    # scans protects their formulas and archived tables against regression.
    run([sys.executable, str(ROOT / "research" / "polytope_transfer_phase_scan.py")], env=env)
    run([sys.executable, str(ROOT / "research" / "minkowski_sum_phase_table.py")], env=env)
    run([sys.executable, str(ROOT / "research" / "structural_threshold_scan.py")], env=env)

    for executable in ("pdflatex", "bibtex", "pdftops"):
        if shutil.which(executable) is None:
            raise RuntimeError(f"full mode requires {executable} on PATH")
    # The main-text figures are vector PDFs whose text is typeset by pdflatex
    # through the matplotlib pgf backend, so they must precede the documents.
    run([sys.executable, "makefigs.py"], cwd=PAPER, env=env)
    for figure in sorted(PAPER.glob("fig-*.tex")):
        run(
            ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", figure.name],
            cwd=PAPER,
            env=env,
        )
    for document in ("covariogram-balancing", "online_resource_crypto"):
        latex(document, env)
    delivery = PAPER / "submission_figures"
    # Keys are in the order the figures are declared in the manuscript, which is
    # the order LaTeX numbers them.
    main_figures = [
        "fig-architecture",
        "fig-exchange-fiber",
        "fig-atomic-exposure",
        "fig-transfer",
        "fig-square-map",
        "fig-parity-rectangle",
        "fig-middle-section",
        "fig-shell-graph",
        "fig-case-partition",
        "fig-rigidity",
        "fig-sharp-constants",
        "fig-threshold",
    ]
    figure_exports = {
        f"{stem}.pdf": f"Fig{index}.eps"
        for index, stem in enumerate(main_figures, start=1)
    }
    figure_exports["fig-retry-qrom.pdf"] = "OnlineResource1_Fig1.eps"
    for source, destination in figure_exports.items():
        run(
            ["pdftops", "-eps", source, str(delivery / destination)],
            cwd=PAPER,
            env=env,
        )
    run(module("ehrhart_fswa.certificate", "create"), env=env)
    run(module("ehrhart_fswa.certificate", "verify"), env=env)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--quick", action="store_true")
    modes.add_argument("--full", action="store_true")
    args = parser.parse_args()
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONPATH"] = str(ROOT / "src") + os.pathsep + env.get("PYTHONPATH", "")
    start = perf_counter()
    if args.quick:
        quick(env)
    else:
        full(env)
    print(f"reproduction completed in {perf_counter() - start:.3f} seconds")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
