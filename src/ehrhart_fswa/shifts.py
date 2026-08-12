"""Finite integer shift sets used by the exact experiments."""

from __future__ import annotations

from collections.abc import Iterator


def integer_l1_shifts(
    dimension: int, radius: int, *, include_zero: bool = True
) -> Iterator[tuple[int, ...]]:
    """Yield all integer vectors ``u`` satisfying ``||u||_1 <= radius``."""

    if dimension < 1:
        raise ValueError("dimension must be positive")
    if radius < 0:
        raise ValueError("radius must be nonnegative")

    prefix = [0] * dimension

    def recurse(index: int, remaining: int) -> Iterator[tuple[int, ...]]:
        if index == dimension:
            candidate = tuple(prefix)
            if include_zero or any(candidate):
                yield candidate
            return
        for value in range(-remaining, remaining + 1):
            prefix[index] = value
            yield from recurse(index + 1, remaining - abs(value))

    yield from recurse(0, radius)
