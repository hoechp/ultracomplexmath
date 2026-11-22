"""Static parametric surfaces with Ultra-valued scalar fields.

The induced metric belongs to the real surface, not to the value algebra.
Torus/Mobius seam checks concern ordinary scalar fields with unchanged values.
"""

from __future__ import annotations

import math
from collections.abc import Callable, Sequence
from dataclasses import dataclass

from .core import Ultra
from .fields import (
    CoordinateMap,
    CoordinateSpace,
    LocatedUltra,
    SpaceTimePoint,
    UltraField,
    _real,
    _weighted_sum,
)

type Position2 = tuple[float, float]
type Jacobian2 = tuple[tuple[float, float], ...]
type Metric2 = tuple[tuple[float, float], tuple[float, float]]


@dataclass(frozen=True, slots=True)
class SurfaceSeam:
    """Two equivalent boundary points and the diagonal transition derivative.

    For a Mobius strip: left=(0,v), right=(2*pi,-v), signs=(1,-1).
    Thus F_v(left)=-F_v(right); no algebra coefficient changes its meaning.
    """

    left: Callable[[float], Position2]
    right: Callable[[float], Position2]
    derivative_signs: tuple[int, int] = (1, 1)

    def __post_init__(self) -> None:
        if len(self.derivative_signs) != 2 or any(s not in (-1, 1) for s in self.derivative_signs):
            raise ValueError("Seam transition signs must be +/-1")


@dataclass(frozen=True, slots=True)
class SeamReport:
    """Maximum absolute mismatch per coefficient over a finite set of samples."""

    comparisons: int
    value_errors: tuple[float, ...]
    derivative_errors: tuple[tuple[float, ...], ...]

    def within(self, *, atol: float = 1e-7) -> bool:
        tolerance = _real(atol, "Seam tolerance")
        if tolerance < 0:
            raise ValueError("Seam tolerance must be nonnegative")
        return all(e <= tolerance for e in self.value_errors) and all(
            e <= tolerance for errors in self.derivative_errors for e in errors
        )


