"""Low-dimensional exact enumeration for rational symmetric H-polytopes."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import product
from typing import Iterator, Sequence


def _as_fraction(value: int | Fraction) -> Fraction:
    return value if isinstance(value, Fraction) else Fraction(value)


@dataclass(frozen=True)
class SymmetricHPolytope:
    """A polytope ``P = {x : |a_j dot x| <= b_j for every j}``.

    ``coordinate_bounds`` supplies a certified axis-aligned bounding box for
    enumeration. It need not describe facets and may be conservative.
    """

    normals: tuple[tuple[int, ...], ...]
    bounds: tuple[Fraction, ...]
    coordinate_bounds: tuple[Fraction, ...]

    def __post_init__(self) -> None:
        if not self.normals:
            raise ValueError("at least one normal is required")
        dimension = len(self.coordinate_bounds)
        if dimension < 1:
            raise ValueError("dimension must be positive")
        if len(self.bounds) != len(self.normals):
            raise ValueError("normals and bounds must have equal length")
        if any(len(normal) != dimension for normal in self.normals):
            raise ValueError("all normals must match the dimension")
        if any(bound <= 0 for bound in self.bounds):
            raise ValueError("facet bounds must be positive")
        if any(bound < 0 for bound in self.coordinate_bounds):
            raise ValueError("coordinate bounds must be nonnegative")

    @classmethod
    def create(
        cls,
        normals: Sequence[Sequence[int]],
        bounds: Sequence[int | Fraction],
        coordinate_bounds: Sequence[int | Fraction],
    ) -> "SymmetricHPolytope":
        return cls(
            tuple(tuple(map(int, normal)) for normal in normals),
            tuple(_as_fraction(bound) for bound in bounds),
            tuple(_as_fraction(bound) for bound in coordinate_bounds),
        )

    @property
    def dimension(self) -> int:
        return len(self.coordinate_bounds)

    def contains(
        self,
        point: Sequence[int],
        scale: int,
        *,
        l1_erosion: int = 0,
    ) -> bool:
        """Test membership, optionally eroded by an integer l1 ball."""

        if len(point) != self.dimension:
            raise ValueError("point has the wrong dimension")
        if scale < 0 or l1_erosion < 0:
            raise ValueError("scale and erosion must be nonnegative")
        for normal, bound in zip(self.normals, self.bounds):
            value = abs(sum(a * int(x) for a, x in zip(normal, point)))
            support = l1_erosion * max(map(abs, normal))
            if value + support > scale * bound:
                return False
        return True

    def lattice_points(
        self, scale: int, *, l1_erosion: int = 0
    ) -> Iterator[tuple[int, ...]]:
        if scale < 0 or l1_erosion < 0:
            raise ValueError("scale and erosion must be nonnegative")
        integer_bounds = [
            (scale * bound).numerator // (scale * bound).denominator
            for bound in self.coordinate_bounds
        ]
        ranges = [range(-bound, bound + 1) for bound in integer_bounds]
        for point in product(*ranges):
            if self.contains(point, scale, l1_erosion=l1_erosion):
                yield point

    def lattice_count(self, scale: int, *, l1_erosion: int = 0) -> int:
        return sum(1 for _ in self.lattice_points(scale, l1_erosion=l1_erosion))

    def overlap_count(self, scale: int, shift: Sequence[int]) -> int:
        if len(shift) != self.dimension:
            raise ValueError("shift has the wrong dimension")
        return sum(
            self.contains(
                tuple(point[i] + int(shift[i]) for i in range(self.dimension)),
                scale,
            )
            for point in self.lattice_points(scale)
        )

    def common_core_count_l1(self, scale: int, secret_l1_radius: int) -> int:
        """Count the intersection over all integer l1-bounded translations."""

        return self.lattice_count(scale, l1_erosion=secret_l1_radius)


def rational_half_square() -> SymmetricHPolytope:
    """The rational square ``[-1/2,1/2]^2`` (Ehrhart period two)."""

    return SymmetricHPolytope.create(
        normals=((1, 0), (0, 1)),
        bounds=(Fraction(1, 2), Fraction(1, 2)),
        coordinate_bounds=(Fraction(1, 2), Fraction(1, 2)),
    )


def integer_hexagon() -> SymmetricHPolytope:
    """The hexagon ``|x|, |y|, |x+y| <= 1``."""

    return SymmetricHPolytope.create(
        normals=((1, 0), (0, 1), (1, 1)),
        bounds=(1, 1, 1),
        coordinate_bounds=(1, 1),
    )


def rational_octagon() -> SymmetricHPolytope:
    """A centrally symmetric rational octagon with denominator two."""

    return SymmetricHPolytope.create(
        normals=((1, 0), (0, 1), (1, 1), (1, -1)),
        bounds=(1, 1, Fraction(3, 2), Fraction(3, 2)),
        coordinate_bounds=(1, 1),
    )
