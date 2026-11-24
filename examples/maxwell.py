"""Generate the Maxwell laboratory, including linked electric lines at t=0."""

import argparse
import json
import math
from fractions import Fraction as F
from itertools import pairwise
from pathlib import Path

from ultracomplexmath import CIRCULAR, MaxwellMode

ROOT = Path(__file__).resolve().parents[1]
# Rational stereographic seeds, each on a different electric field line.
SEEDS = ((0, F(1, 2), 0), (0, 1, 0), (F(2, 3), 1, F(1, 2)), (F(-2, 3), 1, F(-1, 3)))


def fibers(steps=24):
    """Stereographic images of exact great circles on S³, in the direction of E."""
    phases = []
    for quarter in range(4):
        for k in range(steps):
            p = CIRCULAR.cayley(F(k, steps))
            c, s = p.real, p.imag
            for _ in range(quarter):
                c, s = -s, c
            phases.append((c, s))
    lines = []
    for x, y, z in SEEDS:
        r2 = x * x + y * y + z * z
        q = tuple(F(v) / (1 + r2) for v in (2 * x, 2 * y, 2 * z, r2 - 1))
        velocity = (q[3], q[2], -q[1], -q[0])
        points = []
        for c, s in phases:
            a, b, d, h = [c * v + s * w for v, w in zip(q, velocity, strict=True)]
            points.append((a / (1 - h), b / (1 - h), d / (1 - h)))
        lines.append([*points, points[0]])
    return lines


def crossing_link(left, right):
    """Signed inter-component crossings in a generic rational planar projection."""

    def project(p):
        x, y, z = p
        return x + z / 7, y + z / 11, z

    def det(x, y, u, v):
        return x * v - y * u

    a, b = [list(map(project, line)) for line in (left, right)]
    total = 0
    for (x, y, z), (X, Y, Z) in pairwise(a):
        dx, dy = X - x, Y - y
        for (u, v, w), (U, V, W) in pairwise(b):
            ex, ey = U - u, V - v
            denominator = det(dx, dy, ex, ey)
            if not denominator:
                if det(u - x, v - y, dx, dy) == 0:
                    raise ValueError("Collinear projected edges require a different view")
                continue
            t, h = det(u - x, v - y, ex, ey) / denominator, det(u - x, v - y, dx, dy) / denominator
            if 0 <= t <= 1 and 0 <= h <= 1:
                if t in (0, 1) or h in (0, 1):
                    raise ValueError("Projected vertex crossing requires a different view")
                oriented = denominator * (z + t * (Z - z) - w - h * (W - w))
                if not oriented:
                    raise ValueError("Curves intersect")
                total += 1 if oriented > 0 else -1
    if total % 2:
        raise ValueError("Linking count requires closed disjoint polygons")
    return total // 2


def presets():
    return {
        "standing": [MaxwellMode((1, 0, 0), (0, 1, 0), (0, 0, 0))],
        "traveling": [MaxwellMode.traveling((0, 0, 1), (1, 1j, 0))],
        "crossing": [
            MaxwellMode.traveling((2, 2, 1), (1, -1, 0)),
            MaxwellMode.traveling((0, 1, 0), (0.6j, 0, 0.6)),
            MaxwellMode.traveling((1, 0, 0), (0, 0.4 + 0.2j, 0)),
        ],
    }


def mode_data(mode):
    k = mode.wavevector

    # Coefficients of cos(|k|t) and sin(|k|t) for both ordinary complex fields.
    def fields(amplitude):
        return [[round(v, 12) for v in (z.real, z.i, z.ij, -z.j)] for z in amplitude]

    return [k, fields(mode.spectrum(0)), fields(mode.spectrum(math.pi / (2 * math.hypot(*k))))]


def render(output):
    curves = fibers()
    links = [crossing_link(curves[0], line) for line in curves[1:]]
    assert all(abs(n) == 1 for n in links)
    data = dict(
        modes={key: list(map(mode_data, value)) for key, value in presets().items()},
        curves=[
            [[round(float(coordinate), 8) for coordinate in p] for p in line] for line in curves
        ],
        links=links,
    )
    source = Path(__file__).with_suffix(".html").read_text(encoding="utf-8")
    output.write_text(
        source.replace("__DATA__", json.dumps(data, separators=(",", ":"))), encoding="utf-8"
    )


def figure(path):
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D

    fig = plt.figure(figsize=(10, 5.0), facecolor="#102532", layout="constrained")
    ax = fig.add_subplot(121, projection="3d", facecolor="#102532")
    colors = ("#73e2c1", "#ffac76", "#baaeff", "#f8da85")
    for line, color in zip(fibers(), colors, strict=True):
        x, y, z = zip(*line, strict=True)
        ax.plot(list(map(float, x)), list(map(float, y)), list(map(float, z)), color=color, lw=2.6)
    ax.set_box_aspect((1, 1, 1))
    ax.set_axis_off()
    ax.view_init(24, -48)
    ax.set_title("Linked light", color="white", fontsize=21, loc="left")
    ax.text2D(
        0.02,
        0.03,
        "Four electric field lines · Hopfion at t = 0",
        transform=ax.transAxes,
        color="white",
        fontsize=11,
    )
    bx = fig.add_subplot(122, facecolor="#102532")
    xs = [-math.pi + math.tau * k / 160 for k in range(161)]
    mode = presets()["standing"][0]
    samples = [mode.at((x, 0, 0), math.pi / 4) for x in xs]
    for values, color in (
        ([s.electric[1].real ** 2 / 2 for s in samples], colors[0]),
        ([s.magnetic[2].real ** 2 / 2 for s in samples], colors[1]),
        ([s.poynting[0].real for s in samples], colors[2]),
    ):
        bx.plot(xs, values, color=color, lw=2.5)
    bx.set(
        xlim=(-math.pi, math.pi),
        ylim=(-0.3, 0.35),
        xlabel="Position x  ·  ct = π/4",
        xticks=[-math.pi, 0, math.pi],
        xticklabels=["−π", "0", "π"],
    )
    bx.set_title("Where the energy goes", color="white", fontsize=18, loc="left")
    bx.tick_params(colors="#c4d4dd")
    bx.xaxis.label.set_color("white")
    for spine in bx.spines.values():
        spine.set_color("#41606b")
    bx.axhline(0, color="#77909b", lw=0.8, zorder=0)
    bx.legend(
        [Line2D([], [], color=c) for c in colors[:3]],
        ["Electric energy", "Magnetic energy", "Signed energy flux"],
        fontsize=9,
        loc="lower left",
        frameon=False,
        labelcolor="white",
    )
    fig.savefig(path, dpi=140, facecolor=fig.get_facecolor())
    plt.close(fig)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--figure", action="store_true")
    args = parser.parse_args()
    render(ROOT / "docs/gallery/maxwell.html")
    if args.figure:
        figure(ROOT / "docs/gallery/assets/maxwell.png")
