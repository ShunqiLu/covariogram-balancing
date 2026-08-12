"""Audit public NTT rank defects for official NIST ACVP ML-DSA keys."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Sequence

from ehrhart_fswa.mldsa_case import PARAMETER_SETS, MLDSAParameters
from ehrhart_fswa.mldsa_fiber import Q, ntt_rank_defect


N = 256
ACVP_PROMPT_SHA256 = "43e81ad820e495dbcad086fe27c1008393a8c32100bbbff77c558c3f06dcefef"
ACVP_EXPECTED_SHA256 = "361f47ca19d592adcc66ff2cb591686ad785fea157b295648738bed6921a68df"
CLASSICAL_DEFECT_BUDGETS = {"ML-DSA-44": 51, "ML-DSA-65": 272, "ML-DSA-87": 400}
QROM_DEFECT_BUDGETS = {"ML-DSA-44": 27, "ML-DSA-65": 240, "ML-DSA-87": 368}


def sha256_file(path: Path) -> str:
    """Return a lowercase SHA-256 digest for one file."""

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def rej_ntt_poly(seed: bytes) -> tuple[int, ...]:
    """FIPS 204 RejNTTPoly using SHAKE128 and three-byte coefficients."""

    output_length = 840
    consumed = 0
    coefficients: list[int] = []
    while len(coefficients) < N:
        stream = hashlib.shake_128(seed).digest(output_length)
        while consumed + 3 <= len(stream) and len(coefficients) < N:
            first, second, third = stream[consumed : consumed + 3]
            value = first | (second << 8) | ((third & 0x7F) << 16)
            if value < Q:
                coefficients.append(value)
            consumed += 3
        output_length += 168
    return tuple(coefficients)


def expand_a_ntt_lanes(
    rho: bytes, parameters: MLDSAParameters
) -> tuple[tuple[tuple[int, ...], ...], ...]:
    """Return the 256 rectangular NTT lanes of FIPS 204 ExpandA."""

    if len(rho) != 32:
        raise ValueError("rho must contain 32 bytes")
    entries = [
        [rej_ntt_poly(rho + bytes((column, row))) for column in range(parameters.ell)]
        for row in range(parameters.k)
    ]
    return tuple(
        tuple(
            tuple(entries[row][column][lane] for column in range(parameters.ell))
            for row in range(parameters.k)
        )
        for lane in range(N)
    )


@dataclass(frozen=True)
class ACVPAuditRow:
    parameter_set: str
    test_case_id: int
    rho_sha256: str
    rank_defect: int
    classical_defect_budget: int
    passes_classical_budget: bool
    qrom_defect_budget: int
    passes_qrom_budget: bool


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError("ACVP file must contain a JSON object")
    return value


def audit_acvp_keys(prompt_path: Path, expected_path: Path) -> list[ACVPAuditRow]:
    """Compute the public rank certificate for every official keyGen vector."""

    if sha256_file(prompt_path) != ACVP_PROMPT_SHA256:
        raise ValueError("unexpected ACVP prompt SHA-256")
    if sha256_file(expected_path) != ACVP_EXPECTED_SHA256:
        raise ValueError("unexpected ACVP expected-results SHA-256")
    prompt = _load_json(prompt_path)
    expected = _load_json(expected_path)
    parameters_by_name = {parameters.name: parameters for parameters in PARAMETER_SETS}
    names_by_group = {
        int(group["tgId"]): str(group["parameterSet"])
        for group in prompt["testGroups"]
    }
    rows: list[ACVPAuditRow] = []
    for group in expected["testGroups"]:
        name = names_by_group[int(group["tgId"])]
        parameters = parameters_by_name[name]
        for test in group["tests"]:
            public_key = bytes.fromhex(str(test["pk"]))
            rho = public_key[:32]
            lanes = expand_a_ntt_lanes(rho, parameters)
            defect = ntt_rank_defect(lanes)
            rows.append(
                ACVPAuditRow(
                    parameter_set=name,
                    test_case_id=int(test["tcId"]),
                    rho_sha256=hashlib.sha256(rho).hexdigest(),
                    rank_defect=defect,
                    classical_defect_budget=CLASSICAL_DEFECT_BUDGETS[name],
                    passes_classical_budget=defect <= CLASSICAL_DEFECT_BUDGETS[name],
                    qrom_defect_budget=QROM_DEFECT_BUDGETS[name],
                    passes_qrom_budget=defect <= QROM_DEFECT_BUDGETS[name],
                )
            )
    return rows


def write_csv(rows: Sequence[ACVPAuditRow], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(asdict(rows[0]).keys()))
        writer.writeheader()
        writer.writerows(asdict(row) for row in rows)


def write_markdown(rows: Sequence[ACVPAuditRow], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Official NIST ACVP public-key rank-defect audit\n\n",
        "Source: `usnistgov/ACVP-Server`, `ML-DSA-keyGen-FIPS204`, retrieved "
        "2026-08-10.  The archive contains the exact prompt and expected-results "
        "JSON files.\n\n",
        f"- prompt SHA-256: `{ACVP_PROMPT_SHA256}`\n",
        f"- expected-results SHA-256: `{ACVP_EXPECTED_SHA256}`\n\n",
        "For every public key, the audit parses the first 32 bytes as `rho`, "
        "runs FIPS 204 `ExpandA`/`RejNTTPoly`, forms all 256 rectangular NTT "
        "lanes, and sums their column-rank deficiencies.\n\n",
        "| set | vectors | min defect | max defect | classical budget | "
        "QROM budget | pass/pass |\n",
        "|---|---:|---:|---:|---:|---:|---:|\n",
    ]
    for name in ("ML-DSA-44", "ML-DSA-65", "ML-DSA-87"):
        selected = [row for row in rows if row.parameter_set == name]
        passes = sum(
            row.passes_classical_budget and row.passes_qrom_budget for row in selected
        )
        lines.append(
            f"| {name} | {len(selected)} | "
            f"{min(row.rank_defect for row in selected)} | "
            f"{max(row.rank_defect for row in selected)} | "
            f"{selected[0].classical_defect_budget} | "
            f"{selected[0].qrom_defect_budget} | {passes}/{len(selected)} |\n"
        )
    lines.append(
        "\nThis is an audit of the deterministic rank certificate on a fixed "
        "official corpus, not a statistical proof about all ML-DSA keys.  The "
        "per-key rows, including a hash of each `rho`, are in the companion CSV.\n"
    )
    path.write_text("".join(lines), encoding="utf-8")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--prompt",
        type=Path,
        default=Path("research/sources/nist-acvp-mldsa-keygen-prompt.json"),
    )
    parser.add_argument(
        "--expected",
        type=Path,
        default=Path("research/sources/nist-acvp-mldsa-keygen-expected.json"),
    )
    parser.add_argument(
        "--output-prefix",
        type=Path,
        default=Path("results/mldsa_acvp_key_audit"),
    )
    args = parser.parse_args(argv)
    rows = audit_acvp_keys(args.prompt, args.expected)
    write_csv(rows, args.output_prefix.with_suffix(".csv"))
    write_markdown(rows, args.output_prefix.with_suffix(".md"))
    print(f"audited {len(rows)} official ACVP public keys")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
