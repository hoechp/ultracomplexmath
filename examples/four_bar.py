"""Generate the offline four-bar laboratory with exact positions and velocity tests.

Run python -m examples.four_bar from a checkout.
"""

import json
from fractions import Fraction
from pathlib import Path

from ultracomplexmath import (
    CIRCULAR,
    QEPS,
    QI,
    QJ,
    QONE,
    BarFramework2D,
    ExactComplex,
    InconsistentSystemError,
    circle_intersection2d,
)

ROOT = Path(__file__).resolve().parents[1]
BARS = ((0, 1), (1, 2), (2, 3))
PINS = (0, 3)
GROUND = ((0, 0), (3, 0))
ZERO = (0, 0)
BLOCKED_TRIAL = (ZERO, ZERO, (0, 1), ZERO)


def assemblies(crank: ExactComplex):
    """Both finite assembly laws and their derivatives per radian, packed into one value."""
    if crank.determinant != 1:
        raise ValueError("The crank must lie on the unit circle")
    u = crank.to_ultra() * (1 + QI * QEPS)
    selector = 3 * (QONE - QJ) / 2
    return 3 + (u - selector) / (1 - selector * u)


def coordinates(z):
    return (z.real, z.imag)


def trial(framework, velocity):
    if any(framework.first_order_residuals(velocity)):
        return "first-order failure"
    try:
        framework.acceleration_for(velocity)
    except InconsistentSystemError:
        return "second-order obstruction"
    return "compatible acceleration"


def sample(crank):
    b = coordinates(crank)
    vb = (-b[1], b[0])
    closures = circle_intersection2d(b, 9, GROUND[1], 1).rational_points()
    branches = []
    for body, tangent in assemblies(crank).channels():
        c = coordinates(body)
        vc = coordinates(tangent)
        framework = BarFramework2D((GROUND[0], b, c, GROUND[1]), BARS, pins=PINS)
        assert c in closures
        assert trial(framework, (ZERO, vb, vc, ZERO)) == "compatible acceleration"
        branches.append(
            {
                "c": list(map(str, c)),
                "vc": list(map(str, vc)),
                "dimension": len(framework.velocity_basis()),
                "trial": trial(framework, BLOCKED_TRIAL),
            }
        )
    assert {tuple(map(str, p)) for p in closures} == {tuple(item["c"]) for item in branches}
    return {
        "b": list(map(str, b)),
        "vb": list(map(str, vb)),
        "closures": len(closures),
        "branches": branches,
    }


def samples(steps=16):
    # Four quarter-turns. Each local Cayley parameter runs from 0 to 1.
    points = []
    for quadrant in range(4):
        rotation = ExactComplex(0, 1) ** quadrant
        for k in range(steps):
            factor = CIRCULAR.cayley(Fraction(k, steps))
            points.append(sample(rotation * ExactComplex(factor.real, factor.imag)))
    return [*points, points[0]]


def render(output):
    template = Path(__file__).with_suffix(".html").read_text()
    data = json.dumps(samples(), separators=(",", ":"))
    output.write_text(template.replace("__SAMPLES__", data))


if __name__ == "__main__":
    render(ROOT / "docs/gallery/four-bar.html")
