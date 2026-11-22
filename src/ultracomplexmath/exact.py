"""The same commuting algebras over Q, with no implicit float conversion.

Integer and Fraction coefficients are closed under arithmetic and division by
units. Transcendental evaluation is an explicit ``approximate()`` boundary.
"""

from __future__ import annotations

import json
import math
from collections.abc import Iterable, Iterator
from dataclasses import dataclass, fields
from fractions import Fraction
from typing import ClassVar, Literal, Self

from .core import BASIS, DomainError, NonInvertibleError, Ultra
from .numbers import Binary, Complex, Dual, Hypercomplex

type Rational = int | Fraction
type ExactScalar = ExactUltra | ExactHypercomplex | Rational
type ExactChannel = tuple[ExactComplex, ExactComplex]


def rational(value: Rational) -> Fraction:
    """Accept exact inputs only; Fraction(float) must be requested explicitly."""
    if isinstance(value, bool) or not isinstance(value, (int, Fraction)):
        raise TypeError("Exact coefficients require int or Fraction; convert floats explicitly")
    return Fraction(value)


def _rational_sqrt(value: Fraction) -> Fraction:
    if value < 0:
        raise DomainError("No real rational square root")
    a, b = math.isqrt(value.numerator), math.isqrt(value.denominator)
    if a * a != value.numerator or b * b != value.denominator:
        raise DomainError("Square root has irrational coefficients; use approximate().sqrt()")
    return Fraction(a, b)


@dataclass(frozen=True, slots=True, init=False)
class ExactHypercomplex:
    """A closed two-dimensional algebra with rational coefficients."""

    real: Fraction
    imag: Fraction
    square: ClassVar[int] = -1
    unit_index: ClassVar[int] = 2
    symbol: ClassVar[str] = "i"

    def __init__(self, real: Rational = 0, imag: Rational = 0) -> None:
        object.__setattr__(self, "real", rational(real))
        object.__setattr__(self, "imag", rational(imag))

    def _coerce(self, value: ExactHypercomplex | Rational) -> Self:
        if isinstance(value, (int, Fraction)):
            return type(self)(rational(value))
        if type(value) is not type(self):
            raise TypeError("Embed different exact algebras with to_ultra() before combining them")
        return type(self)(value.real, value.imag)

    def __bool__(self) -> bool:
        return bool(self.real or self.imag)

    def __str__(self) -> str:
        return f"({self.real}+({self.imag})*{self.symbol})"

    def __neg__(self) -> Self:
        return type(self)(-self.real, -self.imag)

    def __pos__(self) -> Self:
        return self

    def __add__(self, other: ExactHypercomplex | Rational) -> Self:
        if isinstance(other, ExactUltra):
            return NotImplemented
        v = self._coerce(other)
        return type(self)(self.real + v.real, self.imag + v.imag)

    __radd__ = __add__

    def __sub__(self, other: ExactHypercomplex | Rational) -> Self:
        if isinstance(other, ExactUltra):
            return NotImplemented
        return self + -self._coerce(other)

    def __rsub__(self, other: ExactHypercomplex | Rational) -> Self:
        return self._coerce(other) - self

    def __mul__(self, other: ExactHypercomplex | Rational) -> Self:
        if isinstance(other, ExactUltra):
            return NotImplemented
        v = self._coerce(other)
        return type(self)(
            self.real * v.real + self.square * self.imag * v.imag,
            self.real * v.imag + self.imag * v.real,
        )

    __rmul__ = __mul__

    def conjugate(self) -> Self:
        return type(self)(self.real, -self.imag)

    @property
    def determinant(self) -> Fraction:
        return self.real**2 - self.square * self.imag**2

    @property
    def is_invertible(self) -> bool:
        return self.determinant != 0

    def inverse(self) -> Self:
        norm = self.determinant
        if norm == 0:
            raise NonInvertibleError("Zero quadratic form; no inverse in this exact algebra")
        return type(self)(self.real / norm, -self.imag / norm)

    def __truediv__(self, other: ExactHypercomplex | Rational) -> Self:
        if isinstance(other, ExactUltra):
            return NotImplemented
        return self * self._coerce(other).inverse()

    def __rtruediv__(self, other: ExactHypercomplex | Rational) -> Self:
        return self._coerce(other) / self

    def __pow__(self, exponent: Rational) -> Self:
        return type(self).from_ultra(self.to_ultra() ** exponent)

    def sqrt(self) -> Self:
        return type(self).from_ultra(self.to_ultra().sqrt())

    def to_ultra(self) -> ExactUltra:
        return ExactUltra(self.real) + ExactUltra.unit(self.unit_index) * self.imag

    @classmethod
    def from_ultra(cls, value: ExactUltra) -> Self:
        if any(c for k, c in enumerate(value) if k not in (0, cls.unit_index)):
            raise DomainError(f"Result is outside {cls.__name__}")
        return cls(value.real, value.coefficients[cls.unit_index])

    def approximate(self) -> Hypercomplex:
        kind = {-1: Complex, 1: Binary, 0: Dual}[self.square]
        return kind(float(self.real), float(self.imag))


