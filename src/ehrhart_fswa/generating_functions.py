"""Exact rational generating functions for cross-polytope lenses."""

from __future__ import annotations

from dataclasses import dataclass
from math import comb
from typing import Mapping, Sequence

BivariatePolynomial = dict[tuple[int, int], int]


def _add_term(
    polynomial: BivariatePolynomial, exponent: tuple[int, int], coefficient: int
) -> None:
    polynomial[exponent] = polynomial.get(exponent, 0) + coefficient
    if polynomial[exponent] == 0:
        del polynomial[exponent]


def multiply_bivariate(
    left: Mapping[tuple[int, int], int],
    right: Mapping[tuple[int, int], int],
) -> BivariatePolynomial:
    result: BivariatePolynomial = {}
    for (left_x, left_y), left_coefficient in left.items():
        for (right_x, right_y), right_coefficient in right.items():
            _add_term(
                result,
                (left_x + right_x, left_y + right_y),
                left_coefficient * right_coefficient,
            )
    return result


def coordinate_numerator(absolute_shift: int) -> BivariatePolynomial:
    """Numerator of ``sum_x X^|x| Y^|x+a|`` over ``1-XY``."""

    if absolute_shift < 0:
        raise ValueError("absolute_shift must be nonnegative")
    if absolute_shift == 0:
        return {(0, 0): 1, (1, 1): 1}

    numerator: BivariatePolynomial = {
        (absolute_shift, 0): 1,
        (0, absolute_shift): 1,
    }
    for index in range(1, absolute_shift):
        _add_term(numerator, (index, absolute_shift - index), 1)
        _add_term(numerator, (index + 1, absolute_shift - index + 1), -1)
    return numerator


@dataclass(frozen=True)
class CrossLensGeneratingFunction:
    """Representation ``numerator(X,Y) / (1-XY)^dimension``."""

    dimension: int
    shift_partition: tuple[int, ...]
    numerator_terms: tuple[tuple[int, int, int], ...]

    @property
    def numerator(self) -> BivariatePolynomial:
        return {(x, y): coefficient for x, y, coefficient in self.numerator_terms}

    def coefficient(self, left_degree: int, right_degree: int) -> int:
        """Return the exact coefficient of ``X^left_degree Y^right_degree``."""

        if left_degree < 0 or right_degree < 0:
            return 0
        result = 0
        for x_degree, y_degree, coefficient in self.numerator_terms:
            left_remainder = left_degree - x_degree
            right_remainder = right_degree - y_degree
            if left_remainder == right_remainder and left_remainder >= 0:
                result += coefficient * comb(
                    self.dimension + left_remainder - 1, left_remainder
                )
        return result

    def rectangle_sum(self, radius: int) -> int:
        """Sum coefficients with both bidegrees at most ``radius``."""

        if radius < 0:
            return 0
        result = 0
        for x_degree, y_degree, coefficient in self.numerator_terms:
            steps = radius - max(x_degree, y_degree)
            if steps >= 0:
                result += coefficient * comb(self.dimension + steps, self.dimension)
        return result

    def eventual_binomial_formula(self) -> str:
        """Render the exact finite sum used for all nonnegative radii."""

        terms = []
        for x_degree, y_degree, coefficient in self.numerator_terms:
            offset = max(x_degree, y_degree)
            term = f"C(t-{offset}+{self.dimension},{self.dimension})_+"
            if coefficient != 1:
                term = f"{coefficient}*{term}"
            terms.append(term)
        return " + ".join(terms).replace("+ -", "- ") or "0"


def cross_lens_generating_function(
    shift: Sequence[int],
) -> CrossLensGeneratingFunction:
    """Build the exact rational generating function for an arbitrary shift."""

    if not shift:
        raise ValueError("shift must have positive dimension")
    partition = tuple(sorted((abs(int(value)) for value in shift), reverse=True))
    numerator: BivariatePolynomial = {(0, 0): 1}
    for absolute_shift in partition:
        numerator = multiply_bivariate(numerator, coordinate_numerator(absolute_shift))
    terms = tuple(
        (x_degree, y_degree, coefficient)
        for (x_degree, y_degree), coefficient in sorted(numerator.items())
    )
    return CrossLensGeneratingFunction(len(partition), partition, terms)
