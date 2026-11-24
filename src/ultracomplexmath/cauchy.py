"""Polynomial Cauchy data for the three quadratic planes."""

from dataclasses import dataclass, field
from fractions import Fraction

from .exact import Rational
from .exact_polynomial import ExactPolynomial
from .plane_geometry import QuadraticPlane


@dataclass(frozen=True, slots=True)
class PolynomialCauchyField:
    """Exact solution of U_yy = s U_xx with U(x,0)=trace and U_y(x,0)=normal."""

    plane: QuadraticPlane
    trace: ExactPolynomial
    normal: ExactPolynomial
    _primitive: ExactPolynomial = field(init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        for polynomial in (self.trace, self.normal):
            if any(any(c.coefficients[1:]) for c in polynomial.coefficients):
                raise ValueError("The two Cauchy polynomials must have real rational coefficients")
        object.__setattr__(self, "_primitive", self.normal.integral())

    def __call__(self, x: Rational, y: Rational) -> Fraction:
        point = self.plane.exact(x, y)
        z = point.to_ultra()
        return self.trace(z).real + self._primitive(z).coefficients[point.unit_index]
