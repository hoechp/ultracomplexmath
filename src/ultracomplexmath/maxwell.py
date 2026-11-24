"""Source-free vacuum electrodynamics in normalized units c = ε₀ = μ₀ = 1.

A physical vector has three entries F = E + ij B. Fourier amplitudes and
epsilon variations use the whole scalar algebra. Time is measured as ct.
"""

from __future__ import annotations

import cmath
import math
from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field
from typing import Literal

from .core import ZERO, DomainError, I, J, Scalar, Ultra
from .fields import UltraField, _real

type Vector = tuple[Ultra, Ultra, Ultra]
type Direction = tuple[float, float, float]
IJ = I * J


def _vector(values: Sequence[Scalar]) -> Vector:
    x, y, z = values
    return Ultra.coerce(x), Ultra.coerce(y), Ultra.coerce(z)


def _direction(values: Sequence[float]) -> Direction:
    x, y, z = values
    return _real(x, "x"), _real(y, "y"), _real(z, "z")


def _cross(a: Sequence[Ultra | float], b: Sequence[Ultra]) -> Vector:
    x, y, z = a
    u, v, w = b
    return y * w - z * v, z * u - x * w, x * v - y * u


def _dot(a: Sequence[Ultra | float], b: Vector) -> Ultra:
    return sum((x * y for x, y in zip(a, b, strict=True)), ZERO)


def _pack(electric: Sequence[Scalar], magnetic: Sequence[Scalar]) -> Vector:
    e, b = _vector(electric), _vector(magnetic)
    if any(v != v.conjugate("j") for v in (*e, *b)):
        raise ValueError("E and B components must be complex-dual amplitudes without j")
    return _vector([x + IJ * y for x, y in zip(e, b, strict=True)])


def _physical(v: Ultra) -> Ultra:
    # Half the sum with the physical reality involution conj_i(conj_j(v)).
    return Ultra(real=v.real, ij=v.ij, eps=v.eps, eps_ij=v.eps_ij)


@dataclass(frozen=True, slots=True)
class MaxwellState:
    """Real electromagnetic field at one event, with an optional first variation."""

    components: Vector

    def __post_init__(self) -> None:
        v = _vector(self.components)
        if any(x != _physical(x) for x in v):
            raise ValueError("A physical field needs E and B real in both epsilon layers")
        object.__setattr__(self, "components", v)

    @classmethod
    def from_fields(cls, electric: Sequence[Scalar], magnetic: Sequence[Scalar]) -> MaxwellState:
        return cls(_pack(electric, magnetic))

    @property
    def electric(self) -> Vector:
        return _vector([Ultra.dual(x.real, x.eps) for x in self.components])

    @property
    def magnetic(self) -> Vector:
        return _vector([Ultra.dual(x.ij, x.eps_ij) for x in self.components])

    @property
    def invariant(self) -> Ultra:
        """F·F = E² − B² + 2ij E·B, including its variation."""
        return _dot(self.components, self.components)

    @property
    def energy(self) -> Ultra:
        e, b = self.electric, self.magnetic
        return (_dot(e, e) + _dot(b, b)) * 0.5

    @property
    def poynting(self) -> Vector:
        return _cross(self.electric, self.magnetic)

    def boosted(self, direction: Sequence[float], rapidity: float) -> MaxwellState:
        """Fields measured at this same event by an observer moving along direction."""
        n = _direction(direction)
        length = math.hypot(*n)
        if not length or not math.isfinite(length):
            raise ValueError("A boost needs a finite nonzero direction with representable length")
        n = (n[0] / length, n[1] / length, n[2] / length)
        r = _real(rapidity, "Rapidity")
        parallel = _dot(n, self.components)
        cross = _cross(n, self.components)
        if not r:
            return self

        def transform(axis: float, v: Ultra, w: Ultra) -> Ultra:
            along = axis * parallel
            transverse = v - along
            generator = -IJ * w
            if abs(r) < 1:
                return v + (2 * math.sinh(r / 2) ** 2) * transverse + math.sinh(r) * generator
            # Scale the counterpropagating null directions separately. For a
            # co-moving plane wave this preserves exp(-r) even when cosh(r)
            # and sinh(r) have rounded to the same floating-point value.
            high, low = transverse * 0.5 + generator * 0.5, transverse * 0.5 - generator * 0.5
            return (
                along
                + (high * math.exp(r) if high else ZERO)
                + (low * math.exp(-r) if low else ZERO)
            )

        return MaxwellState(
            _vector(
                [
                    transform(axis, v, w)
                    for axis, v, w in zip(n, self.components, cross, strict=True)
                ]
            )
        )

    def energy_rest_boost(self) -> tuple[Direction, float]:
        """A minimum-speed boost that cancels the body energy flux, when finite."""
        # The direction depends only on field ratios. Normalize before squaring.
        scale = max(abs(v) for x in self.components for v in (x.real, x.ij))
        if scale == 0:
            return (1.0, 0.0, 0.0), 0.0
        state = MaxwellState.from_fields(
            [x.real / scale for x in self.components], [x.ij / scale for x in self.components]
        )
        sx, sy, sz = (v.real for v in state.poynting)
        flow = math.hypot(sx, sy, sz)
        if not flow:
            return (1.0, 0.0, 0.0), 0.0
        inv = state.invariant
        rest = math.hypot(inv.real, inv.ij) / 2
        if not rest:
            raise DomainError("A nonzero null field has no finite energy-rest observer")
        # asinh(flow/rest), with a log form if that ratio would overflow.
        ratio = flow / rest
        double_r = (
            math.asinh(ratio) if math.isfinite(ratio) else math.log(2 * flow) - math.log(rest)
        )
        return (sx / flow, sy / flow, sz / flow), double_r / 2


