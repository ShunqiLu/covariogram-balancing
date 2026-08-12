"""Finite-range discovery of Ehrhart (quasi-)polynomial candidates.

The representation uses the Newton/binomial basis.  For a residue class and
``k = (t - base_t) / period``, a degree-``d`` constituent is

    sum_{j=0}^d c_j * binomial(k, j).

The coefficients are exact integers obtained from forward differences.
Discovery is not a mathematical proof beyond the checked range; the returned
object records that range explicitly.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import comb
from typing import Callable, Mapping


@dataclass(frozen=True)
class Constituent:
    residue: int
    base_t: int
    coefficients: tuple[int, ...]

    def evaluate(self, t: int, period: int) -> int:
        if t < self.base_t or t % period != self.residue:
            raise ValueError("t is outside this constituent's progression")
        k = (t - self.base_t) // period
        return sum(
            coefficient * comb(k, degree)
            for degree, coefficient in enumerate(self.coefficients)
        )


@dataclass(frozen=True)
class QuasiPolynomialCandidate:
    degree: int
    period: int
    onset: int
    checked_through: int
    constituents: tuple[Constituent, ...]

    def evaluate(self, t: int) -> int:
        if not self.onset <= t <= self.checked_through:
            raise ValueError("t is outside the certified finite range")
        residue = t % self.period
        constituent = next(
            item for item in self.constituents if item.residue == residue
        )
        return constituent.evaluate(t, self.period)


def _newton_coefficients(values: list[int], degree: int) -> tuple[int, ...]:
    if len(values) < degree + 1:
        raise ValueError("not enough values to determine the requested degree")
    row = values[: degree + 1]
    coefficients = [row[0]]
    for _ in range(degree):
        row = [right - left for left, right in zip(row, row[1:])]
        coefficients.append(row[0])
    return tuple(coefficients)


def fit_quasipolynomial_candidate(
    values: Mapping[int, int],
    *,
    degree: int,
    max_period: int = 6,
    max_onset: int = 12,
    minimum_holdout: int = 3,
) -> QuasiPolynomialCandidate | None:
    """Find the smallest period and then earliest onset fitting all samples.

    At least ``minimum_holdout`` values per residue class are kept beyond the
    ``degree + 1`` values that determine each constituent.
    """

    if degree < 0:
        raise ValueError("degree must be nonnegative")
    if not values:
        raise ValueError("values must not be empty")
    if set(values) != set(range(min(values), max(values) + 1)):
        raise ValueError("values must cover a contiguous integer interval")

    checked_through = max(values)
    for period in range(1, max_period + 1):
        for onset in range(min(values), min(max_onset, checked_through) + 1):
            constituents: list[Constituent] = []
            fits = True
            for residue in range(period):
                progression = [
                    t
                    for t in range(onset, checked_through + 1)
                    if t % period == residue
                ]
                if len(progression) < degree + 1 + minimum_holdout:
                    fits = False
                    break
                base_t = progression[0]
                coefficients = _newton_coefficients(
                    [values[t] for t in progression], degree
                )
                constituent = Constituent(residue, base_t, coefficients)
                if any(
                    constituent.evaluate(t, period) != values[t] for t in progression
                ):
                    fits = False
                    break
                constituents.append(constituent)
            if fits:
                return QuasiPolynomialCandidate(
                    degree=degree,
                    period=period,
                    onset=onset,
                    checked_through=checked_through,
                    constituents=tuple(constituents),
                )
    return None


def discover_from_counter(
    counter: Callable[[int], int],
    *,
    degree: int,
    checked_through: int = 40,
    max_period: int = 6,
    max_onset: int = 12,
) -> tuple[QuasiPolynomialCandidate | None, dict[int, int]]:
    """Sample an exact counter and discover a candidate from those values."""

    values = {t: counter(t) for t in range(checked_through + 1)}
    candidate = fit_quasipolynomial_candidate(
        values,
        degree=degree,
        max_period=max_period,
        max_onset=max_onset,
    )
    return candidate, values


def constituent_formula(
    constituent: Constituent, period: int, *, variable: str = "t"
) -> str:
    """Render an exact Newton-basis constituent formula."""

    if period == 1 and constituent.base_t == 0:
        k_expression = variable
    else:
        k_expression = f"({variable}-{constituent.base_t})/{period}"
    terms: list[str] = []
    for degree, coefficient in enumerate(constituent.coefficients):
        if coefficient == 0:
            continue
        if degree == 0:
            terms.append(str(coefficient))
        elif degree == 1:
            terms.append(f"{coefficient}*C({k_expression},1)")
        else:
            terms.append(f"{coefficient}*C({k_expression},{degree})")
    return " + ".join(terms) if terms else "0"
