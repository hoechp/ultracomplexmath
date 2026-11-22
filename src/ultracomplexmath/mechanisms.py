"""Articulated frames, scalar freedoms and actors, independent of any GUI."""

from __future__ import annotations

import math
from dataclasses import dataclass, field, replace

from . import geometry as g
from .numbers import Binary, Hypercomplex


@dataclass
class Joint:
    position: g.Vector = g.ZERO3
    normal: g.Vector = g.BASE[2]
    compare: g.Vector = g.BASE[0]
    length: float = 1.0
    angle: Hypercomplex = Binary()
    axis: bool = False

    @property
    def endpoint(self) -> g.Vector:
        return g.add(
            self.position,
            g.scale(
                g.to_frame(g.vector_from_angle(self.angle), self.normal, self.compare), self.length
            ),
        )

    def shift(self, displacement: g.Vector) -> None:
        self.position = g.add(self.position, displacement)

    def stretch(self, factor: float) -> None:
        self.length *= factor

    def add_angle(self, value: Hypercomplex) -> None:
        self.angle = self.angle + value

    def rotate(self, axis: g.Vector, radians: float) -> None:
        self.normal = g.rotate(self.normal, axis, radians)
        self.compare = g.rotate(self.compare, axis, radians)

    def roll(self, radians: float) -> None:
        self.rotate(self.normal, radians)

    def turn(self, radians: float) -> None:
        self.rotate(g.frame(self.normal, self.compare)[1], radians)

    def elevate(self, radians: float) -> None:
        self.rotate(g.frame(self.normal, self.compare)[0], radians)

    def switch_mode(self) -> None:
        self.axis = not self.axis


@dataclass(eq=False)
class Mechanism:
    joint: Joint = field(default_factory=Joint)
    parent: Mechanism | None = None
    attachments: list[Mechanism] = field(default_factory=list, init=False)
    adjusted_joint: Joint = field(init=False)

    def __post_init__(self) -> None:
        self.joint = replace(self.joint)
        parent, self.parent = self.parent, None
        self.reparent(parent)

    def reparent(self, parent: Mechanism | None) -> None:
        cursor = parent
        while cursor is not None:
            if cursor is self:
                raise ValueError("Mechanisms cannot contain cycles")
            cursor = cursor.parent
        if self.parent is not None:
            self.parent.attachments.remove(self)
        self.parent = parent
        if parent is not None:
            parent.attachments.append(self)
        self.update()

    def update(self) -> None:
        adjusted = replace(self.joint)
        if self.parent is not None:
            p = self.parent.adjusted_joint
            adjusted.normal = g.to_frame(adjusted.normal, p.normal, p.compare)
            adjusted.compare = g.to_frame(adjusted.compare, p.normal, p.compare)
            adjusted.position = g.to_frame(adjusted.position, p.normal, p.compare)
            axis, radians = p.normal, p.angle.real
            if not p.axis:
                direction = g.sub(p.endpoint, p.position)
                if g.length(direction) == 0:
                    radians = 0.0
                else:
                    start = g.frame(p.normal, p.compare)[0]
                    perpendicular = g.cross(start, direction)
                    radians = g.angle(start, direction)
                    axis = perpendicular if g.length(perpendicular) > 1e-12 else p.normal
            if radians:
                adjusted.rotate(axis, radians)
                adjusted.position = g.rotate(adjusted.position, axis, radians)
            adjusted.position = g.add(adjusted.position, p.endpoint)
        self.adjusted_joint = adjusted
        for child in self.attachments:
            child.update()


@dataclass
class Freedom:
    periodic: bool = False
    percentage: float = 0.5
    factor: float = 1.0
    minimum: float = 0.0
    inverted: bool = False

    def __post_init__(self) -> None:
        self._normalize()

    def _normalize(self) -> None:
        if not all(map(math.isfinite, (self.percentage, self.factor, self.minimum))):
            raise ValueError("Freedom values must be finite")
        if self.periodic and not 0 <= self.percentage <= 1:
            self.percentage %= 1
        else:
            self.percentage = max(0.0, min(1.0, self.percentage))

    @property
    def value(self) -> float:
        return self.minimum + self.factor * self.percentage

    def add_percentage(self, value: float) -> None:
        self.percentage += -value if self.inverted else value
        self._normalize()

    def set_percentage(self, value: float) -> None:
        self.percentage = 1 - value if self.inverted else value
        self._normalize()

    def invert(self) -> None:
        self.minimum = -(self.minimum + self.factor)
        self.percentage = 1 - self.percentage
        self.inverted = not self.inverted

    def negate(self) -> None:
        self.inverted = not self.inverted


@dataclass
class Actor:
    joint: Joint
    freedoms: dict[str, Freedom] = field(default_factory=dict)
    original: Joint = field(init=False)

    def __post_init__(self) -> None:
        self.original = replace(self.joint)

    def act(self) -> None:
        if self.freedoms.keys() - {"stretch", "roll", "turn", "elevate", "real", "imag"}:
            raise ValueError("Unknown freedom")
        if any(k in self.freedoms for k in ("roll", "turn", "elevate")):
            self.joint.normal, self.joint.compare = self.original.normal, self.original.compare
        for name in ("roll", "turn", "elevate"):
            if name in self.freedoms:
                getattr(self.joint, name)(self.freedoms[name].value)
        if "stretch" in self.freedoms:
            self.joint.length = self.freedoms["stretch"].value
        self.joint.angle = self.joint.angle.with_coefficients(
            real=self.freedoms["real"].value if "real" in self.freedoms else None,
            imag=self.freedoms["imag"].value if "imag" in self.freedoms else None,
        )

    def reset(self) -> None:
        for name in ("position", "normal", "compare", "length", "angle", "axis"):
            setattr(self.joint, name, getattr(self.original, name))


@dataclass
class Machine:
    root: Mechanism = field(default_factory=Mechanism)
    mechanisms: dict[str, Mechanism] = field(default_factory=dict)
    actors: dict[str, Actor] = field(default_factory=dict)

    def connect(self, name: str, joint: Joint, parent: str | None = None) -> Mechanism:
        if name in self.mechanisms:
            raise ValueError("Duplicate mechanism name")
        mechanism = Mechanism(joint, self.root if parent is None else self.mechanisms[parent])
        self.mechanisms[name] = mechanism
        self.actors[name] = Actor(mechanism.joint)
        return mechanism

    def update(self) -> None:
        for actor in self.actors.values():
            actor.act()
        self.root.update()
