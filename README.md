# Reproducibility package

Source and verification code for **Exact Coordinate-Balancing Calculus and
Sharp Stability for Symmetric Lattice Cross-Covariograms** (Shunqi Lu, School
of Artificial Intelligence, Capital University of Economics and Business).

Every theorem in the manuscript is proved by hand; the code here reproduces the
tables and figures and re-verifies the statements over explicit finite ranges.
No finite computation enters a proof.

## Contents

- `paper/focus.tex`, `paper/focus.bib`, `paper/focus.pdf`: the manuscript, its
  cited-only bibliography, and the compiled paper (59 pages).
- `paper/online_resource_crypto.tex` and `.pdf`: Online Resource 1, the
  probabilistic, QROM, and public-rank material separated from the main
  narrative (7 pages).
- `paper/makefigs.py` and `paper/figdata.py`: the generator for every main-text
  figure and the exact computations behind the numbers it draws. Text is
  typeset by pdflatex through the matplotlib pgf backend, so the figures carry
  the manuscript fonts.
- `paper/fig-*.pdf`: the figures used by the two documents.
  `paper/fig-retry-qrom.tex` and `paper/drawio/*.drawio` are the TikZ and
  editable diagrams.net sources of the Online Resource figure.
- `src/ehrhart_fswa/`: the research and certificate code.
- `tests/`: the verification suite (478 automated tests).
- `results/`: the archived tables, reports, environment metadata, and the
  SHA-256 manifest.
- `research/*.py`: standalone exact scans, including
  `structural_threshold_scan.py` for the structural theorem and
  `polytope_transfer_phase_scan.py` for the falsification scans beyond the Lee
  setting.
- `research/*.md`: proof-development records for the universal exchange-fiber
  theorem and the non-Lee sharp models, the verification matrix, and provenance
  notes for the external inputs; the finished proofs are in `paper/focus.tex`.
- `research/sources/`: the retrieved NIST potential-updates workbook and ACVP
  ML-DSA key-generation vectors used by the audits.
- `scripts/reproduce.py`, `scripts/reproduce.ps1`, `scripts/reproduce.sh`:
  reproduction entry points.

Results worth reading on their own:

- `results/quantitative_lee_rearrangement.md`: the local-chamber, weighted
  shell-graph, radial-equality, and finite-quotient boundary audit.
- `results/structural_threshold_scan.md` and `.json`: the exact regression scan
  behind the structural theorem, covering the master kernel, both cases of the
  edge law, the donor-heavy endpoint, and the sharp constant, minimizing orbit,
  and threshold sign for `3 <= d <= 39` and `2 <= b <= 6`.
- `results/polytope_transfer_phase_scan.md` and `.json`: exact scans for
  symmetric convex bodies, mixed Minkowski sums, and sharpness
  counterexamples.
- `results/minkowski_sum_phase_table.md`: exact sharp unit-transfer tables for
  the integer interpolation `alpha C_3 + beta B_inf^3` at fixed axial radius
  two.

## Verify

Install the pinned tools and run:

```text
python -m pip install -r requirements-repro.txt
python scripts/reproduce.py --quick
```

The archived manifest can be checked independently with:

```text
python -m ehrhart_fswa.certificate verify
```

## Reproduce all results and rebuild the paper

With `pdflatex`, `bibtex`, and `pdftops` on `PATH`, run:

```text
python scripts/reproduce.py --full
```

On Windows the equivalent wrapper is:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/reproduce.ps1
```

The driver stops on the first failing command, prints the wall time, and
verifies the newly generated hashes. The single timing experiment fixes seed
20260802; every theorem and table value is deterministic, so only
machine-dependent timing columns vary between runs. Exact environment metadata
are recorded in `results/performance_environment.json`.
