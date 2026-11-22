"""Exact coefficient polynomials and Hermite interpolation over the unified algebra."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from .exact import QONE, QZERO, ExactScalar, ExactUltra, Rational, rational
from .exact_linalg import exact_solve


@dataclass(frozen=True, init=False)
class ExactPolynomial:
    """Power-basis coefficients in ascending order, normalized by exact zeros."""

    coefficients: tuple[ExactUltra, ...]

    def __init__(self, coefficients: Sequence[ExactScalar]) -> None:
        values = [ExactUltra.coerce(x) for x in coefficients]
        if not values:
            values = [QZERO]
        while len(values) > 1 and not values[-1]:
            values.pop()
        object.__setattr__(self, "coefficients", tuple(values))

    @property
    def degree(self) -> int:
        return len(self.coefficients) - 1 if any(self.coefficients) else -1

    def __call__(self, value: ExactScalar) -> ExactUltra:
        x, result = ExactUltra.coerce(value), QZERO
        for c in reversed(self.coefficients):
            result = result * x + c
        return result

    def __add__(self, other: ExactPolynomial) -> ExactPolynomial:
        n = max(len(self.coefficients), len(other.coefficients))
        a = self.coefficients + (QZERO,) * (n - len(self.coefficients))
        b = other.coefficients + (QZERO,) * (n - len(other.coefficients))
        return ExactPolynomial([x + y for x, y in zip(a, b, strict=True)])

    def __neg__(self) -> ExactPolynomial:
        return ExactPolynomial([-c for c in self.coefficients])

    def __sub__(self, other: ExactPolynomial) -> ExactPolynomial:
        return self + -other

    def __mul__(self, other: ExactPolynomial | ExactScalar) -> ExactPolynomial:
        if not isinstance(other, ExactPolynomial):
            return ExactPolynomial([c * ExactUltra.coerce(other) for c in self.coefficients])
        result = [QZERO] * (len(self.coefficients) + len(other.coefficients) - 1)
        for i, a in enumerate(self.coefficients):
            for j, b in enumerate(other.coefficients):
                result[i + j] = result[i + j] + a * b
        return ExactPolynomial(result)

    __rmul__ = __mul__

    def derivative(self, order: int = 1) -> ExactPolynomial:
        if type(order) is not int or order < 0:
            raise ValueError("Derivative order must be a nonnegative integer")
        result = self
        for _ in range(min(order, len(self.coefficients))):
            result = ExactPolynomial([i * c for i, c in enumerate(result.coefficients) if i])
        return result

    def integral(self, constant: ExactScalar = 0) -> ExactPolynomial:
        return ExactPolynomial(
            [ExactUltra.coerce(constant), *(c / (i + 1) for i, c in enumerate(self.coefficients))]
        )

    def __divmod__(self, divisor: ExactPolynomial) -> tuple[ExactPolynomial, ExactPolynomial]:
        if divisor.degree < 0:
            raise ZeroDivisionError("Zero polynomial divisor")
        inv = divisor.coefficients[-1].inverse()
        remainder = list(self.coefficients)
        quotient = [QZERO] * max(1, self.degree - divisor.degree + 1)
        while len(remainder) >= len(divisor.coefficients) and any(remainder):
            power = len(remainder) - len(divisor.coefficients)
            coefficient = remainder[-1] * inv
            quotient[power] = coefficient
            for i, c in enumerate(divisor.coefficients):
                remainder[i + power] = remainder[i + power] - coefficient * c
            while len(remainder) > 1 and not remainder[-1]:
                remainder.pop()
        return ExactPolynomial(quotient), ExactPolynomial(remainder)

    @classmethod
    def interpolate(
        cls, nodes: Sequence[Rational], values: Sequence[ExactScalar]
    ) -> ExactPolynomial:
        xs = tuple(rational(x) for x in nodes)
        if not xs or len(xs) != len(values) or len(set(xs)) != len(xs):
            raise ValueError("Distinct rational nodes and matching values are required")
        divided = [ExactUltra.coerce(y) for y in values]
        for order in range(1, len(xs)):
            for i in range(len(xs) - 1, order - 1, -1):
                divided[i] = (divided[i] - divided[i - 1]) / (xs[i] - xs[i - order])
        result, product = cls([QZERO]), cls([QONE])
        for x, c in zip(xs, divided, strict=True):
            result = result + product * c
            product = product * cls([-x, 1])
        return result

    @classmethod
    def hermite(
        cls,
        nodes: Sequence[Rational],
        values: Sequence[ExactScalar],
        derivatives: Sequence[ExactScalar],
    ) -> ExactPolynomial:
        xs = tuple(rational(x) for x in nodes)
        if (
            not xs
            or len(xs) != len(values)
            or len(xs) != len(derivatives)
            or len(set(xs)) != len(xs)
        ):
            raise ValueError("Distinct nodes with one value and derivative each are required")
        n = 2 * len(xs)
        matrix: list[list[ExactScalar]] = []
        rhs: list[ExactScalar] = []
        for x, y, dy in zip(xs, values, derivatives, strict=True):
            matrix.append([x**k for k in range(n)])
            matrix.append([0, *(k * x ** (k - 1) for k in range(1, n))])
            rhs.extend((y, dy))
        return cls(exact_solve(matrix, rhs))
