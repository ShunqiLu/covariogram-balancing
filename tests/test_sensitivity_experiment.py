from fractions import Fraction

from ehrhart_fswa.sensitivity_experiment import run_sensitivity


def test_sensitivity_includes_four_thresholds_and_exact_pareto_rows() -> None:
    thresholds = [
        Fraction(1, 2),
        Fraction(3, 4),
        Fraction(9, 10),
        Fraction(99, 100),
    ]
    rows = run_sensitivity([8], 2, thresholds)
    assert {row.anchor_threshold for row in rows} == {
        "1/2",
        "3/4",
        "9/10",
        "99/100",
    }
    assert all(Fraction(row.acceptance_exact) > 0 for row in rows)
    assert any(row.pareto_optimal for row in rows)
