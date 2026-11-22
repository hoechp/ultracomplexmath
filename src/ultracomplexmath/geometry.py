"""Finite vectors, orthonormal frames, hypercomplex angles and oriented lines."""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass

from .core import DomainError
from .numbers import Binary, Dual, Hypercomplex

type Vector = tuple[float, ...]
type Frame = tuple[Vector, Vector, Vector]
BASE: Frame = ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0))
ZERO3: Vector = (0.0, 0.0, 0.0)


def vector(values: Sequence[float]) -> Vector:
    result = tuple(map(float, values))
    if not result or not all(map(math.isfinite, result)):
        raise ValueError("A vector must have finite coordinates and positive dimension")
    return result


def add(a: Sequence[float], b: Sequence[float]) -> Vector:
    return tuple(x + y for x, y in zip(a, b, strict=True))


def sub(a: Sequence[float], b: Sequence[float]) -> Vector:
    return tuple(x - y for x, y in zip(a, b, strict=True))


def scale(a: Sequence[float], factor: float) -> Vector:
    return tuple(x * factor for x in a)


def dot(a: Sequence[float], b: Sequence[float] | None = None) -> float:
    return math.fsum(x * y for x, y in zip(a, a if b is None else b, strict=True))


def length(a: Sequence[float]) -> float:
    return math.hypot(*a)


def unit(a: Sequence[float]) -> Vector:
    values = vector(a)
    magnitude = max(map(abs, values))
    if magnitude == 0:
        raise DomainError("A zero vector has no direction")
    scaled = tuple(x / magnitude for x in values)
    norm = math.hypot(*scaled)
    return tuple(x / norm for x in scaled)


def cross(a: Sequence[float], b: Sequence[float]) -> Vector:
    x, y, z = a
    u, v, w = b
    return y * w - z * v, z * u - x * w, x * v - y * u


def isclose(a: Sequence[float], b: Sequence[float], *, tolerance: float = 1e-10) -> bool:
    return len(a) == len(b) and all(abs(x - y) <= tolerance for x, y in zip(a, b, strict=True))


def project(a: Sequence[float], direction: Sequence[float]) -> Vector:
    axis = unit(direction)
    return scale(axis, dot(a, axis))


def reject(a: Sequence[float], direction: Sequence[float]) -> Vector:
    return sub(a, project(a, direction))


def angle(a: Sequence[float], b: Sequence[float]) -> float:
    u, v = unit(a), unit(b)
    # The half-angle formula retains small angles and is stable near pi.
    return 2 * math.atan2(length(sub(u, v)), length(add(u, v)))


def rotate(value: Sequence[float], axis: Sequence[float], radians: float) -> Vector:
    n = unit(axis)
    c, s = math.cos(radians), math.sin(radians)
    return add(add(scale(value, c), scale(cross(n, value), s)), scale(n, dot(n, value) * (1 - c)))


def frame(normal: Sequence[float], compare: Sequence[float]) -> Frame:
    z = unit(normal)
    y = unit(cross(z, unit(compare)))
    return unit(cross(y, z)), y, z


def to_base(value: Sequence[float], basis: Sequence[Sequence[float]]) -> Vector:
    if len(value) != len(basis) or not basis:
        raise ValueError("Coordinate and basis dimensions differ")
    result = (0.0,) * len(basis[0])
    for coefficient, axis in zip(value, basis, strict=True):
        result = add(result, scale(unit(axis), coefficient))
    return result


def from_base(value: Sequence[float], basis: Sequence[Sequence[float]]) -> Vector:
    from .linalg import real_solution

    axes = [unit(axis) for axis in basis]
    result = real_solution(list(map(list, zip(*axes, strict=True))), value)
    if result.basis:
        raise DomainError("Basis is linearly dependent")
    return result.particular


def to_frame(value: Sequence[float], normal: Sequence[float], compare: Sequence[float]) -> Vector:
    return to_base(value, frame(normal, compare))


def from_frame(value: Sequence[float], normal: Sequence[float], compare: Sequence[float]) -> Vector:
    return from_base(value, frame(normal, compare))


def azimuth(
    value: Sequence[float], normal: Sequence[float] = BASE[2], compare: Sequence[float] = BASE[0]
) -> float:
    x, y, _ = from_frame(value, normal, compare)
    return math.atan2(y, x)


def vector_from_angle(value: Hypercomplex) -> Vector:
    a, b = value.real, value.imag
    if isinstance(value, Binary):
        radius, z = math.cos(b), math.sin(b)
    elif isinstance(value, Dual):
        radius, z = 1.0, b
    else:
        radius, z = math.cosh(b), math.sinh(b)
    return math.cos(a) * radius, math.sin(a) * radius, z


def angle_from_vector(
    value: Sequence[float], kind: type[Hypercomplex] = Binary
) -> tuple[Hypercomplex, float]:
    x, y, z = value
    radial = math.hypot(x, y)
    a = math.atan2(y, x)
    if issubclass(kind, Binary):
        magnitude = math.hypot(radial, z)
        if magnitude == 0:
            raise DomainError("Zero has no direction")
        return kind(a, math.atan2(z, radial)), magnitude
    if issubclass(kind, Dual):
        if radial == 0:
            raise DomainError("Dual angles require a nonzero xy projection")
        return kind(a, z / radial), radial
    if radial <= abs(z):
        raise DomainError("Complex angles require x²+y² > z²")
    ratio = abs(z) / radial
    magnitude = radial * math.sqrt(1 - ratio) * math.sqrt(1 + ratio)
    return kind(a, math.asinh(z / magnitude)), magnitude


@dataclass(frozen=True)
class Line:
    point: Vector
    direction: Vector

    def __post_init__(self) -> None:
        if len(self.point) != 3 or len(self.direction) != 3:
            raise ValueError("Lines require three dimensions")
        object.__setattr__(self, "point", vector(self.point))
        object.__setattr__(self, "direction", unit(vector(self.direction)))

    def at(self, parameter: float) -> Vector:
        return add(self.point, scale(self.direction, parameter))

    def closest_points(self, other: Line) -> tuple[Vector, Vector]:
        v, w = self.direction, other.direction
        offset = sub(self.point, other.point)
        b, d, e = dot(v, w), dot(v, offset), dot(w, offset)
        denominator = dot(cross(v, w))
        if denominator <= 1e-24:
            return self.point, other.at(e)
        t, u = (b * e - d) / denominator, (e - b * d) / denominator
        return self.at(t), other.at(u)

    def connecting_normal(self, other: Line) -> Vector:
        first, second = self.closest_points(other)
        return sub(second, first)

    def intersection(self, other: Line, *, tolerance: float = 1e-10) -> Vector:
        first, second = self.closest_points(other)
        if length(sub(first, second)) > tolerance:
            raise DomainError("Lines do not intersect")
        if length(cross(self.direction, other.direction)) <= tolerance:
            raise DomainError("Coincident lines have no unique intersection")
        return scale(add(first, second), 0.5)

    def normalized_pair(self, other: Line) -> tuple[Line, Line]:
        first, second = self.closest_points(other)
        return Line(first, self.direction), Line(second, other.direction)

    def dual_angle(self, other: Line) -> Dual:
        radians = angle(self.direction, other.direction)
        orientation = dot(cross(self.direction, other.direction), sub(other.point, self.point))
        return Dual(-radians if orientation < 0 else radians, length(self.connecting_normal(other)))

    def transcend(self, screw: Sequence[float], value: Dual) -> Line:
        return Line(
            add(self.point, scale(unit(screw), value.imag)),
            rotate(self.direction, screw, value.real),
        )
