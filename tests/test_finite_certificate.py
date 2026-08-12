from fractions import Fraction

from ehrhart_fswa.finite_certificate import (
    common_target,
    endogenous_membership_law,
    exogenous_membership_law,
    maximal_common_subdistribution,
)


def test_common_target_is_uniform_for_each_exogenous_shift() -> None:
    source = frozenset({(0,), (1,), (2,)})
    shifts = [(0,), (1,)]
    target = common_target(source, shifts)
    assert target == frozenset({(1,), (2,)})
    uniform = {(1,): Fraction(1, 2), (2,): Fraction(1, 2)}
    assert exogenous_membership_law(source, shifts[0], target) == uniform
    assert exogenous_membership_law(source, shifts[1], target) == uniform


def test_endogenous_counterexample_is_not_uniform() -> None:
    source = frozenset({(0,), (1,), (2,)})
    target = frozenset({(1,), (2,)})
    shift_by_source: dict[tuple[int, ...], tuple[int, ...]] = {
        (0,): (0,),
        (1,): (0,),
        (2,): (1,),
    }
    assert endogenous_membership_law(source, shift_by_source, target) == {
        (1,): Fraction(1)
    }


def test_maximal_common_subdistribution_for_nonuniform_laws() -> None:
    left: dict[tuple[int, ...], Fraction] = {
        (0,): Fraction(9, 10),
        (1,): Fraction(1, 10),
    }
    right: dict[tuple[int, ...], Fraction] = {
        (0,): Fraction(1, 10),
        (1,): Fraction(9, 10),
    }
    acceptance, output, filters = maximal_common_subdistribution((left, right))
    assert acceptance == Fraction(1, 5)
    assert output == {(0,): Fraction(1, 2), (1,): Fraction(1, 2)}
    assert filters == (
        {(0,): Fraction(1, 9), (1,): Fraction(1)},
        {(0,): Fraction(1), (1,): Fraction(1, 9)},
    )


def test_uniform_translates_recover_common_target_ratio() -> None:
    laws: tuple[dict[tuple[int, ...], Fraction], ...] = (
        {(0,): Fraction(1, 3), (1,): Fraction(1, 3), (2,): Fraction(1, 3)},
        {(1,): Fraction(1, 3), (2,): Fraction(1, 3), (3,): Fraction(1, 3)},
    )
    acceptance, output, _ = maximal_common_subdistribution(laws)
    assert acceptance == Fraction(2, 3)
    assert output == {(1,): Fraction(1, 2), (2,): Fraction(1, 2)}


def test_disjoint_laws_have_no_positive_common_subdistribution() -> None:
    left: dict[tuple[int, ...], Fraction] = {(0,): Fraction(1)}
    right: dict[tuple[int, ...], Fraction] = {(1,): Fraction(1)}
    acceptance, output, filters = maximal_common_subdistribution((left, right))
    assert acceptance == 0
    assert output == {}
    assert filters == ({}, {})
