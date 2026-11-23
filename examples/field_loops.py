"""Build the offline F(z)=z-j path lab and check its presets with UltraField."""

from __future__ import annotations

import cmath
import json
import math
from dataclasses import dataclass
from pathlib import Path

from ultracomplexmath import ONE, CoordinateSpace, DomainError, J, Ultra, UltraField

FIELD = UltraField.from_formula("x+i*y-j", space=CoordinateSpace.cartesian(2, time_axis=None))
ROOT = Path(__file__).resolve().parents[1]
CLEARANCE = 0.045  # Radius of the two marked disks in the interactive experiment.


@dataclass(frozen=True)
class Lift:
    windings: tuple[int, int]
    factor: Ultra


def trace_loop(vertices: list[complex], *, clearance: float = CLEARANCE) -> Lift:
    """Lift the square root along the closed polygon, including the last-to-first edge."""
    if len(vertices) < 3 or not math.isfinite(clearance) or clearance < 0:
        raise ValueError("Supply three vertices and a finite nonnegative clearance")
    start = vertices[0]
    polar = FIELD.at(start.real, start.imag).value.polar()
    initial = polar
    for a, b in zip(vertices, vertices[1:] + [start], strict=True):
        step = b - a
        for pole in (1, -1):
            fraction = max(0.0, min(1.0, ((pole - a) / step).real)) if step else 0.0
            if abs(a + fraction * step - pole) <= clearance:
                raise DomainError("A segment touches a marked branch-point disk")
        polar = FIELD.at(b.real, b.imag).value.polar(previous=polar)
    turns = tuple(
        round((v - u) / math.tau) for v, u in zip(polar.phases, initial.phases, strict=True)
    )
    factor = polar.root() / initial.root()
    return Lift((turns[0], turns[1]), factor)


def presets() -> list[dict[str, object]]:
    samples = []
    for name, center, radius, wanted in [
        ("Right point", 1, 0.57, -J),
        ("Left point", -1, 0.57, J),
        ("Both points", 0, 1.65, -ONE),
        ("Neither point", 0, 0.5, ONE),
    ]:
        vertices = [center + radius * cmath.exp(1j * math.tau * k / 72) for k in range(72)]
        lift = trace_loop(vertices)
        if not lift.factor.isclose(wanted):
            raise AssertionError((name, lift))
        samples.append(
            {
                "name": name,
                "vertices": [[v.real, v.imag] for v in vertices],
                "windings": lift.windings,
            }
        )
    return samples


def main() -> None:
    template = Path(__file__).with_suffix(".html").read_text()
    data = {"clearance": CLEARANCE, "presets": presets()}
    (ROOT / "docs/gallery/field-loops.html").write_text(
        template.replace("__FIELD_DATA__", json.dumps(data, allow_nan=False, separators=(",", ":")))
    )


if __name__ == "__main__":
    main()
