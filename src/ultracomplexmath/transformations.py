"""Coupled and projective geometry over the complete unified algebra.

Both ExactUltra and Ultra are supported, with no implicit domain conversion.
These are operators ON algebra values; their noncommutative composition does
not change the commutative multiplication of the scalar algebra itself.
"""

from __future__ import annotations

from dataclasses import dataclass

from .core import NonInvertibleError, Ultra
from .exact import ExactUltra


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
            not (a or b)
            for (a, _), (b, _) in zip(self.x.channels(), self.y.channels(), strict=True)
        ):
            raise ValueError("Homogeneous coordinates must be unimodular in every body channel")

    def affine(self) -> N:
        """x/y in this affine chart; a nonunit y is a chart boundary, not NaN."""
        return self.x / self.y

    @property
    def charts(self) -> tuple[str, str]:
        """Per split mode: 'y' permits x/y, otherwise 'x' permits y/x."""
        (p, _), (m, _) = self.y.channels()
        return ("y" if p else "x", "y" if m else "x")

    def equivalent(
        self, other: ProjectivePoint[N], *, rel_tol: float = 1e-9, abs_tol: float = 1e-12
    ) -> bool:
        _same_domain(self.x, other.x)
        determinant = self.x * other.y - self.y * other.x
        if isinstance(determinant, ExactUltra):
            return not determinant
        return (self.x * other.y).isclose(self.y * other.x, rel_tol=rel_tol, abs_tol=abs_tol)


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
