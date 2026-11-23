"""Coupled and projective geometry over the complete unified algebra.

Both ExactUltra and Ultra are supported, with no implicit domain conversion.
These are operators ON algebra values; their noncommutative composition does
not change the commutative multiplication of the scalar algebra itself.
"""

from __future__ import annotations

import math
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from typing import Literal, overload

from .core import NonFiniteError, NonInvertibleError, Ultra
from .exact import ExactChannel, ExactComplex, ExactUltra


def _same_domain(*values: Ultra | ExactUltra) -> None:
    if not values or type(values[0]) not in (Ultra, ExactUltra):
        raise TypeError("Use Ultra or ExactUltra coefficients explicitly")
    if any(type(v) is not type(values[0]) for v in values):
        raise TypeError("Transformation coefficients must share their coefficient domain")


@dataclass(frozen=True)
class ModeOperator[N: (Ultra, ExactUltra)]:
    """T(x)=alpha*x+beta*conj_j(x), closed under composition.

    This represents all 2x2 matrices over the complex-dual subalgebra. It adds
    mixing of the two split modes while retaining phase and sensitivities.
    """

    alpha: N
    beta: N

    def __post_init__(self) -> None:
        _same_domain(self.alpha, self.beta)

    def apply(self, value: N) -> N:
        _same_domain(self.alpha, value)
        return self.alpha * value + self.beta * value.conjugate("j")

    __call__ = apply

    def __matmul__(self, other: ModeOperator[N]) -> ModeOperator[N]:
        _same_domain(self.alpha, other.alpha)
        return ModeOperator(
            self.alpha * other.alpha + self.beta * other.beta.conjugate("j"),
            self.alpha * other.beta + self.beta * other.alpha.conjugate("j"),
        )

    def __add__(self, other: ModeOperator[N]) -> ModeOperator[N]:
        _same_domain(self.alpha, other.alpha)
        return ModeOperator(self.alpha + other.alpha, self.beta + other.beta)

    def __neg__(self) -> ModeOperator[N]:
        return ModeOperator(-self.alpha, -self.beta)

    def __sub__(self, other: ModeOperator[N]) -> ModeOperator[N]:
        return self + -other

    def scaled(self, scalar: N) -> ModeOperator[N]:
        """Left multiplication of the output by an algebra value."""
        _same_domain(self.alpha, scalar)
        return ModeOperator(scalar * self.alpha, scalar * self.beta)

    def cayley(self, step: N) -> ModeOperator[N]:
        """(Id + step*T) @ inverse(Id - step*T), with a central step.

        Exact inputs keep the entire rational map and its epsilon derivative
        exact. The denominator must be invertible. No square root of the
        generator's quadratic form is needed at the parabolic transition.
        """
        _same_domain(self.alpha, step)
        if step.conjugate("j") != step:
            raise ValueError("Cayley step must belong to the central complex-dual subalgebra")
        identity = ModeOperator(type(self.alpha)(1), type(self.alpha)(0))
        increment = self.scaled(step)
        return (identity + increment) @ (identity - increment).inverse()

    def flow(self: ModeOperator[Ultra], time: float = 1.0) -> ModeOperator[Ultra]:
        """exp(time*A) for a constant complex-dual two-mode generator.

        Scale the time step before evaluating the entire centered series, then
        square the full map. The epsilon part differentiates every operation,
        including at a repeated eigenvalue.
        """
        if type(self.alpha) is not Ultra:
            raise TypeError("Continuous flows require numerical Ultra coefficients")
        if isinstance(time, bool) or not isinstance(time, (int, float)) or not math.isfinite(time):
            raise ValueError("time must be a finite real number")
        identity = ModeOperator(Ultra(1), Ultra())
        if time == 0:
            return identity
        size = max(abs(x) for v in (self.alpha, self.beta) for x in v.coefficients[:4])
        # A channel matrix entry combines at most four real body coefficients.
        squarings = max(0, math.frexp(size)[1] + math.frexp(abs(time))[1] + 3) if size else 0
        step = self.scaled(Ultra(math.ldexp(time, -squarings)))
        (a, b), (c, d) = step.matrix()
        mu, offset = (a + d) * 0.5, (a - d) * 0.5
        delta = offset * offset + b * c
        centered = step - identity.scaled(mu)
        # Horner forms for cosh(sqrt(delta)) and sinh(sqrt(delta))/sqrt(delta).
        # With the scaled body |delta| <= 1, the omitted body term is <= 1/34!;
        # the differentiated tail is bounded by its differentiated scalar series.
        even = odd = Ultra(1)
        for k in range(16, 0, -1):
            even = 1 + delta * (even / ((2 * k) * (2 * k - 1)))
            odd = 1 + delta * (odd / ((2 * k) * (2 * k + 1)))
        result = (identity.scaled(even) + centered.scaled(odd)).scaled(mu.exp())
        for _ in range(squarings):
            result = result @ result
        return result

    def determinant(self) -> N:
        """The 2x2 determinant, embedded without a j component."""
        return self.alpha * self.alpha.conjugate("j") - self.beta * self.beta.conjugate("j")

    def inverse(self) -> ModeOperator[N]:
        determinant = self.determinant()
        return ModeOperator(self.alpha.conjugate("j") / determinant, -self.beta / determinant)

    def __pow__(self, exponent: int) -> ModeOperator[N]:
        if type(exponent) is not int:
            raise TypeError("Operator powers require an integer")
        factor = self if exponent >= 0 else self.inverse()
        result = ModeOperator(type(self.alpha)(1), type(self.alpha)(0))
        n = abs(exponent)
        while n:
            if n & 1:
                result = result @ factor
            n >>= 1
            if n:
                factor = factor @ factor
        return result

    @classmethod
    def from_matrix(cls, a: N, b: N, c: N, d: N) -> ModeOperator[N]:
        """a,b,c,d are row-major and must belong to the complex-dual subalgebra."""
        _same_domain(a, b, c, d)
        if any(v.conjugate("j") != v for v in (a, b, c, d)):
            raise ValueError("Matrix entries must not contain j, ij, eps*j or eps*ij")
        one, j = type(a)(1), type(a).unit(1)
        plus, minus = (one + j) / 2, (one - j) / 2
        return cls(a * plus + d * minus, b * plus + c * minus)

    def matrix(self) -> tuple[tuple[N, N], tuple[N, N]]:
        j = type(self.alpha).unit(1)
        a0 = (self.alpha + self.alpha.conjugate("j")) / 2
        a1 = j * (self.alpha - self.alpha.conjugate("j")) / 2
        b0 = (self.beta + self.beta.conjugate("j")) / 2
        b1 = j * (self.beta - self.beta.conjugate("j")) / 2
        return ((a0 + a1, b0 + b1), (b0 - b1, a0 - a1))


