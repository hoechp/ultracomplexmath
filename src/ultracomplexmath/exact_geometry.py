"""Exact Euclidean construction and predicates on rational planar coordinates.

These use the circular plane's affine coordinates. They do not silently apply
Euclidean predicates to the hyperbolic or degenerate parabolic metric.
"""

from __future__ import annotations

from collections.abc import Sequence
from fractions import Fraction

from .core import DomainError
from .exact import Rational, rational

type RationalPoint2 = tuple[Fraction, Fraction]
type PointInput = Sequence[Rational]


def rational_point2(value: PointInput) -> RationalPoint2:
    if len(value) != 2:
        raise ValueError("A planar point requires two rational coordinates")
    return rational(value[0]), rational(value[1])


def _sub(a: RationalPoint2, b: RationalPoint2) -> RationalPoint2:
    return a[0] - b[0], a[1] - b[1]


def _cross(a: RationalPoint2, b: RationalPoint2) -> Fraction:
    return a[0] * b[1] - a[1] * b[0]


def orientation2d(a: PointInput, b: PointInput, c: PointInput) -> Fraction:
    """Signed twice-area: >0 counterclockwise, <0 clockwise, =0 collinear."""
    p, q, r = map(rational_point2, (a, b, c))
    return _cross(_sub(q, p), _sub(r, p))


def line_intersection2d(
    a: PointInput, b: PointInput, c: PointInput, d: PointInput
) -> RationalPoint2:
    """Unique intersection of two infinite lines, each given by distinct points."""
    p, q, r, s = map(rational_point2, (a, b, c, d))
    u, v = _sub(q, p), _sub(s, r)
    if not any(u) or not any(v):
        raise DomainError("A line needs two distinct points")
    denominator = _cross(u, v)
    if not denominator:
        raise DomainError("Parallel or coincident lines have no unique intersection")
    t = _cross(_sub(r, p), v) / denominator
    return p[0] + t * u[0], p[1] + t * u[1]


def segment_intersection2d(
    a: PointInput, b: PointInput, c: PointInput, d: PointInput
) -> tuple[RationalPoint2, ...]:
    """Empty, singleton, or two endpoints of a closed overlapping segment.

    Degenerate point segments and exact endpoint contacts are supported.
    """
    p, q, r, s = map(rational_point2, (a, b, c, d))
    u, v, offset = _sub(q, p), _sub(s, r), _sub(r, p)
    denominator = _cross(u, v)
    if denominator:
        t, w = _cross(offset, v) / denominator, _cross(offset, u) / denominator
        return ((p[0] + t * u[0], p[1] + t * u[1]),) if 0 <= t <= 1 and 0 <= w <= 1 else ()
    if _cross(offset, u) or _cross(offset, v):
        return ()
    lower, upper = max(min(p, q), min(r, s)), min(max(p, q), max(r, s))
    return () if lower > upper else (lower,) if lower == upper else (lower, upper)


def barycentric2d(
    point: PointInput, a: PointInput, b: PointInput, c: PointInput
) -> tuple[Fraction, Fraction, Fraction]:
    """Affine barycentric coordinates of a point in a nondegenerate triangle."""
    p, x, y, z = map(rational_point2, (point, a, b, c))
    area = orientation2d(x, y, z)
    if not area:
        raise DomainError("A collinear triangle has no unique barycentric coordinates")
    return (
        orientation2d(p, y, z) / area,
        orientation2d(x, p, z) / area,
        orientation2d(x, y, p) / area,
    )


def circumcircle2d(a: PointInput, b: PointInput, c: PointInput) -> tuple[RationalPoint2, Fraction]:
    """Return rational center and radius SQUARED; no irrational square root."""
    p, q, r = map(rational_point2, (a, b, c))
    u, v = _sub(q, p), _sub(r, p)
    denominator = 2 * _cross(u, v)
    if not denominator:
        raise DomainError("Collinear points do not determine a unique circle")
    uu, vv = u[0] ** 2 + u[1] ** 2, v[0] ** 2 + v[1] ** 2
    x, y = (uu * v[1] - vv * u[1]) / denominator, (u[0] * vv - v[0] * uu) / denominator
    return (p[0] + x, p[1] + y), x * x + y * y


def incircle2d(point: PointInput, a: PointInput, b: PointInput, c: PointInput) -> int:
    """+1 inside, 0 on, -1 outside the circumcircle, independent of winding."""
    p, x, y, z = map(rational_point2, (point, a, b, c))
    area = orientation2d(x, y, z)
    if not area:
        raise DomainError("Collinear points do not determine a circle")
    u, v, w = _sub(x, p), _sub(y, p), _sub(z, p)
    determinant = (
        (u[0] ** 2 + u[1] ** 2) * _cross(v, w)
        - (v[0] ** 2 + v[1] ** 2) * _cross(u, w)
        + (w[0] ** 2 + w[1] ** 2) * _cross(u, v)
    )
    oriented = determinant if area > 0 else -determinant
    return (oriented > 0) - (oriented < 0)
