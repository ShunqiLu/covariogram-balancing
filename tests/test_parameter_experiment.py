from fractions import Fraction

import pytest

from ehrhart_fswa.fswa import Family, common_core_metrics
from ehrhart_fswa.parameter_experiment import optimize_family, run_optimization


@pytest.mark.parametrize(
    "family",
    [
        "cube",
        "cross_polytope",
        "cross_blocks_2",
        "cross_blocks_4",
        "hexagon_blocks",
        "hybrid_full",
        "hybrid_blocks_4",
    ],
)
def test_optimizer_returns_first_exact_scale(family: Family) -> None:
    dimension = 4
    threshold = Fraction(1, 2)
    row = optimize_family(family, dimension, 1, [threshold], max_scale=100)[0]
    assert Fraction(row.acceptance_exact) >= threshold
    if row.source_scale > 1:
        previous = common_core_metrics(family, dimension, row.source_scale - 1, 1)
        assert previous.acceptance < threshold


def test_optimization_preserves_requested_threshold_order() -> None:
    thresholds = [Fraction(9, 10), Fraction(1, 2), Fraction(3, 4)]
    rows = optimize_family("cube", 4, 1, thresholds, max_scale=100)
    assert [row.required_acceptance for row in rows] == [
        "9/10",
        "1/2",
        "3/4",
    ]


def test_small_run_contains_compatible_families() -> None:
    rows = run_optimization([8], 1, [Fraction(1, 2)])
    assert {row.family for row in rows} == {
        "cube",
        "cross_polytope",
        "cross_blocks_2",
        "cross_blocks_4",
        "cross_blocks_8",
        "hexagon_blocks",
        "hybrid_full",
        "hybrid_blocks_4",
        "hybrid_blocks_8",
    }