def _vanishing_bodies(value: Ultra | ExactUltra) -> tuple[bool, bool]:
    # Check each channel for an exact zero without evaluating a potentially
    # overflowing sum or involving its tangent.
    return (
        (value.real, value.i) == (-value.j, -value.ij),
        (value.real, value.i) == (value.j, value.ij),
    )


@dataclass(frozen=True)
class ProjectivePoint[N: (Ultra, ExactUltra)]:
    """Unimodular homogeneous pair [x:y] over the algebra.

    Each complex body channel must have at least one nonzero coordinate.
    Merely requiring (x,y) != (0,0) would admit invalid ring-projective points.
    """

    x: N
    y: N

    def __post_init__(self) -> None:
        _same_domain(self.x, self.y)
        if any(
            a and b
            for a, b in zip(_vanishing_bodies(self.x), _vanishing_bodies(self.y), strict=True)
        ):
            raise ValueError("Homogeneous coordinates must be unimodular in every body channel")

    def affine(self) -> N:
        """x/y in this affine chart; a nonunit y is a chart boundary, not NaN."""
        return self.x / self.y

    @property
    def charts(self) -> tuple[str, str]:
        """Per split mode: 'y' permits x/y, otherwise 'x' permits y/x."""
        p, m = _vanishing_bodies(self.y)
        return ("x" if p else "y", "x" if m else "y")

    def equivalent(
        self, other: ProjectivePoint[N], *, rel_tol: float = 1e-9, abs_tol: float = 1e-12
    ) -> bool:
        _same_domain(self.x, other.x)
        determinant = self.x * other.y - self.y * other.x
        if isinstance(determinant, ExactUltra):
            return not determinant
        return (self.x * other.y).isclose(self.y * other.x, rel_tol=rel_tol, abs_tol=abs_tol)


type Chart = Literal["x", "y"]


@dataclass(frozen=True, slots=True)
class ChartCoordinate[C: (complex, ExactComplex)]:
    """A single split channel in the chart named for its denominator."""

    chart: Chart
    value: C
    tangent: C

    def approximate(self: ChartCoordinate[ExactComplex]) -> ChartCoordinate[complex]:
        try:
            return ChartCoordinate(
                self.chart,
                complex(self.value.real, self.value.imag),
                complex(self.tangent.real, self.tangent.imag),
            )
        except OverflowError as error:
            raise NonFiniteError("Projective coordinate exceeds binary64") from error


