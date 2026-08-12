from fractions import Fraction

from ehrhart_fswa.experiment import run_baseline
from ehrhart_fswa.shifts import integer_l1_shifts


def test_l1_shift_enumerator_has_no_duplicates_and_respects_radius() -> None:
    shifts = list(integer_l1_shifts(3, 2))
    assert len(shifts) == len(set(shifts))
    assert all(sum(map(abs, shift)) <= 2 for shift in shifts)
    # The 3-dimensional cross-polytope of radius 2 has 25 lattice points.
    assert len(shifts) == 25


def test_small_baseline_is_exact_and_within_budget() -> None:
    rows = run_baseline([2], [4], 1)
    assert {row.family for row in rows} == {
        "cube",
        "cross_polytope",
        "hybrid_H",
        "hexagon_blocks",
    }
    for row in rows:
        assert row.actual_max_l2_squared <= row.norm_budget**2
        acceptance = Fraction(row.acceptance_exact)
        assert acceptance == Fraction(row.overlap_count, row.lattice_point_count)
        assert 0 < acceptance <= 1
