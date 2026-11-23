"""Unit polar coordinates, continuous phase lifts and root families over R."""

from __future__ import annotations

import cmath
import math
from collections.abc import Iterator
from dataclasses import dataclass
from fractions import Fraction

from .core import ZERO, Channel, DomainError, Ultra
from .exact import ExactComplex, ExactUltra


def _near(angle: float, reference: float) -> float:
    return angle + math.tau * round((reference - angle) / math.tau)


def _degree(n: int) -> None:
    if type(n) is not int or n < 1:
        raise ValueError("Root degree must be a positive integer")


@dataclass(frozen=True, slots=True)
class PolarForm:
    """r exp(j*rho + i*theta + ij*phi) (1 + eps*v), with unwrapped angles."""

    r: float
    rho: float
    theta: float
    phi: float
    v: Ultra = ZERO

    def __post_init__(self) -> None:
        if not all(map(math.isfinite, (self.r, self.rho, self.theta, self.phi))) or self.r <= 0:
            raise ValueError("Polar coordinates require finite parameters and r > 0")
        if not isinstance(self.v, Ultra) or self.v.tangent:
            raise ValueError("v must be a numerical body with four real coefficients")

    @property
    def phases(self) -> tuple[float, float]:
        return self.theta + self.phi, self.theta - self.phi

    @classmethod
    def from_value(cls, value: Ultra, *, previous: PolarForm | None = None) -> PolarForm:
        (p, _), (m, _) = value.channels()
        if not p or not m:
            raise DomainError("Polar coordinates require both body channels to be nonzero")
        lp, lm = math.log(abs(p)), math.log(abs(m))
        ap, am = cmath.phase(p), cmath.phase(m)
        if previous is not None:
            ref_p, ref_m = previous.phases
            ap, am = _near(ap, ref_p), _near(am, ref_m)
            if any(
                math.isclose(abs(step), math.pi, rel_tol=0, abs_tol=4 * math.ulp(math.pi))
                for step in (ap - ref_p, am - ref_m)
            ):
                raise DomainError("Ambiguous half turn; add an intermediate path sample")

        # Recover small angle differences and relative stretches before channel
        # rounding erases them. Angles are lifted to the requested two sheets.
        scale = max(abs(x) for x in value.coefficients[:4])
        a = complex(value.real, value.i) / scale
        b = complex(value.j, value.ij) / scale
        product = a.conjugate() * b
        norm = abs(a) ** 2 + abs(b) ** 2
        ratio = 2 * product.real / norm
        rho = math.atanh(ratio) / 2 if abs(ratio) < 0.5 else (lp - lm) / 2
        phase_product = a * a - b * b
        phase_ratio = complex(abs(a) ** 2 - abs(b) ** 2, 2 * product.imag)

        def half_angle(z: complex, target: float) -> float:
            if abs(z) < 1e-8 * norm:
                return target / 2
            return _near(cmath.phase(z), target) / 2

        v = ZERO
        if value.tangent:
            v = (
                ExactUltra.from_approximate(value.tangent)
                / ExactUltra.from_approximate(value.primal)
            ).approximate()
        return cls(
            math.exp((lp + lm) / 2),
            rho,
            half_angle(phase_product, ap + am),
            half_angle(phase_ratio, ap - am),
            v,
        )

    def reconstruct(self) -> Ultra:
        body = Ultra(math.log(self.r), self.rho, self.theta, self.phi).exp()
        return body.with_tangent(body * self.v)

    def shifted(self, plus: int = 0, minus: int = 0) -> PolarForm:
        """Change the two channel arguments by integer multiples of 2*pi."""
        if type(plus) is not int or type(minus) is not int:
            raise TypeError("Both winding indices must be integers")
        return PolarForm(
            self.r,
            self.rho,
            self.theta + math.pi * (plus + minus),
            self.phi + math.pi * (plus - minus),
            self.v,
        )

    def root(self, degree: int = 2) -> Ultra:
        """Take the root on this lift; along a sampled path it remains continuous."""
        _degree(degree)
        return PolarForm(
            self.r ** (1 / degree),
            self.rho / degree,
            self.theta / degree,
            self.phi / degree,
            self.v / degree,
        ).reconstruct()

    def __mul__(self, other: PolarForm) -> PolarForm:
        if not isinstance(other, PolarForm):
            return NotImplemented
        return PolarForm(
            self.r * other.r,
            self.rho + other.rho,
            self.theta + other.theta,
            self.phi + other.phi,
            self.v + other.v,
        )


@dataclass(frozen=True, slots=True)
class UltraRoots:
    """Two independent channel equations. Sheet representatives are generated lazily."""

    value: Ultra
    degree: int

    def __post_init__(self) -> None:
        _degree(self.degree)

    @property
    def strata(self) -> tuple[str, str]:
        """Classify each input channel under multiplication by units."""

        def kind(channel: Channel) -> str:
            z, w = channel
            return "regular" if z else ("nilpotent" if w else "zero")

        p, m = self.value.channels()
        return kind(p), kind(m)

    @property
    def sheet_counts(self) -> tuple[int, int]:
        if self.degree == 1:
            return 1, 1

        def sheets(kind: str) -> int:
            return {"regular": self.degree, "nilpotent": 0, "zero": 1}[kind]

        p, m = self.strata
        return sheets(p), sheets(m)

    @property
    def count(self) -> int | float:
        p, m = self.sheet_counts
        if p * m and self.degree > 1 and "zero" in self.strata:
            return math.inf
        return p * m

    def at(
        self,
        plus: int = 0,
        minus: int = 0,
        *,
        plus_tangent: complex = 0j,
        minus_tangent: complex = 0j,
    ) -> Ultra:
        """Select a sheet and, for each free channel, its arbitrary complex tangent."""
        if self.degree == 1:
            if (
                type(plus) is not int
                or type(minus) is not int
                or plus
                or minus
                or plus_tangent
                or minus_tangent
            ):
                raise ValueError("Degree one has one fixed root")
            return self.value
        counts = self.sheet_counts
        if not all(counts):
            raise DomainError("A nonzero pure nilpotent channel has no such root")

        def channel_root(channel: Channel, index: int, count: int, tangent: complex) -> Channel:
            if type(index) is not int or not 0 <= index < count:
                raise ValueError("Sheet index is outside the channel's range")
            z, w = channel
            if not z:
                return 0j, tangent
            if tangent:
                raise ValueError("Only a zero channel admits a free tangent for degree > 1")
            if self.degree == 2:
                u = cmath.sqrt(z) * (1 if index == 0 else -1)
            else:
                u = cmath.rect(
                    abs(z) ** (1 / self.degree), (cmath.phase(z) + math.tau * index) / self.degree
                )
            if not w:
                return u, 0j

            # u*w/(n*z); avoid intermediate overflow with exact binary inputs.
            def exact(x: complex) -> ExactComplex:
                return ExactComplex(Fraction(x.real), Fraction(x.imag))

            variation = exact(u) * exact(w) / (exact(z) * self.degree)
            return u, complex(float(variation.real), float(variation.imag))

        p, m = self.value.channels()
        return Ultra.from_channels(
            channel_root(p, plus, counts[0], plus_tangent),
            channel_root(m, minus, counts[1], minus_tangent),
        )

    def representatives(self) -> Iterator[Ultra]:
        """One value per discrete sheet, setting all free tangents to zero."""
        p, m = self.sheet_counts
        for i in range(p):
            for j in range(m):
                yield self.at(i, j)
