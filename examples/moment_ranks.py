"""Exact ranks of rectangular powered convolution windows in characteristic zero.

Research implementation accompanying docs/research/higher-power-rank.md.
Integer operation counts per window depend on the power, even for huge dimensions.
"""

from collections.abc import Iterator
from dataclasses import dataclass
from math import gcd

from examples.novelty_models import _band_domain, _integer


@dataclass(frozen=True)
class _Segment:
    """Residue classes with the same two quotient intervals."""

    start: int
    stop: int
    left_end: int
    right_start: int
    right_end: int

    @property
    def size(self) -> int:
        return self.left_end + self.right_end - self.right_start

    @property
    def width(self) -> int:
        return self.stop - self.start

    def samples(self, period: int) -> Iterator[list[int]]:
        # A degree-size polynomial family is spanned by size+1 translates.
        for residue in range(self.start, min(self.stop, self.start + self.size + 1)):
            yield [
                residue + period * i
                for interval in (range(self.left_end), range(self.right_start, self.right_end))
                for i in interval
            ]


def _segments(rows: int, columns: int, degree: int, power: int, offset: int) -> list[_Segment]:
    _integer("power", power, 1)
    _integer("degree", degree)
    _band_domain(rows, columns, power * degree, offset)
    period = degree + 1
    left = columns + offset - rows
    right = columns + offset
    end = columns + power * degree
    breaks = sorted({0, period, left % period, right % period, end % period})
    return [
        _Segment(
            lo,
            hi,
            (left + period - 1 - lo) // period,
            (right + period - 1 - lo) // period,
            (end + period - 1 - lo) // period,
        )
        for lo, hi in zip(breaks[:-1], breaks[1:], strict=True)
    ]


def _annihilator(exponents: list[int]) -> list[int]:
    """Coefficients in ascending order of the polynomial with these roots."""
    coefficients = [1]
    for k in exponents:
        coefficients = [
            a - k * b for a, b in zip([0] + coefficients, coefficients + [0], strict=True)
        ]
    return coefficients


def _constraints(segments: list[_Segment], period: int, power: int) -> Iterator[list[int]]:
    for segment in segments:
        if segment.size >= power:
            continue
        for exponents in segment.samples(period):
            polynomial = _annihilator(exponents)
            for shift in range(power - segment.size):
                yield [0] * shift + polynomial + [0] * (power - segment.size - shift - 1)


def _constraint_rank(rows: Iterator[list[int]], width: int) -> int:
    """Fraction-free row elimination; retain at most width independent rows."""
    basis: dict[int, list[int]] = {}
    for row in rows:
        for k in range(width):
            if not row[k]:
                continue
            if k not in basis:
                basis[k] = row
                break
            pivot = basis[k]
            row = [pivot[k] * v - row[k] * p for v, p in zip(row, pivot, strict=True)]
            scale = gcd(*row)
            if scale > 1:
                row = [v // scale for v in row]
        if len(basis) == width:
            break
    return len(basis)


def equal_even_power_rank(size: int, degree: int, power: int) -> int:
    """Total rank of multiplication by h_degree**power for two equal Jordan sizes.

    Derived by summing the maximal graded ranks over a characteristic-zero field.
    """
    _integer("size", size, 1)
    _integer("degree", degree)
    _integer("power", power, 1)
    if power % 2:
        raise ValueError("The Gram formula requires an even power")
    return max(0, size - (power // 2) * degree) ** 2


def moment_band_rank(rows: int, columns: int, degree: int, power: int, offset: int) -> int:
    """Rank over Q of R[i,j] = [z**(offset+j-i)](1+...+z**degree)**power."""
    segments = _segments(rows, columns, degree, power, offset)
    # A centered maximal square minor is the Gram matrix of polynomial shifts.
    last_offset = offset + columns - rows
    if power % 2 == 0 and min(offset, last_offset) <= (power // 2) * degree <= max(
        offset, last_offset
    ):
        return min(rows, columns)
    excess = sum(s.width * max(0, s.size - power) for s in segments)
    if any(s.size == 0 for s in segments):
        return columns - excess
    constraint_rank = _constraint_rank(_constraints(segments, degree + 1, power), power)
    return columns - excess - (power - constraint_rank)


def third_power_band_rank(rows: int, columns: int, degree: int, offset: int) -> int:
    """Explicit cubic classification by empty classes, singletons and pair collinearity."""
    segments = _segments(rows, columns, degree, 3, offset)
    excess = sum(s.width * max(0, s.size - 3) for s in segments)
    if any(s.size == 0 for s in segments):
        return columns - excess
    singles = sum(s.width for s in segments if s.size == 1)
    pairs = sum(s.width for s in segments if s.size == 2)
    if singles:
        common = int(singles == 1 and pairs == 0)
    elif pairs < 2:
        common = 3 - pairs
    else:
        points = ((a + b, a * b) for s in segments if s.size == 2 for a, b in s.samples(degree + 1))
        x0, y0 = next(points)
        x1, y1 = next(points)
        common = int(all((x1 - x0) * (y - y0) == (y1 - y0) * (x - x0) for x, y in points))
    return columns - excess - common
