"""Build the offline field, quadric, polarization, roots and sound experiments."""

import json
import math
from fractions import Fraction as F
from pathlib import Path

from ultracomplexmath import (
    CIRCULAR,
    HYPERBOLIC,
    PARABOLIC,
    QEPS,
    QI,
    QJ,
    QONE,
    QZERO,
    ExactComplex,
    ExactPolynomial,
    ExactStokes,
    ModeOperator,
    PolynomialCauchyField,
    ProjectivePoint,
    SegreQuadricPoint,
)

from .comb_filter import comb_response, group_delays

ROOT = Path(__file__).resolve().parents[1]
PLUS, MINUS = (QONE + QJ) / 2, (QONE - QJ) / 2
SAMPLE_RATE, DELAY = 48000, 48


def root_samples():
    data = []
    for label, value in (
        ("1", QONE),
        ("−1", -QONE),
        ("(1+j)/2", PLUS),
        ("0", QZERO),
        ("ε", QEPS),
        ("2", 2 * QONE),
    ):
        family = value.square_roots()
        p, m = family.sheet_counts
        samples = []
        for k in range(-2, 3):
            free = ExactComplex(k, 1 if k else 0)
            roots = [
                family.at(
                    i,
                    j,
                    plus_tangent=free if p == 1 else ExactComplex(),
                    minus_tangent=free if m == 1 else ExactComplex(),
                )
                for i in range(p)
                for j in range(m)
            ]
            assert all(root * root == value for root in roots)
            samples.append([[str(c) for c in root.coefficients] for root in roots])
        data.append(
            dict(
                label=label,
                count="∞" if family.count == math.inf else str(family.count),
                sheets=family.sheet_counts,
                samples=samples,
            )
        )
    return data


def field_samples():
    xs = [F(k, 20) for k in range(-30, 31)]
    ys = [F(k, 8) for k in range(-6, 7)]
    trace, normal = ExactPolynomial([1, 0, -2, 0, 1]), ExactPolynomial([0, F(1, 2)])
    fields = [
        PolynomialCauchyField(plane, trace, normal) for plane in (CIRCULAR, HYPERBOLIC, PARABOLIC)
    ]
    return dict(
        x=list(map(float, xs)),
        y=list(map(float, ys)),
        slices=[[[float(field(x, y)) for x in xs] for field in fields] for y in ys],
    )


def quadric_samples():
    axis = [F(k, 4) for k in range(-4, 5)]
    rows = []
    for a in axis:
        row = []
        for b in axis:
            # Tangent da=db=1 on this real slice of the complex surface.
            point = ProjectivePoint((a + QEPS) * PLUS + (b + QEPS) * MINUS, QONE)
            q = SegreQuadricPoint.from_projective(point)
            assert point.equivalent(q.to_projective())
            row.append([float(c.real) for c in (q.sv, q.tu, q.su)] + [float(q.su.eps)])
        rows.append(row)
    return rows


def phase_circle(steps):
    unit = ExactComplex(0, 1)
    for quarter in range(4):
        for k in range(steps):
            p = CIRCULAR.cayley(F(k, steps))
            yield unit**quarter * ExactComplex(p.real, p.imag)
    yield ExactComplex(1)


def light_samples(phases):
    result = []
    for fraction in (0, F(1, 2), 1):
        source = ExactStokes(2, 0, 2 * fraction, 0)
        curve = []
        for phase in phases:
            factor = phase.to_ultra() * (1 + QI * QEPS)
            plate = ModeOperator.from_matrix(factor, QZERO, QZERO, QONE)
            out = source.through(plate)
            curve.append(
                [
                    float(out.s2.real / 2),
                    float(out.s3.real / 2),
                    float(out.s2.eps / 2),
                    float(out.s3.eps / 2),
                ]
            )
        result.append(curve)
    return result


def sound_samples(phases, angles):
    curves = []
    for gain in (F(1, 2), F(1)):
        curve = []
        for phase in phases:
            h = comb_response(phase.conjugate(), DELAY, gain)
            powers = [float(z.determinant) for z, _ in h.channels()]
            delays = [None if d is None else float(d) for d in group_delays(h)]
            curve.append(powers + delays)
        curves.append(curve)
    hz = [round((1 + a / math.tau) * SAMPLE_RATE / DELAY, 9) for a in angles]
    return dict(hz=hz, curves=curves, delay=DELAY, rate=SAMPLE_RATE)


def samples():
    phases = list(phase_circle(8))
    angles = [math.atan2(p.imag, p.real) % math.tau for p in phases[:-1]] + [math.tau]
    return dict(
        roots=root_samples(),
        field=field_samples(),
        quadric=quadric_samples(),
        degrees=[round(math.degrees(a), 9) for a in angles],
        light=light_samples(phases),
        sound=sound_samples(phases, angles),
    )


def render(output):
    template = Path(__file__).with_suffix(".html").read_text(encoding="utf-8")
    data = json.dumps(samples(), separators=(",", ":"), allow_nan=False)
    output.write_text(template.replace("__DATA__", data), encoding="utf-8")


if __name__ == "__main__":
    render(ROOT / "docs/gallery/five-experiments.html")