def _chart_coordinate(
    x: ExactChannel, y: ExactChannel, previous: Chart | None
) -> ChartCoordinate[ExactComplex]:
    nx, ny = x[0].determinant, y[0].determinant
    # Compare squared magnitudes. Switch at a factor of two; an initial tie prefers y.
    if previous == "x":
        use_x = 4 * nx > ny
    elif previous == "y":
        use_x = nx >= 4 * ny
    else:
        use_x = nx > ny
    chart: Chart = "x" if use_x else "y"
    (a, da), (b, db) = (y, x) if use_x else (x, y)
    value = a / b
    return ChartCoordinate(chart, value, (da - value * db) / b)


@overload
def projective_path(
    points: Iterable[ProjectivePoint[Ultra]],
) -> Iterator[tuple[ChartCoordinate[complex], ChartCoordinate[complex]]]: ...
@overload
def projective_path(
    points: Iterable[ProjectivePoint[ExactUltra]],
) -> Iterator[tuple[ChartCoordinate[ExactComplex], ChartCoordinate[ExactComplex]]]: ...


def projective_path(
    points: Iterable[ProjectivePoint[Ultra] | ProjectivePoint[ExactUltra]],
) -> Iterator[
    tuple[ChartCoordinate[complex], ChartCoordinate[complex]]
    | tuple[ChartCoordinate[ExactComplex], ChartCoordinate[ExactComplex]]
]:
    """Yield (+, −) chart coordinates and their input epsilon tangents at each sample.

    The first sample chooses the larger body denominator in each channel. A
    subsequent sample switches when the other denominator is at least twice as
    large. Coordinates in adjacent charts are reciprocals on their overlap.
    """
    previous_plus: Chart | None = None
    previous_minus: Chart | None = None
    domain = None
    for point in points:
        if domain is not None and type(point.x) is not domain:
            raise TypeError("A projective path must use one coefficient domain")
        domain = type(point.x)
        x = ExactUltra.from_approximate(point.x) if isinstance(point.x, Ultra) else point.x
        y = ExactUltra.from_approximate(point.y) if isinstance(point.y, Ultra) else point.y
        xp, xm = x.channels()
        yp, ym = y.channels()
        plus = _chart_coordinate(xp, yp, previous_plus)
        minus = _chart_coordinate(xm, ym, previous_minus)
        previous_plus, previous_minus = plus.chart, minus.chart
        if isinstance(point.x, Ultra):
            yield plus.approximate(), minus.approximate()
        else:
            yield plus, minus


@dataclass(frozen=True)
class Mobius[N: (Ultra, ExactUltra)]:
    """Invertible fractional-linear map z -> (a*z+b)/(c*z+d)."""

    a: N
    b: N
    c: N
    d: N

    def __post_init__(self) -> None:
        _same_domain(self.a, self.b, self.c, self.d)
        if not self.determinant().is_invertible:
            raise NonInvertibleError("A projective automorphism needs a unit determinant")

    def determinant(self) -> N:
        return self.a * self.d - self.b * self.c

    def apply(self, value: N) -> N:
        _same_domain(self.a, value)
        return (self.a * value + self.b) / (self.c * value + self.d)

    __call__ = apply

    def apply_projective(self, point: ProjectivePoint[N]) -> ProjectivePoint[N]:
        _same_domain(self.a, point.x)
        return ProjectivePoint(
            self.a * point.x + self.b * point.y, self.c * point.x + self.d * point.y
        )

    def __matmul__(self, other: Mobius[N]) -> Mobius[N]:
        _same_domain(self.a, other.a)
        return Mobius(
            self.a * other.a + self.b * other.c,
            self.a * other.b + self.b * other.d,
            self.c * other.a + self.d * other.c,
            self.c * other.b + self.d * other.d,
        )

    def inverse(self) -> Mobius[N]:
        # A common unit factor does not affect a projective transformation.
        return Mobius(self.d, -self.b, -self.c, self.a)


def cross_ratio[N: (Ultra, ExactUltra)](a: N, b: N, c: N, d: N) -> N:
    """(a-c)(b-d)/((a-d)(b-c)), requiring a unit denominator."""
    _same_domain(a, b, c, d)
    return ((a - c) * (b - d)) / ((a - d) * (b - c))