@dataclass(frozen=True, slots=True)
class ParametricSurface:
    """A static two-parameter immersion in an ordinary Euclidean ambient space.

    ``jacobian`` returns one (du,dv) row per ambient spatial coordinate.
    Bounds specify a fundamental integration rectangle, not an automatic
    boundary condition. Rules/stencils must be defined where evaluated.
    Degenerate/ill-conditioned charts raise instead of using a pseudoinverse.
    """

    embedding: Callable[[Position2], tuple[float, ...]]
    jacobian: Callable[[Position2], Jacobian2]
    bounds: tuple[tuple[float, float], tuple[float, float]]
    space: CoordinateSpace = CoordinateSpace(("u", "v"))
    ambient: CoordinateSpace = CoordinateSpace()
    seams: tuple[SurfaceSeam, ...] = ()
    name: str = "surface"

    def __post_init__(self) -> None:
        if len(self.space.spatial_axes) != 2:
            raise ValueError("A parametric surface needs two spatial parameters")
        if len(self.ambient.spatial_axes) < 2 or self.space.time_axis != self.ambient.time_axis:
            raise ValueError("Surface needs at least two ambient axes and matching time axes")
        bounds = tuple(tuple(_real(x, "Surface bound") for x in pair) for pair in self.bounds)
        if len(bounds) != 2 or any(len(pair) != 2 or pair[0] >= pair[1] for pair in bounds):
            raise ValueError("Surface bounds must contain two increasing finite intervals")
        object.__setattr__(self, "bounds", bounds)
        object.__setattr__(self, "seams", tuple(self.seams))

    def _position(self, point: SpaceTimePoint) -> Position2:
        if point.space != self.space:
            raise ValueError("Point must belong to the surface parameter space")
        return point.position[0], point.position[1]

    @property
    def coordinate_map(self) -> CoordinateMap:
        def embed(point: SpaceTimePoint) -> SpaceTimePoint:
            return self.ambient.point(*self.embedding(self._position(point)), time=point.time)

        return CoordinateMap(self.space, self.ambient, embed)

    def locate(self, value: LocatedUltra) -> LocatedUltra:
        return self.coordinate_map.locate(value)

    def pullback(self, field: UltraField) -> UltraField:
        return self.coordinate_map.pullback(field)

    def _geometry(self, point: SpaceTimePoint) -> tuple[Jacobian2, Metric2, Metric2, float]:
        rows = tuple(
            tuple(_real(x, "Jacobian entry") for x in row)
            for row in self.jacobian(self._position(point))
        )
        if len(rows) != len(self.ambient.spatial_axes) or any(len(row) != 2 for row in rows):
            raise ValueError("Jacobian must have shape (ambient dimension, 2)")
        jac: Jacobian2 = tuple((row[0], row[1]) for row in rows)
        scale = max(abs(x) for row in jac for x in row)
        if scale == 0:
            raise ValueError("Degenerate surface chart")
        a = math.fsum((row[0] / scale) ** 2 for row in jac)
        b = math.fsum((row[0] / scale) * (row[1] / scale) for row in jac)
        d = math.fsum((row[1] / scale) ** 2 for row in jac)
        determinant = a * d - b * b
        if determinant <= 1e-14 * (a + d) ** 2:
            raise ValueError("Degenerate or ill-conditioned surface chart")
        square = scale * scale
        if square == 0 or not math.isfinite(square):
            raise ValueError("Surface metric exceeds floating-point range")
        metric: Metric2 = ((a * square, b * square), (b * square, d * square))
        inverse: Metric2 = (
            ((d / determinant) / square, (-b / determinant) / square),
            ((-b / determinant) / square, (a / determinant) / square),
        )
        area = math.sqrt(determinant) * square
        if (
            area == 0
            or not all(math.isfinite(x) for row in metric + inverse for x in row)
            or not math.isfinite(area)
        ):
            raise ValueError("Surface metric exceeds floating-point range")
        return jac, metric, inverse, area

    def metric(self, point: SpaceTimePoint) -> Metric2:
        """The real first fundamental form J^T J in parameter coordinates."""
        return self._geometry(point)[1]

    def area_density(self, point: SpaceTimePoint) -> float:
        return self._geometry(point)[3]

    def _check_field(self, field: UltraField) -> None:
        if field.space != self.space:
            raise ValueError("Field must use the surface parameter space")

    def gradient(
        self, field: UltraField, point: SpaceTimePoint, *, step: float = 1e-3
    ) -> tuple[Ultra, ...]:
        """Ambient components of the tangent gradient J g^{-1} dF."""
        self._check_field(field)
        jac, _, inverse, _ = self._geometry(point)
        partials = [d(point) for d in field.gradient(step=step)]
        intrinsic = [_weighted_sum(list(zip(row, partials, strict=True))) for row in inverse]
        return tuple(_weighted_sum(list(zip(row, intrinsic, strict=True))) for row in jac)

    def laplacian(self, field: UltraField, *, step: float = 1e-3) -> UltraField:
        """Laplace-Beltrami: |g|^-1/2 d_a(|g|^1/2 g^{ab} d_b F).

        This differentiates the metric as well as the value. Numerical stencils
        require a smooth local extension at a boundary or seam.
        """
        self._check_field(field)
        partials = field.gradient(step=step)

        def flux(index: int) -> UltraField:
            def rule(point: SpaceTimePoint) -> Ultra:
                _, _, inverse, area = self._geometry(point)
                return _weighted_sum(
                    [(area * inverse[index][b], d(point)) for b, d in enumerate(partials)]
                )

            return UltraField(rule, self.space)

        derivatives = [
            flux(a).partial(axis, step=step) for a, axis in enumerate(self.space.spatial_axes)
        ]
        return UltraField(
            lambda p: _weighted_sum([(1 / self.area_density(p), d(p)) for d in derivatives]),
            self.space,
            f"Delta_{self.name}({field.name})",
        )

    def integrate(
        self,
        field: UltraField,
        *,
        shape: tuple[int, int] = (64, 64),
        time: float | None = None,
        max_points: int = 1_000_000,
    ) -> Ultra:
        """Midpoint quadrature of F dA over bounds; no orientation is required."""
        self._check_field(field)
        if len(shape) != 2 or any(type(n) is not int or n < 1 for n in shape):
            raise ValueError("Quadrature shape must contain two positive integers")
        if type(max_points) is not int or max_points < 1 or math.prod(shape) > max_points:
            raise ValueError("Quadrature exceeds the positive max_points budget")
        widths = tuple((hi - lo) / n for (lo, hi), n in zip(self.bounds, shape, strict=True))
        terms = []
        for a in range(shape[0]):
            for b in range(shape[1]):
                p = self.space.point(
                    self.bounds[0][0] + (a + 0.5) * widths[0],
                    self.bounds[1][0] + (b + 0.5) * widths[1],
                    time=time,
                )
                terms.append((self.area_density(p) * widths[0] * widths[1], field(p)))
        return _weighted_sum(terms)

    def check_seams(
        self,
        field: UltraField,
        *,
        samples: int = 17,
        times: Sequence[float | None] = (None,),
        derivatives: bool = True,
        step: float = 1e-3,
    ) -> SeamReport:
        """Check values and first derivatives at finitely many seam points.

        A successful report is a diagnostic, not proof of global smoothness.
        Seam functions receive fractions in [0,1]. Derivatives compare with
        the declared transition signs, including the Mobius transverse flip.
        """
        self._check_field(field)
        if not self.seams:
            raise ValueError("This surface has no declared seams")
        if type(samples) is not int or samples < 2 or not times:
            raise ValueError("At least two seam samples and one time are required")
        partials = field.gradient(step=step) if derivatives else ()
        errors = [0.0] * 8
        derivative_errors = [[0.0] * 8 for _ in partials]
        count = 0
        for seam in self.seams:
            for time in times:
                for n in range(samples):
                    fraction = n / (samples - 1)
                    left = self.space.point(*seam.left(fraction), time=time)
                    right = self.space.point(*seam.right(fraction), time=time)
                    difference = field(left) - field(right)
                    errors = [max(e, abs(v)) for e, v in zip(errors, difference, strict=True)]
                    for a, derivative in enumerate(partials):
                        delta = derivative(left) - derivative(right) * seam.derivative_signs[a]
                        derivative_errors[a] = [
                            max(e, abs(v)) for e, v in zip(derivative_errors[a], delta, strict=True)
                        ]
                    count += 1
        return SeamReport(count, tuple(errors), tuple(tuple(row) for row in derivative_errors))


