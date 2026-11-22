"""Immutable Cartesian and polar coordinates (the original Polynominal2D)."""

from __future__ import annotations

import math
from dataclasses import dataclass


def wrap_angle(angle: float) -> float:
    value = (angle + math.pi) % math.tau - math.pi
    return math.pi if value == -math.pi else value


@dataclass(frozen=True, slots=True)
class Cartesian2D:
    x: float = 0.0
    y: float = 0.0

    def __post_init__(self) -> None:
        if not all(map(math.isfinite, (self.x, self.y))):
            raise ValueError("Coordinates must be finite")

    @property
    def polar(self) -> Polar2D:
        return Polar2D(math.hypot(self.x, self.y), math.atan2(self.y, self.x))

    def dot(self, other: Cartesian2D) -> float:
        return self.x * other.x + self.y * other.y

    def __add__(self, other: Cartesian2D) -> Cartesian2D:
        return Cartesian2D(self.x + other.x, self.y + other.y)

    def __sub__(self, other: Cartesian2D) -> Cartesian2D:
        return Cartesian2D(self.x - other.x, self.y - other.y)


@dataclass(frozen=True, slots=True)
class Polar2D:
    radius: float = 0.0
    angle: float = 0.0

    def __post_init__(self) -> None:
        if not all(map(math.isfinite, (self.radius, self.angle))):
            raise ValueError("Coordinates must be finite")
        angle = self.angle + (math.pi if self.radius < 0 else 0)
        object.__setattr__(self, "radius", abs(self.radius))
        object.__setattr__(self, "angle", wrap_angle(angle))

    @property
    def cartesian(self) -> Cartesian2D:
        return Cartesian2D(self.radius * math.cos(self.angle), self.radius * math.sin(self.angle))

    def turned_by(self, angle: float) -> Polar2D:
        return Polar2D(self.radius, self.angle + angle)

    def __mul__(self, other: Polar2D) -> Polar2D:
        return Polar2D(self.radius * other.radius, self.angle + other.angle)

    def __truediv__(self, other: Polar2D) -> Polar2D:
        return Polar2D(self.radius / other.radius, self.angle - other.angle)


Polynominal2D = Polar2D