class ExactComplex(ExactHypercomplex):
    """Gaussian rationals, Q[i]."""


class ExactBinary(ExactHypercomplex):
    """Split rationals with j²=1."""

    square = 1
    unit_index = 1
    symbol = "j"


class ExactDual(ExactHypercomplex):
    """Dual rationals with eps²=0."""

    square = 0
    unit_index = 4
    symbol = "eps"


@dataclass(frozen=True, slots=True, init=False)
class ExactUltra:
    """Q[i,j,eps]/(i²+1,j²-1,eps²), preserving arbitrary-size rationals.

    The coefficient order and multiplication are identical to Ultra. Exact and
    floating-point values never mix implicitly. Equality is value equality
    between ExactUltra instances; numerical approximation is explicit.
    """

    real: Fraction
    j: Fraction
    i: Fraction
    ij: Fraction
    eps: Fraction
    eps_j: Fraction
    eps_i: Fraction
    eps_ij: Fraction

    def __init__(
        self,
        real: Rational = 0,
        j: Rational = 0,
        i: Rational = 0,
        ij: Rational = 0,
        eps: Rational = 0,
        eps_j: Rational = 0,
        eps_i: Rational = 0,
        eps_ij: Rational = 0,
    ) -> None:
        values = (real, j, i, ij, eps, eps_j, eps_i, eps_ij)
        for field, value in zip(fields(self), values, strict=True):
            object.__setattr__(self, field.name, rational(value))

    @classmethod
    def coerce(cls, value: ExactScalar) -> ExactUltra:
        if isinstance(value, ExactUltra):
            return value
        if isinstance(value, ExactHypercomplex):
            return value.to_ultra()
        return cls(rational(value))

    @classmethod
    def from_coefficients(cls, values: Iterable[Rational]) -> ExactUltra:
        coefficients = tuple(values)
        if len(coefficients) != 8:
            raise ValueError("Exactly eight coefficients are required")
        return cls(*coefficients)

    @classmethod
    def unit(cls, index: int) -> ExactUltra:
        if type(index) is not int or not 0 <= index < 8:
            raise ValueError("Basis index must be an integer in 0..7")
        return cls(*(int(k == index) for k in range(8)))

    @classmethod
    def complex(cls, real: Rational = 0, imag: Rational = 0) -> ExactUltra:
        return cls(real=real, i=imag)

    @classmethod
    def split(cls, real: Rational = 0, imag: Rational = 0) -> ExactUltra:
        return cls(real=real, j=imag)

    @classmethod
    def dual(cls, real: Rational = 0, tangent: Rational = 0) -> ExactUltra:
        return cls(real=real, eps=tangent)

    @property
    def coefficients(self) -> tuple[Fraction, ...]:
        return (self.real, self.j, self.i, self.ij, self.eps, self.eps_j, self.eps_i, self.eps_ij)

    def __iter__(self) -> Iterator[Fraction]:
        return iter(self.coefficients)

    def __bool__(self) -> bool:
        return any(self)

    def __str__(self) -> str:
        return (
            " + ".join(
                f"({c})" if k == "1" else f"({c})*{k}"
                for c, k in zip(self, BASIS, strict=True)
                if c
            )
            or "0"
        )

    def __neg__(self) -> ExactUltra:
        return ExactUltra(*(-c for c in self))

    def __pos__(self) -> ExactUltra:
        return self

    def __add__(self, other: ExactScalar) -> ExactUltra:
        try:
            v = self.coerce(other)
        except TypeError:
            return NotImplemented
        return ExactUltra(*(a + b for a, b in zip(self, v, strict=True)))

    __radd__ = __add__

    def __sub__(self, other: ExactScalar) -> ExactUltra:
        return self + -self.coerce(other)

    def __rsub__(self, other: ExactScalar) -> ExactUltra:
        return self.coerce(other) - self

    def __mul__(self, other: ExactScalar) -> ExactUltra:
        try:
            v = self.coerce(other)
        except TypeError:
            return NotImplemented
        coefficients = [Fraction(0) for _ in range(8)]
        for a, x in enumerate(self):
            for b, y in enumerate(v):
                if not (a & b & 4):
                    coefficients[a ^ b] += (-1 if a & b & 2 else 1) * x * y
        return ExactUltra(*coefficients)

    __rmul__ = __mul__

    def channels(self) -> tuple[ExactChannel, ExactChannel]:
        return (
            (
                ExactComplex(self.real + self.j, self.i + self.ij),
                ExactComplex(self.eps + self.eps_j, self.eps_i + self.eps_ij),
            ),
            (
                ExactComplex(self.real - self.j, self.i - self.ij),
                ExactComplex(self.eps - self.eps_j, self.eps_i - self.eps_ij),
            ),
        )

    @classmethod
    def from_channels(cls, plus: ExactChannel, minus: ExactChannel) -> ExactUltra:
        zp, wp = plus
        zm, wm = minus
        if any(not isinstance(v, ExactComplex) for v in (zp, wp, zm, wm)):
            raise TypeError("Exact channels require ExactComplex bodies and tangents")
        a, b, c, d = (zp + zm) / 2, (zp - zm) / 2, (wp + wm) / 2, (wp - wm) / 2
        return cls(a.real, b.real, a.imag, b.imag, c.real, d.real, c.imag, d.imag)

    @property
    def is_invertible(self) -> bool:
        return all(bool(z) for z, _ in self.channels())

    def inverse(self) -> ExactUltra:
        result = []
        for z, w in self.channels():
            inv = z.inverse()
            result.append((inv, -w * inv * inv))
        return ExactUltra.from_channels(result[0], result[1])

    def __truediv__(self, other: ExactScalar) -> ExactUltra:
        return self * self.coerce(other).inverse()

    def __rtruediv__(self, other: ExactScalar) -> ExactUltra:
        return self.coerce(other) / self

    def __pow__(self, exponent: Rational) -> ExactUltra:
        value = rational(exponent)
        if value == Fraction(1, 2):
            return self.sqrt()
        if value.denominator != 1:
            raise DomainError(
                "Exact powers support integer exponents and rational square roots; use approximate() for other branches"
            )
        n = value.numerator
        factor, result = (self if n >= 0 else self.inverse()), ExactUltra(1)
        n = abs(n)
        while n:
            if n & 1:
                result = result * factor
            n >>= 1
            if n:
                factor = factor * factor
        return result

    def conjugate(self, generator: Literal["i", "j", "eps"] = "i") -> ExactUltra:
        if generator not in ("i", "j", "eps"):
            raise ValueError("Generator must be i, j or eps")
        bit = {"i": 2, "j": 1, "eps": 4}[generator]
        return ExactUltra(*(c * (-1 if k & bit else 1) for k, c in enumerate(self)))

    def determinant(self) -> Fraction:
        (p, _), (m, _) = self.channels()
        return p.determinant**2 * m.determinant**2

    def sqrt(self) -> ExactUltra:
        """Principal channel square root, if every coefficient is rational."""
        result = []
        for z, w in self.channels():
            if not z:
                if w:
                    raise DomainError("A nonzero pure tangent has no square root")
                result.append((ExactComplex(), ExactComplex()))
                continue
            radius = _rational_sqrt(z.determinant)
            a = _rational_sqrt((radius + z.real) / 2)
            b = _rational_sqrt((radius - z.real) / 2)
            root = ExactComplex(a, -b if z.imag < 0 else b)
            result.append((root, w / (2 * root)))
        return ExactUltra.from_channels(result[0], result[1])

    @property
    def primal(self) -> ExactUltra:
        return ExactUltra(*self.coefficients[:4])

    @property
    def tangent(self) -> ExactUltra:
        return ExactUltra(*self.coefficients[4:])

    def with_tangent(self, value: ExactScalar) -> ExactUltra:
        tangent = self.coerce(value)
        if any(tangent.coefficients[4:]):
            raise ValueError("A tangent seed must not itself contain epsilon")
        return self.primal + ExactUltra.unit(4) * tangent

    def abs2(self) -> ExactUltra:
        """Complex channel intensities including their exact first variations."""
        return self * self.conjugate("i")

    def real_part(self) -> ExactUltra:
        return (self + self.conjugate("i")) / 2

    def imag_part(self) -> ExactUltra:
        return (self - self.conjugate("i")) / (2 * ExactUltra.unit(2))

    def approximate(self) -> Ultra:
        return Ultra(*(float(c) for c in self))

    @classmethod
    def from_approximate(cls, value: Ultra) -> ExactUltra:
        """Capture the represented binary fractions, not guessed decimal inputs."""
        return cls(*(Fraction(c) for c in value))

    def to_json(self) -> str:
        """String numerator/denominator pairs avoid JSON integer precision loss."""
        return json.dumps(
            {
                "algebra": "Q[i,j,eps]",
                "version": 1,
                "coefficients": [[str(c.numerator), str(c.denominator)] for c in self],
            }
        )

    @classmethod
    def from_json(cls, source: str) -> ExactUltra:
        data = json.loads(source)
        if (
            not isinstance(data, dict)
            or data.get("algebra") != "Q[i,j,eps]"
            or data.get("version") != 1
        ):
            raise ValueError("Unsupported exact algebra serialization")
        coefficients = data.get("coefficients")
        if not isinstance(coefficients, list) or len(coefficients) != 8:
            raise ValueError("Expected eight rational coefficients")
        result = []
        for pair in coefficients:
            if (
                not isinstance(pair, list)
                or len(pair) != 2
                or not all(isinstance(x, str) for x in pair)
            ):
                raise ValueError("Expected string numerator/denominator pairs")
            result.append(Fraction(int(pair[0]), int(pair[1])))
        return cls(*result)


QZERO = ExactUltra()
QONE = ExactUltra(1)
QI = ExactUltra.unit(2)
QJ = ExactUltra.unit(1)
QEPS = ExactUltra.unit(4)
