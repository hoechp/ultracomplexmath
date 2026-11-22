"""Exact rational linear algebra, including zero-divisor solution families."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from fractions import Fraction

from .exact import QONE, QZERO, ExactScalar, ExactUltra, Rational, rational
from .linalg import InconsistentSystemError, SingularSystemError


def rational_solution(
    matrix: Sequence[Sequence[Rational]], rhs: Sequence[Rational]
) -> tuple[tuple[Fraction, ...], tuple[tuple[Fraction, ...], ...]]:
    """Rational RREF: exact zero tests, no tolerances or float intermediates."""
    if not matrix or not matrix[0] or len(matrix) != len(rhs):
        raise ValueError("Expected nonempty matrix and matching right-hand side")
    columns = len(matrix[0])
    if any(len(row) != columns for row in matrix):
        raise ValueError("Ragged matrix")
    rows = [[*(rational(x) for x in row), rational(b)] for row, b in zip(matrix, rhs, strict=True)]
    pivots: list[int] = []
    for col in range(columns):
        rank = len(pivots)
        pivot_row = next((i for i in range(rank, len(rows)) if rows[i][col]), None)
        if pivot_row is None:
            continue
        rows[rank], rows[pivot_row] = rows[pivot_row], rows[rank]
        p = rows[rank][col]
        rows[rank] = [x / p for x in rows[rank]]
        for i in range(len(rows)):
            if i != rank and rows[i][col]:
                factor = rows[i][col]
                rows[i] = [a - factor * b for a, b in zip(rows[i], rows[rank], strict=True)]
        pivots.append(col)
    if any(not any(row[:-1]) and row[-1] for row in rows):
        raise InconsistentSystemError("Exactly inconsistent equations")
    particular = [Fraction(0)] * columns
    for i, col in enumerate(pivots):
        particular[col] = rows[i][-1]
    basis = []
    for free in sorted(set(range(columns)) - set(pivots)):
        v = [Fraction(0)] * columns
        v[free] = Fraction(1)
        for i, col in enumerate(pivots):
            v[col] = -rows[i][free]
        basis.append(tuple(v))
    return tuple(particular), tuple(basis)


@dataclass(frozen=True)
class ExactLinearSolution:
    """Complete affine solution space over Q, including a particular solution."""

    particular: tuple[ExactUltra, ...]
    basis: tuple[tuple[ExactUltra, ...], ...]

    def at(self, *parameters: Rational) -> tuple[ExactUltra, ...]:
        if len(parameters) != len(self.basis):
            raise ValueError("One rational parameter is required per free direction")
        weights = tuple(rational(t) for t in parameters)
        return tuple(
            x + sum((t * v[i] for t, v in zip(weights, self.basis, strict=True)), QZERO)
            for i, x in enumerate(self.particular)
        )


def exact_solution_space(
    matrix: Sequence[Sequence[ExactScalar]],
    rhs: Sequence[ExactScalar],
    *,
    basis_indices: Sequence[int] = tuple(range(8)),
) -> ExactLinearSolution:
    if not matrix or not matrix[0] or len(matrix) != len(rhs):
        raise ValueError("Expected nonempty matrix and matching right-hand side")
    n, indices = len(matrix[0]), tuple(basis_indices)
    if (
        not indices
        or len(set(indices)) != len(indices)
        or any(type(k) is not int or k not in range(8) for k in indices)
    ):
        raise ValueError("Invalid basis indices")
    rows: list[list[Fraction]] = []
    values: list[Fraction] = []
    for row, b in zip(matrix, rhs, strict=True):
        if len(row) != n:
            raise ValueError("Ragged matrix")
        columns = [ExactUltra.coerce(a) * ExactUltra.unit(k) for a in row for k in indices]
        rows.extend([[v.coefficients[k] for v in columns] for k in range(8)])
        values.extend(ExactUltra.coerce(b).coefficients)
    particular, basis = rational_solution(rows, values)

    def decode(v: tuple[Fraction, ...]) -> tuple[ExactUltra, ...]:
        return tuple(
            sum(
                (ExactUltra.unit(k) * v[c * len(indices) + j] for j, k in enumerate(indices)), QZERO
            )
            for c in range(n)
        )

    return ExactLinearSolution(decode(particular), tuple(decode(v) for v in basis))


def exact_solve(
    matrix: Sequence[Sequence[ExactScalar]], rhs: Sequence[ExactScalar]
) -> tuple[ExactUltra, ...]:
    solution = exact_solution_space(matrix, rhs)
    if solution.basis:
        raise SingularSystemError("Multiple solutions; use exact_solution_space()")
    return solution.particular


@dataclass(frozen=True, init=False)
class ExactMatrix:
    """Matrices over ExactUltra. All entries and results retain rational coefficients."""

    rows: tuple[tuple[ExactUltra, ...], ...]

    def __init__(self, rows: Sequence[Sequence[ExactScalar]]) -> None:
        values = tuple(tuple(ExactUltra.coerce(x) for x in row) for row in rows)
        if not values or not values[0] or any(len(row) != len(values[0]) for row in values):
            raise ValueError("Expected a nonempty rectangular matrix")
        object.__setattr__(self, "rows", values)

    @classmethod
    def identity(cls, size: int) -> ExactMatrix:
        if type(size) is not int or size <= 0:
            raise ValueError("Positive integer matrix size required")
        return cls([[int(i == j) for j in range(size)] for i in range(size)])

    @property
    def shape(self) -> tuple[int, int]:
        return len(self.rows), len(self.rows[0])

    @property
    def transpose(self) -> ExactMatrix:
        return ExactMatrix(tuple(zip(*self.rows, strict=True)))

    def __add__(self, other: ExactMatrix) -> ExactMatrix:
        if self.shape != other.shape:
            raise ValueError("Matrix shapes must match")
        return ExactMatrix(
            [
                [a + b for a, b in zip(row, col, strict=True)]
                for row, col in zip(self.rows, other.rows, strict=True)
            ]
        )

    def __neg__(self) -> ExactMatrix:
        return self * -1

    def __sub__(self, other: ExactMatrix) -> ExactMatrix:
        return self + -other

    def __mul__(self, scalar: ExactScalar) -> ExactMatrix:
        value = ExactUltra.coerce(scalar)
        return ExactMatrix([[x * value for x in row] for row in self.rows])

    __rmul__ = __mul__

    def __matmul__(self, other: ExactMatrix) -> ExactMatrix:
        if self.shape[1] != other.shape[0]:
            raise ValueError("Matrix dimensions do not align")
        return ExactMatrix(
            [
                [
                    sum((a * b for a, b in zip(row, col, strict=True)), QZERO)
                    for col in other.transpose.rows
                ]
                for row in self.rows
            ]
        )

    def apply(self, vector: Sequence[ExactScalar]) -> tuple[ExactUltra, ...]:
        if len(vector) != self.shape[1]:
            raise ValueError("Vector dimension does not match")
        return tuple(
            sum((a * ExactUltra.coerce(b) for a, b in zip(row, vector, strict=True)), QZERO)
            for row in self.rows
        )

    def solve(self, rhs: Sequence[ExactScalar]) -> tuple[ExactUltra, ...]:
        return exact_solve(self.rows, rhs)

    def inverse(self) -> ExactMatrix:
        n, m = self.shape
        if n != m:
            raise ValueError("Inverse requires a square matrix")
        columns = [self.solve([int(i == j) for i in range(n)]) for j in range(n)]
        return ExactMatrix(tuple(zip(*columns, strict=True)))

    def determinant(self) -> ExactUltra:
        """Faddeev–LeVerrier over Q-algebras: no division by matrix pivots."""
        n, m = self.shape
        if n != m:
            raise ValueError("Determinant requires a square matrix")
        identity = ExactMatrix.identity(n)
        b, coefficient = identity, QONE
        for k in range(1, n + 1):
            product = self @ b
            coefficient = -sum((product.rows[i][i] for i in range(n)), QZERO) / k
            b = product + identity * coefficient
        return coefficient * (-1 if n % 2 else 1)

    def __pow__(self, exponent: int) -> ExactMatrix:
        if type(exponent) is not int or self.shape[0] != self.shape[1]:
            raise ValueError("Matrix powers require a square matrix and integer exponent")
        factor = self if exponent >= 0 else self.inverse()
        n, result = abs(exponent), ExactMatrix.identity(self.shape[0])
        while n:
            if n & 1:
                result = result @ factor
            n >>= 1
            if n:
                factor = factor @ factor
        return result
