"""Circular, hyperbolic and parabolic plane geometry with explicit metrics.

For u²=s, the quadratic form is x²-s*y². Angles mean radians (s=-1),
rapidity with a sector (s=1), or shear with an orientation (s=0).
Exact constructions return rational coefficients without trigonometric calls.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from fractions import Fraction
from typing import Literal

from .core import DomainError
from .exact import ExactBinary, ExactComplex, ExactDual, ExactHypercomplex, Rational, rational
from .numbers import Binary, Complex, Dual, Hypercomplex

type PlaneKind = Literal["complex", "split", "dual"]
type PlaneNumber = Hypercomplex | ExactHypercomplex


def _same(a: PlaneNumber, b: PlaneNumber) -> None:
    if type(a) is not type(b):
        raise TypeError("Plane values must share their algebra and coefficient domain")


def metric_dot[V: (Hypercomplex, ExactHypercomplex)](a: V, b: V) -> float | Fraction:
    """The bilinear form x*x' - s*y*y', including its degenerate dual case."""
    _same(a, b)
    return a.real * b.real - a.square * a.imag * b.imag


def metric_project[V: (Hypercomplex, ExactHypercomplex)](value: V, direction: V) -> V:
    """Projection onto a non-null direction in that plane's metric."""
    _same(value, direction)
    if isinstance(value, ExactHypercomplex):
        q = direction.determinant
        if not q:
            raise DomainError("Projection onto a null direction is undefined")
        weight = (value.real * direction.real - value.square * value.imag * direction.imag) / q
        return direction * weight
    # Scaling avoids squaring a tiny or very large direction.
    scale = max(abs(direction.real), abs(direction.imag))
    if not scale:
        raise DomainError("Projection onto zero is undefined")
    unit = type(direction)(direction.real / scale, direction.imag / scale)
    q = unit.determinant
    if not q:
        raise DomainError("Projection onto a null direction is undefined")
    return unit * ((value.real * unit.real - value.square * value.imag * unit.imag) / q)


def metric_reflect[V: (Hypercomplex, ExactHypercomplex)](value: V, normal: V) -> V:
    """Reflect in the line orthogonal to a non-null normal; origin is fixed."""
    return value - 2 * metric_project(value, normal)


@dataclass(frozen=True)
class PlanePolar:
    """Numerical polar data; a sector is indispensable outside complex geometry."""

    kind: PlaneKind
    radius: float
    parameter: float
    sector: tuple[int, int]

    def __post_init__(self) -> None:
        if not math.isfinite(self.radius) or self.radius <= 0:
            raise DomainError("Polar radius must be finite and positive")
        if not math.isfinite(self.parameter):
            raise DomainError("Polar parameter must be finite")
        allowed: tuple[tuple[int, int], ...] = (
            ((1, 0),) if self.kind == "complex" else ((1, 0), (-1, 0))
        )
        if self.kind == "split":
            allowed += ((0, 1), (0, -1))
        if self.sector not in allowed:
            raise DomainError("Invalid sector for this geometry")
        QuadraticPlane(self.kind)

    def reconstruct(self) -> Hypercomplex:
        plane = QuadraticPlane(self.kind)
        return plane.rotor(self.parameter) * plane.point(*self.sector) * self.radius


