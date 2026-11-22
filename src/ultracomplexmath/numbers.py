"""Closed two-dimensional algebras, Euclidean geometry, branches and roots.

Arithmetic between different algebras requires explicit reinterpretation or
embedding into Ultra. Values are immutable; ``with_coefficients`` replaces
the Java setters. ``roots`` includes a family for infinitely many dual roots.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from fractions import Fraction
from typing import ClassVar, Self

from .coordinates import Cartesian2D, Polar2D, wrap_angle
from .core import DomainError, Ultra


@dataclass(frozen=True)
class Hypercomplex:
    real: float = 0.0
    imag: float = 0.0
    square: ClassVar[int] = -1
    unit_index: ClassVar[int] = 2
    symbol: ClassVar[str] = "i"

    def __post_init__(self) -> None:
        if any(
            isinstance(x, bool) or not isinstance(x, (int, float)) for x in (self.real, self.imag)
        ):
            raise TypeError("Coefficients must be real int or float values")
        if not all(map(math.isfinite, (self.real, self.imag))):
            raise ValueError("Coefficients must be finite")

    @classmethod
    def from_polar(cls, radius: float, angle: float) -> Self:
        c = Polar2D(radius, angle).cartesian
        return cls(c.x, c.y)

    @classmethod
    def reinterpret(cls, value: Hypercomplex) -> Self:
        return cls(value.real, value.imag)

    @classmethod
    def from_ultra(cls, value: Ultra, *, tolerance: float = 1e-12) -> Self:
        if any(abs(c) > tolerance for k, c in enumerate(value) if k not in (0, cls.unit_index)):
            raise DomainError(f"Result is outside {cls.__name__}")
        return cls(value.real, value.coefficients[cls.unit_index])

    @classmethod
    def parse(cls, source: str) -> Self:
        from .expressions import Calculation

        return cls.from_ultra(Calculation(source).result())

    def to_ultra(self) -> Ultra:
        return Ultra(self.real) + Ultra.unit(self.unit_index) * self.imag

    def with_coefficients(self, *, real: float | None = None, imag: float | None = None) -> Self:
        return type(self)(self.real if real is None else real, self.imag if imag is None else imag)

    @property
    def cartesian(self) -> Cartesian2D:
        return Cartesian2D(self.real, self.imag)

    @property
    def polar(self) -> Polar2D:
        return self.cartesian.polar

    @property
    def length(self) -> float:
        return math.hypot(self.real, self.imag)

    @property
    def angle(self) -> float:
        return math.atan2(self.imag, self.real)

    @property
    def determinant(self) -> float:
        return (
            self.real * self.real
            if self.square == 0
            else self.real * self.real - self.square * self.imag * self.imag
        )

    @property
    def euler_length(self) -> float:
        return math.sqrt(abs(self.determinant))

    @property
    def euler_angle(self) -> float:
        return self.angle

    def __str__(self) -> str:
        sign = "+" if self.imag >= 0 else "-"
        return f"({self.real!r}{sign}{abs(self.imag)!r}*{self.symbol})"

    @property
    def is_real(self) -> bool:
        return self.imag == 0

    @property
    def is_real_integer(self) -> bool:
        return self.is_real and float(self.real).is_integer()

    def __float__(self) -> float:
        if not self.is_real:
            raise TypeError("Cannot convert a nonreal number to float")
        return float(self.real)

    def __complex__(self) -> complex:
        if self.square != -1 and self.imag:
            raise TypeError("Split and dual units are not the complex unit")
        return complex(self.real, self.imag)

    def __abs__(self) -> float:
        return self.length

    def __bool__(self) -> bool:
        return bool(self.real or self.imag)

    def _coerce(self, other: Hypercomplex | float) -> Self:
        if isinstance(other, bool):
            raise TypeError("Boolean values are not algebra scalars")
        if isinstance(other, (int, float)):
            return type(self)(other)
        if type(other) is not type(self):
            raise TypeError("Use reinterpret() or to_ultra() to combine different algebras")
        return type(self)(other.real, other.imag)

    def __add__(self, other: Hypercomplex | float) -> Self:
        v = self._coerce(other)
        return type(self)(self.real + v.real, self.imag + v.imag)

    __radd__ = __add__

    def __neg__(self) -> Self:
        return type(self)(-self.real, -self.imag)

    def __sub__(self, other: Hypercomplex | float) -> Self:
        return self + -self._coerce(other)

    def __rsub__(self, other: Hypercomplex | float) -> Self:
        return -self + other

    def __mul__(self, other: Hypercomplex | float) -> Self:
        v = self._coerce(other)
        return type(self)(
            self.real * v.real + self.square * self.imag * v.imag,
            self.real * v.imag + self.imag * v.real,
        )

    __rmul__ = __mul__

    def conjugate(self) -> Self:
        return type(self)(self.real, -self.imag)

    def inverse(self) -> Self:
        return type(self).from_ultra(self.to_ultra().inverse())

    def __truediv__(self, other: Hypercomplex | float) -> Self:
        return type(self).from_ultra(self.to_ultra() / self._coerce(other).to_ultra())

    def __rtruediv__(self, other: Hypercomplex | float) -> Self:
        return self._coerce(other) / self

    def __pow__(self, exponent: Hypercomplex | float) -> Self:
        if type(exponent) is int:
            return type(self).from_ultra(self.to_ultra() ** exponent)
        v = self._coerce(exponent)
        return type(self).from_ultra(self.to_ultra() ** v.to_ultra())

    def __rpow__(self, base: Hypercomplex | float) -> Self:
        return self._coerce(base) ** self

    def power(self, exponent: Hypercomplex | float, *, branch: int = 0) -> Self:
        if type(branch) is not int:
            raise TypeError("Logarithm branch must be an integer")
        if branch and self.square != -1:
            raise DomainError("Real split/dual logarithms have no integer branches")
        # Integer powers are independent of the complex logarithm branch and
        # remain defined at zero without taking its logarithm.
        if type(exponent) is int or isinstance(exponent, float) and exponent.is_integer():
            return self**exponent
        return (self.log(branch=branch) * exponent).exp()

    def isclose(
        self, other: Hypercomplex | float, *, rel_tol: float = 1e-10, abs_tol: float = 1e-12
    ) -> bool:
        v = self._coerce(other)
        return all(
            math.isclose(a, b, rel_tol=rel_tol, abs_tol=abs_tol)
            for a, b in ((self.real, v.real), (self.imag, v.imag))
        )

    def _function(self, name: str) -> Self:
        result: Ultra = getattr(self.to_ultra(), name)()
        return type(self).from_ultra(result)

    def exp(self) -> Self:
        return self._function("exp")

    def sqrt(self) -> Self:
        return self._function("sqrt")

    def sin(self) -> Self:
        return self._function("sin")

    def cos(self) -> Self:
        return self._function("cos")

    def tan(self) -> Self:
        return self._function("tan")

    def cot(self) -> Self:
        return self._function("cot")

    def sec(self) -> Self:
        return self._function("sec")

    def csc(self) -> Self:
        return self._function("csc")

    def sinh(self) -> Self:
        return self._function("sinh")

    def cosh(self) -> Self:
        return self._function("cosh")

    def tanh(self) -> Self:
        return self._function("tanh")

    def coth(self) -> Self:
        return self._function("coth")

    def sech(self) -> Self:
        return self._function("sech")

    def csch(self) -> Self:
        return self._function("csch")

    def asin(self) -> Self:
        return self._function("asin")

    def acos(self) -> Self:
        return self._function("acos")

    def atan(self) -> Self:
        return self._function("atan")

    def acot(self) -> Self:
        return self._function("acot")

    def asec(self) -> Self:
        return self._function("asec")

    def acsc(self) -> Self:
        return self._function("acsc")

    def asinh(self) -> Self:
        return self._function("asinh")

    def acosh(self) -> Self:
        return self._function("acosh")

    def atanh(self) -> Self:
        return self._function("atanh")

    def acoth(self) -> Self:
        return self._function("acoth")

    def asech(self) -> Self:
        return self._function("asech")

    def acsch(self) -> Self:
        return self._function("acsch")

    def log(self, base: Hypercomplex | float | None = None, *, branch: int = 0) -> Self:
        if branch and self.square != -1:
            raise DomainError("Real split/dual logarithms have no integer branches")
        result = type(self).from_ultra(self.to_ultra().log(branches=(branch, branch)))
        return result if base is None else result / self._coerce(base).log()

    ln = log

    def roots(self, degree: int) -> RootSet:
        if type(degree) is not int or degree <= 0:
            raise ValueError("Root degree must be a positive integer")
        if degree == 1:
            return RootSet((self,))
        if self.square == -1:
            if not self:
                return RootSet((type(self)(),))
            return RootSet(
                tuple(
                    type(self).from_polar(
                        self.length ** (1 / degree), (self.angle + math.tau * k) / degree
                    )
                    for k in range(degree)
                )
            )

        def real_roots(value: float) -> tuple[float, ...]:
            if value == 0:
                return (0.0,)
            if degree % 2:
                return (math.copysign(abs(value) ** (1 / degree), value),)
            if value < 0:
                return ()
            root = value ** (1 / degree)
            return (root, -root)

        if self.square == 1:
            return RootSet(
                tuple(
                    type(self)((p + m) / 2, (p - m) / 2)
                    for p in real_roots(self.real + self.imag)
                    for m in real_roots(self.real - self.imag)
                )
            )
        if self.real == 0:
            return RootSet((), Dual(0, 1) if self.imag == 0 else None)
        return RootSet(
            tuple(
                type(self)(r, self.imag / (degree * r ** (degree - 1)))
                for r in real_roots(self.real)
            )
        )

    def rational_power(self, numerator: int, denominator: int) -> RootSet:
        fraction = Fraction(numerator, denominator)
        return (self**fraction.numerator).roots(fraction.denominator)

    def is_log_of(self, value: Hypercomplex, base: Hypercomplex | float = math.e) -> bool:
        return (self._coerce(base).log() * self).exp().isclose(value)

    def is_root_of(self, value: Hypercomplex, degree: int) -> bool:
        return (self**degree).isclose(value)

    def is_power_of(
        self, base: Hypercomplex, exponent: Hypercomplex | float, *, branch: int = 0
    ) -> bool:
        return self.isclose(base.power(exponent, branch=branch))

    def dot(self, other: Hypercomplex) -> float:
        return self.real * other.real + self.imag * other.imag

    def normalized(self) -> Self:
        from .geometry import unit

        x, y = unit((self.real, self.imag))
        return type(self)(x, y)

    def r(self, exponent: float) -> Self:
        magnitude: float = self.length**exponent
        return self.normalized() * magnitude

    def turned_by(self, angle: float) -> Self:
        return type(self).from_polar(self.length, self.angle + angle)

    def angle_to(self, other: Hypercomplex) -> float:
        return wrap_angle(self.angle - other.angle)

    def points_towards(self, other: Hypercomplex) -> bool:
        return self.dot(other) > 0

    def part_in_direction(self, other: Hypercomplex) -> Self:
        from .geometry import project

        x, y = project((self.real, self.imag), (other.real, other.imag))
        return type(self)(x, y)

    def part_orthogonal_to(self, other: Hypercomplex) -> Self:
        return self - self.part_in_direction(other)

    def mirrored_radial_to(self, other: Hypercomplex) -> Self:
        return self - 2 * self.part_in_direction(other)

    def mirrored_orthogonal_to(self, other: Hypercomplex) -> Self:
        return 2 * self.part_in_direction(other) - self

    def hilbert(self, other: Hypercomplex) -> tuple[Self, Self]:
        axis = self.normalized()
        return axis, type(self).reinterpret(other).part_orthogonal_to(axis).normalized()

    def color(self) -> tuple[int, int, int]:
        intensity = 51 + 204 / math.log(10 * self.length + math.e)
        spread = min(255 - intensity, intensity - 51)
        channels = tuple(
            max(
                0,
                min(
                    255,
                    math.floor(intensity + (math.cos(self.angle + shift) + 1) / 2 * spread + 0.5),
                ),
            )
            for shift in (0, math.tau / 3, -math.tau / 3)
        )
        return channels[0], channels[1], channels[2]


class Complex(Hypercomplex):
    """i² = -1; principal branches agree with the Ultra embedding."""


class Binary(Hypercomplex):
    """Split-complex numbers j² = 1, including all four hyperbolic sectors."""

    square = 1
    unit_index = 1
    symbol = "j"

    @property
    def diagonal(self) -> tuple[float, float]:
        return self.real - self.imag, self.real + self.imag

    @classmethod
    def from_diagonal(cls, lower: float, upper: float) -> Binary:
        return cls((lower + upper) / 2, (upper - lower) / 2)

    @property
    def range_from(self) -> float:
        return self.real - self.imag

    @property
    def range_to(self) -> float:
        return self.real + self.imag

    @property
    def range_base(self) -> float:
        return self.real

    @property
    def range_radius(self) -> float:
        return self.imag

    def hyperbolic_form(self) -> tuple[float, Binary, float]:
        scale = max(abs(self.real), abs(self.imag))
        if scale == 0 or abs(self.real) == abs(self.imag):
            raise DomainError("Null rays have no finite hyperbolic angle")
        direction = (
            Binary(math.copysign(1, self.real))
            if abs(self.real) > abs(self.imag)
            else Binary(0, math.copysign(1, self.imag))
        )
        a, b = self.real / scale, self.imag / scale
        norm = math.sqrt(abs(a - b)) * math.sqrt(abs(a + b))
        length = scale * norm
        parameter = math.atanh(b / a if abs(a) > abs(b) else a / b)
        return length, direction, parameter

    @property
    def euler_angle(self) -> float:
        return self.hyperbolic_form()[2]

    @property
    def euler_direction(self) -> Binary:
        return self.hyperbolic_form()[1]

    @classmethod
    def from_hyperbolic(cls, radius: float, direction: Binary, angle: float) -> Binary:
        if radius < 0 or direction not in (cls(1), cls(-1), cls(0, 1), cls(0, -1)):
            raise DomainError("Expected nonnegative radius and one of the four sector units")
        return cls(math.cosh(angle), math.sinh(angle)) * direction * radius

    null_basis = diagonal
    from_null_basis = from_diagonal


class Dual(Hypercomplex):
    """eps² = 0, useful for differentiation and oriented line geometry."""

    square = 0
    unit_index = 4
    symbol = "eps"

    @property
    def euler_length(self) -> float:
        return self.real

    @property
    def euler_angle(self) -> float:
        return self.imag / self.real

    def unit_sphere_position(self) -> tuple[float, float, float]:
        scale = 4 / (self.real**2 + self.imag**2 + 4)
        return scale * self.real, scale * self.imag, 1 - 2 * scale

    @classmethod
    def from_unit_sphere(cls, x: float, y: float, z: float) -> Dual:
        if not math.isclose(x * x + y * y + z * z, 1, abs_tol=1e-10) or z == 1:
            raise DomainError("Expected a unit-sphere point other than the north pole")
        return cls(2 * x / (1 - z), 2 * y / (1 - z))


@dataclass(frozen=True)
class RootSet:
    values: tuple[Hypercomplex, ...]
    free_direction: Hypercomplex | None = None

    def at(self, parameter: float) -> Hypercomplex:
        if self.free_direction is None:
            raise ValueError("This root set is discrete")
        return self.free_direction * parameter