@dataclass(frozen=True, slots=True, init=False)
class MaxwellMode:
    """One real Fourier harmonic Re((E_k,B_k) exp(i k·x)) at t=0."""

    wavevector: Direction
    amplitude: Vector
    _quadrature: Vector = field(repr=False)
    _frequency: float = field(repr=False)

    def __init__(
        self, wavevector: Sequence[float], electric: Sequence[Scalar], magnetic: Sequence[Scalar]
    ) -> None:
        k = _direction(wavevector)
        magnitude = math.hypot(*k)
        if not math.isfinite(magnitude):
            raise ValueError("Unrepresentable wave number")
        a = _pack(electric, magnetic)
        n = (k[0] / magnitude, k[1] / magnitude, k[2] / magnitude) if magnitude else (0.0, 0.0, 0.0)
        # Check real, imaginary and both tangent parts separately for both fields.
        for column in zip(*(v.coefficients for v in a), strict=True):
            scale = max(map(abs, column))
            if (
                scale
                and abs(math.fsum(axis * (v / scale) for axis, v in zip(n, column, strict=True)))
                > 1e-12
            ):
                raise ValueError("Vacuum modes need transverse electric and magnetic amplitudes")
        if not magnitude and any(v != _physical(v) for v in a):
            raise ValueError("A uniform mode must have real electric and magnetic fields")
        object.__setattr__(self, "wavevector", k)
        object.__setattr__(self, "amplitude", a)
        object.__setattr__(self, "_frequency", magnitude)
        object.__setattr__(self, "_quadrature", _vector([J * v for v in _cross(n, a)]))

    @classmethod
    def traveling(cls, wavevector: Sequence[float], electric: Sequence[Scalar]) -> MaxwellMode:
        """Forward wave with B = k̂ × E; complex polarization is allowed."""
        k = _direction(wavevector)
        length = math.hypot(*k)
        if not length or not math.isfinite(length):
            raise ValueError("A traveling wave needs a nonzero finite wave number")
        e = _vector(electric)
        return cls(k, e, _cross([v / length for v in k], e))

    def spectrum(self, time: float) -> Vector:
        """Packed Fourier coefficient after exact-in-time modal evolution (binary64)."""
        phase = self._frequency * _real(time, "Time")
        c, s = math.cos(phase), math.sin(phase)
        return _vector(
            [c * a + s * b for a, b in zip(self.amplitude, self._quadrature, strict=True)]
        )

    def at(self, position: Sequence[float], time: float = 0) -> MaxwellState:
        x = _direction(position)
        phase = cmath.rect(1.0, math.fsum(k * u for k, u in zip(self.wavevector, x, strict=True)))
        return MaxwellState(_vector([_physical(v * phase) for v in self.spectrum(time)]))


@dataclass(frozen=True, slots=True, init=False)
class MaxwellField:
    """A superposition of arbitrary transverse harmonics and uniform backgrounds."""

    modes: tuple[MaxwellMode, ...]

    def __init__(self, modes: Iterable[MaxwellMode]) -> None:
        values = tuple(modes)
        if any(not isinstance(m, MaxwellMode) for m in values):
            raise TypeError("A Maxwell field requires MaxwellMode instances")
        object.__setattr__(self, "modes", values)

    def at(self, x: float, y: float, z: float, *, time: float = 0) -> MaxwellState:
        position, t = _direction((x, y, z)), _real(time, "Time")
        values = [mode.at(position, t).components for mode in self.modes]
        return MaxwellState(
            _vector(
                [
                    Ultra.from_coefficients(
                        math.fsum(v[axis].coefficients[k] for v in values) for k in range(8)
                    )
                    for axis in range(3)
                ]
            )
        )

    def component(self, axis: Literal["x", "y", "z"]) -> UltraField:
        """Expose one packed coordinate as a normal 3+1 UltraField for slices and grids."""
        index = ("x", "y", "z").index(axis)
        return UltraField(
            lambda p: self.at(*p.position, time=p["t"]).components[index], name=f"F_{axis}"
        )