@dataclass(frozen=True)
class QuadraticPlane:
    """One construction language for all three embedded two-dimensional algebras."""

    kind: PlaneKind

    def __post_init__(self) -> None:
        if self.kind not in ("complex", "split", "dual"):
            raise ValueError("Plane kind must be complex, split or dual")

    @property
    def square(self) -> int:
        return {"complex": -1, "split": 1, "dual": 0}[self.kind]

    def point(self, x: float = 0, y: float = 0) -> Hypercomplex:
        return {"complex": Complex, "split": Binary, "dual": Dual}[self.kind](x, y)

    def exact(self, x: Rational = 0, y: Rational = 0) -> ExactHypercomplex:
        return {"complex": ExactComplex, "split": ExactBinary, "dual": ExactDual}[self.kind](x, y)

    def _check(self, value: PlaneNumber) -> None:
        if value.square != self.square:
            raise TypeError("The point belongs to a different quadratic plane")

    def quadrance(self, value: PlaneNumber) -> float | Fraction:
        self._check(value)
        return value.determinant

    def classify(self, value: PlaneNumber) -> str:
        """Geometric classification, testing nullity without floating squaring."""
        self._check(value)
        x: float | Fraction = value.real
        y: float | Fraction = value.imag
        if not x and not y:
            return "zero"
        if self.square == -1:
            return "regular"
        if self.square == 0:
            return "null" if not x else "positive" if x > 0 else "negative"
        mx, my = (x if x >= 0 else -x), (y if y >= 0 else -y)
        if mx == my:
            return "null"
        return "timelike" if mx > my else "spacelike"

    def polar(self, value: Hypercomplex) -> PlanePolar:
        """Extract numerical angle/shear and sector; exact callers approximate explicitly."""
        self._check(value)
        if isinstance(value, ExactHypercomplex):
            raise TypeError("Polar extraction is numerical; call approximate() explicitly")
        if self.classify(value) in ("zero", "null"):
            raise DomainError("Zero and null directions have no finite polar angle")
        if self.kind == "complex":
            return PlanePolar(self.kind, math.hypot(value.real, value.imag), value.angle, (1, 0))
        if self.kind == "split":
            radius, direction, angle = Binary(value.real, value.imag).hyperbolic_form()
            return PlanePolar(self.kind, radius, angle, (int(direction.real), int(direction.imag)))
        return PlanePolar(
            self.kind,
            abs(value.real),
            value.imag / value.real,
            (1 if value.real > 0 else -1, 0),
        )

    def angle_between(self, start: Hypercomplex, end: Hypercomplex) -> PlanePolar:
        """Oriented relative angle plus scale and sector, from start to end."""
        self._check(start)
        self._check(end)
        _same(start, end)
        return self.polar(end / start)

    def rotor(self, parameter: float) -> Hypercomplex:
        """exp(u*parameter): circle rotation, boost, or shear respectively."""
        if isinstance(parameter, bool) or not isinstance(parameter, (int, float)):
            raise TypeError("Numerical rotor parameter must be int or float")
        if not math.isfinite(parameter):
            raise DomainError("Rotor parameter must be finite")
        if self.kind == "complex":
            return self.point(math.cos(parameter), math.sin(parameter))
        if self.kind == "split":
            return self.point(math.cosh(parameter), math.sinh(parameter))
        return self.point(1, parameter)

    def cayley(self, parameter: Rational) -> ExactHypercomplex:
        """(1+u*t)/(1-u*t), an exact unit-quadrance factor.

        t=tan(theta/2), tanh(rapidity/2), or shear/2. The split chart
        excludes t=±1; the circular chart misses the factor -1.
        """
        t = rational(parameter)
        denominator = 1 - self.square * t * t
        if not denominator:
            raise DomainError("Cayley parameter lies on a split null boundary")
        return self.exact((1 + self.square * t * t) / denominator, 2 * t / denominator)


@dataclass(frozen=True)
class PlaneIsometry[V: (Hypercomplex, ExactHypercomplex)]:
    """z -> factor * (conj(z) if reflected else z) + translation.

    Preserves the appropriate quadratic form of point differences. In the
    degenerate dual plane this is the shear/translation/reflection subgroup,
    not every linear map preserving x².
    """

    factor: V
    translation: V
    reflected: bool = False

    def __post_init__(self) -> None:
        _same(self.factor, self.translation)
        if type(self.reflected) is not bool:
            raise TypeError("reflected must be bool")
        q = self.factor.determinant
        valid = (
            q == 1
            if isinstance(self.factor, ExactHypercomplex)
            else math.isclose(q, 1, abs_tol=1e-12)
        )
        if not valid:
            raise DomainError("An isometry factor must have unit quadrance")

    def apply(self, point: V) -> V:
        _same(self.factor, point)
        return self.factor * (point.conjugate() if self.reflected else point) + self.translation

    __call__ = apply

    def __matmul__(self, other: PlaneIsometry[V]) -> PlaneIsometry[V]:
        """Composition: (A @ B)(z) = A(B(z))."""
        _same(self.factor, other.factor)
        factor = other.factor.conjugate() if self.reflected else other.factor
        shift = other.translation.conjugate() if self.reflected else other.translation
        return PlaneIsometry(
            self.factor * factor,
            self.factor * shift + self.translation,
            self.reflected != other.reflected,
        )

    def inverse(self) -> PlaneIsometry[V]:
        inv = self.factor.inverse()
        shift = -(inv * self.translation)
        if self.reflected:
            inv, shift = inv.conjugate(), shift.conjugate()
        return PlaneIsometry(inv, shift, self.reflected)

    def homogeneous_matrix(self) -> tuple[tuple[float | Fraction, ...], ...]:
        """3x3 affine matrix on (x,y,1), retaining Fraction entries when exact."""
        a, b, s = self.factor.real, self.factor.imag, self.factor.square
        sign = -1 if self.reflected else 1
        zero, one = a * 0, a * 0 + 1
        return (
            (a, sign * s * b, self.translation.real),
            (b, sign * a, self.translation.imag),
            (zero, zero, one),
        )


CIRCULAR = QuadraticPlane("complex")
HYPERBOLIC = QuadraticPlane("split")
PARABOLIC = QuadraticPlane("dual")
