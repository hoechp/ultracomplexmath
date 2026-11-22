"""Real matrices and the original canonicalizing M2R experiment."""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass

from .geometry import BASE, Vector, rotate, scale, unit
from .numbers import Binary, Complex, Dual, Hypercomplex


@dataclass(frozen=True, init=False)
class Matrix:
    rows: tuple[tuple[float, ...], ...]

    def __init__(self, rows: Sequence[Sequence[float]]) -> None:
        values = tuple(tuple(map(float, row)) for row in rows)
        if not values or not values[0] or any(len(row) != len(values[0]) for row in values):
            raise ValueError("Expected a nonempty rectangular matrix")
        if not all(math.isfinite(x) for row in values for x in row):
            raise ValueError("Matrix entries must be finite")
        object.__setattr__(self, "rows", values)

    @classmethod
    def zeros(cls, rows: int, columns: int) -> Matrix:
        return cls([[0.0] * columns for _ in range(rows)])

    @classmethod
    def from_flat(cls, rows: int, columns: int, values: Sequence[float]) -> Matrix:
        if rows <= 0 or columns <= 0 or len(values) != rows * columns:
            raise ValueError("Invalid dimensions")
        return cls([values[i * columns : (i + 1) * columns] for i in range(rows)])

    @classmethod
    def rotation(cls, axis: Sequence[float] | int, radians: float) -> Matrix:
        """Row-vector Rodrigues matrix: points @ rotation."""
        direction = BASE[axis] if isinstance(axis, int) else axis
        return cls([rotate(base, direction, radians) for base in BASE])

    @classmethod
    def translation(cls, direction: Sequence[float] | int, distance: float) -> Matrix:
        return cls(
            [scale(unit(BASE[direction] if isinstance(direction, int) else direction), distance)]
        )

    @property
    def shape(self) -> tuple[int, int]:
        return len(self.rows), len(self.rows[0])

    @property
    def transpose(self) -> Matrix:
        return Matrix(list(zip(*self.rows, strict=True)))

    @property
    def vectors(self) -> tuple[Vector, ...]:
        return self.rows

    def __add__(self, other: Matrix) -> Matrix:
        m, n = self.shape
        p, q = other.shape
        if (m != p and min(m, p) != 1) or (n != q and min(n, q) != 1):
            raise ValueError("Only singleton-axis broadcasting is supported")
        return Matrix(
            [
                [self.rows[i % m][j % n] + other.rows[i % p][j % q] for j in range(max(n, q))]
                for i in range(max(m, p))
            ]
        )

    def __sub__(self, other: Matrix) -> Matrix:
        return self + other * -1

    def __mul__(self, scalar: float) -> Matrix:
        return Matrix([[x * scalar for x in row] for row in self.rows])

    __rmul__ = __mul__

    def __matmul__(self, other: Matrix) -> Matrix:
        if self.shape[1] != other.shape[0]:
            raise ValueError("Matrix dimensions do not align")
        return Matrix(
            [
                [
                    math.fsum(a * b for a, b in zip(row, col, strict=True))
                    for col in other.transpose.rows
                ]
                for row in self.rows
            ]
        )


@dataclass(frozen=True, init=False)
class M2R:
    """Historical projection to canonical 2×2 forms; composition is not associative.

    Each raw operation is canonicalized anew, losing its similarity basis.
    Use Matrix for ordinary linear algebra.
    """

    value: Hypercomplex

    def __init__(self, value: Hypercomplex | Sequence[Sequence[float]]) -> None:
        if isinstance(value, Hypercomplex):
            result = value
        else:
            (a, b), (c, d) = value
            x = (a + d) / 2
            p = (a - x) ** 2 + b * c
            result = (
                Binary(x, math.sqrt(p))
                if p > 0
                else Complex(x, math.sqrt(-p))
                if p < 0
                else Dual(x, b if b else c)
            )
        object.__setattr__(self, "value", result)

    @property
    def matrix(self) -> Matrix:
        a, b = self.value.real, self.value.imag
        if isinstance(self.value, Dual):
            return Matrix(((a, b), (0, a)))
        if isinstance(self.value, Binary):
            return Matrix(((a, b), (b, a)))
        return Matrix(((a, -b), (b, a)))

    def __add__(self, other: M2R) -> M2R:
        return M2R((self.matrix + other.matrix).rows)

    def __sub__(self, other: M2R) -> M2R:
        return M2R((self.matrix - other.matrix).rows)

    def __mul__(self, other: M2R) -> M2R:
        return M2R((self.matrix @ other.matrix).rows)

    def __truediv__(self, other: M2R) -> M2R:
        return self * M2R(other.value.inverse())

    def __pow__(self, other: M2R) -> M2R:
        return M2R((M2R(self.value.log()) * other).value.exp())
