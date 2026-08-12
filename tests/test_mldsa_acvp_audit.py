from __future__ import annotations

import hashlib
from pathlib import Path

from ehrhart_fswa.mldsa_acvp_audit import (
    audit_acvp_keys,
    expand_a_ntt_lanes,
    rej_ntt_poly,
)
from ehrhart_fswa.mldsa_case import PARAMETER_SETS


ROOT = Path(__file__).resolve().parents[1]
PROMPT = ROOT / "research/sources/nist-acvp-mldsa-keygen-prompt.json"
EXPECTED = ROOT / "research/sources/nist-acvp-mldsa-keygen-expected.json"


def test_rej_ntt_poly_is_deterministic_and_in_range() -> None:
    seed = bytes(range(34))
    first = rej_ntt_poly(seed)
    assert first == rej_ntt_poly(seed)
    assert len(first) == 256
    assert all(0 <= value < 8_380_417 for value in first)


def test_expand_a_has_the_fips_rectangular_lane_shape() -> None:
    parameters = PARAMETER_SETS[0]
    lanes = expand_a_ntt_lanes(bytes(32), parameters)
    assert len(lanes) == 256
    assert all(len(lane) == parameters.k for lane in lanes)
    assert all(len(row) == parameters.ell for lane in lanes for row in lane)


def test_official_acvp_public_keys_pass_both_defect_budgets() -> None:
    rows = audit_acvp_keys(PROMPT, EXPECTED)
    assert len(rows) == 75
    assert {row.parameter_set for row in rows} == {
        "ML-DSA-44",
        "ML-DSA-65",
        "ML-DSA-87",
    }
    assert all(row.rank_defect == 0 for row in rows)
    assert all(row.passes_classical_budget for row in rows)
    assert all(row.passes_qrom_budget for row in rows)


def test_first_acvp_rho_matches_fips_keygen_seed_expansion() -> None:
    import json

    prompt = json.loads(PROMPT.read_text(encoding="utf-8"))
    expected = json.loads(EXPECTED.read_text(encoding="utf-8"))
    seed = bytes.fromhex(prompt["testGroups"][0]["tests"][0]["seed"])
    public_key = bytes.fromhex(expected["testGroups"][0]["tests"][0]["pk"])
    parameters = PARAMETER_SETS[0]
    derived_rho = hashlib.shake_256(
        seed + bytes((parameters.k, parameters.ell))
    ).digest(128)[:32]
    assert public_key[:32] == derived_rho
