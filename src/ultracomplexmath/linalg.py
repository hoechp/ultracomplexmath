"""Solve square systems over Ultra by reducing to complex channel systems."""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass

from .core import Channel, NonFiniteError, Scalar, Ultra, _finite


class SingularSystemError(ArithmeticError):
    """No unique solution, or a pivot is numerically singular at the given tolerance."""


class InconsistentSystemError(ArithmeticError):
    """No solution satisfies all equations at the requested tolerance."""


@dataclass(frozen=True)
class RealSolution:
    particular: tuple[float, ...]
    basis: tuple[tuple[float, ...], ...]

    def at(self, *parameters: float) -> tuple[float, ...]:
        if len(parameters) != len(self.basis):
            raise ValueError("One real parameter is required per free direction")
        return tuple(
            x + sum(t * v[i] for t, v in zip(parameters, self.basis, strict=True))
            for i, x in enumerate(self.particular)
        )


def real_solution(
    matrix: Sequence[Sequence[float]], rhs: Sequence[float], *, rtol: float = 1e-12
) -> RealSolution:
    """Row-scaled RREF, including rectangular, inconsistent and singular systems."""
    if not math.isfinite(rtol) or rtol < 0:
        raise ValueError("rtol must be finite and nonnegative")
    if not matrix or not matrix[0] or len(matrix) != len(rhs):
        raise ValueError("Expected nonempty matrix and matching rhs")
    n = len(matrix[0])
    if any(len(row) != n for row in matrix):
        raise ValueError("Ragged matrix")
    rows = []
    for row, b in zip(matrix, rhs, strict=True):
        if not all(math.isfinite(v) for v in (*row, b)):
            raise ValueError("Coefficients must be finite")
        norm = max(map(abs, row)) or abs(b) or 1.0
        rows.append([v / norm for v in (*row, b)])
    if not all(math.isfinite(v) for row in rows for v in row):
        raise NonFiniteError("Row scaling exceeded finite arithmetic")
    pivots: list[int] = []
    for col in range(n):
        rank = len(pivots)
        if rank == len(rows):
            break
        p = max(range(rank, len(rows)), key=lambda i: abs(rows[i][col]))
        if abs(rows[p][col]) <= rtol:
            continue
        rows[rank], rows[p] = rows[p], rows[rank]
        pivot = rows[rank][col]
        rows[rank] = [v / pivot for v in rows[rank]]
        for i, row in enumerate(rows):
            if i != rank:
                factor = row[col]
                rows[i] = [a - factor * b for a, b in zip(row, rows[rank], strict=True)]
        pivots.append(col)
    if not all(math.isfinite(v) for row in rows for v in row):
        raise NonFiniteError("Row reduction exceeded finite arithmetic")
    if any(max(map(abs, row[:-1])) <= rtol and abs(row[-1]) > rtol for row in rows):
        raise InconsistentSystemError("Contradictory equations")
    particular = [0.0] * n
    for i, col in enumerate(pivots):
        particular[col] = rows[i][-1]
    basis = []
    for free in sorted(set(range(n)) - set(pivots)):
        direction = [0.0] * n
        direction[free] = 1.0
        for i, col in enumerate(pivots):
            direction[col] = -rows[i][free]
        basis.append(tuple(direction))
    return RealSolution(tuple(particular), tuple(basis))


@dataclass(frozen=True)
class LinearSolution:
    particular: tuple[Ultra, ...]
    basis: tuple[tuple[Ultra, ...], ...]

    def at(self, *parameters: float) -> tuple[Ultra, ...]:
        if len(parameters) != len(self.basis):
            raise ValueError("One real parameter is required per free direction")
        return tuple(
            x + sum((t * v[i] for t, v in zip(parameters, self.basis, strict=True)), Ultra())
            for i, x in enumerate(self.particular)
        )