def torus(
    major_radius: float = 2.0, minor_radius: float = 0.65, *, time_axis: str | None = "t"
) -> ParametricSurface:
    """Embedded ring torus; both parameters are 2*pi periodic."""
    major = _real(major_radius, "Major radius")
    minor = _real(minor_radius, "Minor radius")
    if not 0 < minor < major:
        raise ValueError("A regular ring torus requires 0 < minor_radius < major_radius")

    def embedding(p: Position2) -> tuple[float, ...]:
        u, v = p
        radius = major + minor * math.cos(v)
        return radius * math.cos(u), radius * math.sin(u), minor * math.sin(v)

    def jacobian(p: Position2) -> Jacobian2:
        u, v = p
        radius = major + minor * math.cos(v)
        return (
            (-radius * math.sin(u), -minor * math.sin(v) * math.cos(u)),
            (radius * math.cos(u), -minor * math.sin(v) * math.sin(u)),
            (0, minor * math.cos(v)),
        )

    seams = (
        SurfaceSeam(lambda f: (0, math.tau * f), lambda f: (math.tau, math.tau * f)),
        SurfaceSeam(lambda f: (math.tau * f, 0), lambda f: (math.tau * f, math.tau)),
    )
    return ParametricSurface(
        embedding,
        jacobian,
        ((0, math.tau), (0, math.tau)),
        CoordinateSpace(("u", "v"), time_axis),
        CoordinateSpace(time_axis=time_axis),
        seams,
        "torus",
    )


def mobius_strip(
    radius: float = 2.0, half_width: float = 0.6, *, time_axis: str | None = "t"
) -> ParametricSurface:
    """Mobius strip with (u+2*pi,v) equivalent to (u,-v), ordinary scalar values."""
    radius = _real(radius, "Radius")
    width = _real(half_width, "Half width")
    if not 0 < width < radius:
        raise ValueError("Require 0 < half_width < radius")

    def embedding(p: Position2) -> tuple[float, ...]:
        u, v = p
        radial = radius + v * math.cos(u / 2)
        return radial * math.cos(u), radial * math.sin(u), v * math.sin(u / 2)

    def jacobian(p: Position2) -> Jacobian2:
        u, v = p
        c, s = math.cos(u / 2), math.sin(u / 2)
        radial = radius + v * c
        return (
            (-radial * math.sin(u) - v * s * math.cos(u) / 2, c * math.cos(u)),
            (radial * math.cos(u) - v * s * math.sin(u) / 2, c * math.sin(u)),
            (v * c / 2, s),
        )

    seam = SurfaceSeam(
        lambda f: (0, (2 * f - 1) * width),
        lambda f: (math.tau, -(2 * f - 1) * width),
        (1, -1),
    )
    return ParametricSurface(
        embedding,
        jacobian,
        ((0, math.tau), (-width, width)),
        CoordinateSpace(("u", "v"), time_axis),
        CoordinateSpace(time_axis=time_axis),
        (seam,),
        "mobius",
    )