def solution_space(
    matrix: Sequence[Sequence[Scalar]],
    rhs: Sequence[Scalar],
    *,
    basis_indices: Sequence[int] = tuple(range(8)),
    rtol: float = 1e-12,
) -> LinearSolution:
    """All solutions, parametrized over R; works even for zero-divisor pivots.

    Restrict unknowns to a subalgebra with (0,2), (0,1) or (0,4) for
    complex, split-complex or dual systems respectively. Equations always
    enforce every Ultra component, so restrictions cannot discard constraints.
    """
    if not matrix or not matrix[0] or len(matrix) != len(rhs):
        raise ValueError("Invalid dimensions")
    n, indices = len(matrix[0]), tuple(basis_indices)
    if not indices or len(set(indices)) != len(indices) or any(i not in range(8) for i in indices):
        raise ValueError("Invalid basis indices")
    rows: list[list[float]] = []
    values: list[float] = []
    for row, b in zip(matrix, rhs, strict=True):
        if len(row) != n:
            raise ValueError("Ragged matrix")
        products = [Ultra.coerce(a) * Ultra.unit(i) for a in row for i in indices]
        rows.extend([[p.coefficients[k] for p in products] for k in range(8)])
        values.extend(Ultra.coerce(b).coefficients)
    result = real_solution(rows, values, rtol=rtol)

    def decode(coefficients: tuple[float, ...]) -> tuple[Ultra, ...]:
        return tuple(
            sum(
                (
                    Ultra.unit(index) * coefficients[col * len(indices) + k]
                    for k, index in enumerate(indices)
                ),
                Ultra(),
            )
            for col in range(n)
        )

    return LinearSolution(decode(result.particular), tuple(decode(v) for v in result.basis))


def _solve_complex(a: list[list[complex]], b: list[complex], rtol: float) -> list[complex]:
    n = len(b)
    rows = [row.copy() + [rhs] for row, rhs in zip(a, b, strict=True)]
    scales = [max(map(abs, row)) for row in a]
    if any(scale == 0 for scale in scales):
        raise SingularSystemError("Zero row in body matrix")
    for col in range(n):
        pivot = max(range(col, n), key=lambda r: abs(rows[r][col]) / scales[r])
        if abs(rows[pivot][col]) <= rtol * scales[pivot]:
            raise SingularSystemError(f"Body matrix singular at column {col}; rtol={rtol}")
        rows[col], rows[pivot] = rows[pivot], rows[col]
        scales[col], scales[pivot] = scales[pivot], scales[col]
        for row in range(col + 1, n):
            ratio = rows[row][col] / rows[col][col]
            rows[row][col] = 0j
            for k in range(col + 1, n + 1):
                rows[row][k] = _finite(rows[row][k] - ratio * rows[col][k])
    result = [0j] * n
    for row in reversed(range(n)):
        residual = rows[row][n] - sum(rows[row][k] * result[k] for k in range(row + 1, n))
        result[row] = _finite(residual / rows[row][row])
    return result


def solve(
    matrix: Sequence[Sequence[Scalar]], rhs: Sequence[Scalar], *, rtol: float = 1e-12
) -> tuple[Ultra, ...]:
    """Solve A*x=b for a nonempty square matrix with invertible body channels.

    Scaled partial pivoting happens separately in each complex channel. Thus a
    matrix may be invertible even if every individual entry is a zero divisor.
    Singular/underdetermined and rectangular systems are not handled here.
    """
    if not math.isfinite(rtol) or rtol < 0:
        raise ValueError("rtol must be finite and nonnegative")
    n = len(rhs)
    if n == 0 or len(matrix) != n or any(len(row) != n for row in matrix):
        raise ValueError("Expected a nonempty square matrix and matching right-hand side")
    a = [[Ultra.coerce(value).channels() for value in row] for row in matrix]
    b = [Ultra.coerce(value).channels() for value in rhs]
    solutions: list[list[Channel]] = []
    for channel in range(2):
        body = [[value[channel][0] for value in row] for row in a]
        tangent = [[value[channel][1] for value in row] for row in a]
        try:
            x = _solve_complex(body, [value[channel][0] for value in b], rtol)
            residual = [
                value[channel][1] - sum(t * z for t, z in zip(row, x, strict=True))
                for value, row in zip(b, tangent, strict=True)
            ]
            dx = _solve_complex(body, residual, rtol)
        except SingularSystemError as error:
            raise SingularSystemError(f"{'+' if channel == 0 else '-'} channel: {error}") from error
        solutions.append(list(zip(x, dx, strict=True)))
    return tuple(Ultra.from_channels(p, m) for p, m in zip(*solutions, strict=True))
