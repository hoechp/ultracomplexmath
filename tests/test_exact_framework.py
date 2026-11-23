import json
import re
from fractions import Fraction as F
from pathlib import Path

import pytest

from examples.four_bar import BARS, BLOCKED_TRIAL, PINS, assemblies, samples
from ultracomplexmath import (
    BarFramework2D,
    DomainError,
    ExactComplex,
    ExactDual,
    InconsistentSystemError,
    SingularSystemError,
    circle_intersection2d,
    orientation2d,
)


def squared(a, b):
    return sum((u - v) ** 2 for u, v in zip(a, b, strict=True))


@pytest.mark.parametrize(
    "a,r,b,s,kind,points",
    [
        ((0, 0), 25, (6, 0), 25, "pair", ((3, 4), (3, -4))),
        ((0, 0), 25, (0, -6), 25, "pair", ((4, -3), (-4, -3))),
        ((0, 0), 9, (4, 0), 1, "point", ((3, 0),)),
        ((0, 0), 9, (2, 0), 1, "point", ((3, 0),)),
        ((0, 0), 9, (0, 0), 1, "empty", ()),
        ((0, 0), 9, (1, 0), 1, "empty", ()),
        ((0, 0), 9, (5, 0), 1, "empty", ()),
        ((0, 0), 0, (0, 0), 0, "point", ((0, 0),)),
        ((0, 0), 0, (3, 4), 25, "point", ((0, 0),)),
        ((0, 0), 0, (1, 0), 0, "empty", ()),
        ((0, 0), 0, (0, 1), 4, "empty", ()),
    ],
)
def test_circle_incidence(a, r, b, s, kind, points):
    cut = circle_intersection2d(a, r, b, s)
    assert cut.kind == kind
    assert cut.rational_points() == points
    for p in points:
        assert squared(a, p) == r and squared(b, p) == s
    swapped = circle_intersection2d(b, s, a, r)
    assert swapped.rational_points() == points[::-1]
    if kind == "pair":
        assert orientation2d(a, b, points[0]) > 0


def test_circle_irrational_pairs_and_infinite_families_are_distinct():
    cut = circle_intersection2d((0, 0), 1, (1, 0), 1)
    assert cut.kind == "pair"
    assert (cut.midpoint, cut.direction, cut.radicand) == ((F(1, 2), 0), (0, 1), F(3, 4))
    with pytest.raises(DomainError, match="irrational"):
        cut.rational_points()
    infinite = circle_intersection2d((1, 2), 4, (1, 2), 4)
    assert infinite.kind == "coincident"
    with pytest.raises(DomainError, match="infinitely"):
        infinite.rational_points()
    with pytest.raises(ValueError, match="nonnegative"):
        circle_intersection2d((0, 0), -1, (2, 3), 2)
    with pytest.raises(TypeError):
        circle_intersection2d((0, 0), 1.0, (2, 3), 2)


def test_nearly_tangent_after_large_translation():
    o, h = 10**150, F(1, 10**120)
    for shift, expected in [(-h, "pair"), (0, "point"), (h, "empty")]:
        assert circle_intersection2d((o, o), 1, (o + 2 + shift, o), 1).kind == expected


def dual_rates(points, speeds):
    jets = [
        tuple(ExactDual(x, v) for x, v in zip(p, w, strict=True))
        for p, w in zip(points, speeds, strict=True)
    ]
    return tuple((squared(jets[i], jets[j]) / 2).imag for i, j in BARS)


def verify_acceleration(framework, velocities, accelerations):
    # Quadratic coefficient of each squared bar length along p+t*v+t²*a/2.
    for i, j in framework.bars:
        coefficient = squared(velocities[i], velocities[j]) + sum(
            (framework.points[i][k] - framework.points[j][k])
            * (accelerations[i][k] - accelerations[j][k])
            for k in (0, 1)
        )
        assert coefficient == 0
    assert all(accelerations[i] == (0, 0) for i in framework.pins)


@pytest.mark.parametrize("x,ratio", [(1, -2), (-1, F(-1, 2))])
def test_toggle_tangent_cone_against_both_finite_branches(x, ratio):
    framework = BarFramework2D(((0, 0), (x, 0), (3 + x, 0), (3, 0)), BARS, pins=PINS)
    with pytest.raises(SingularSystemError):
        framework.solve_velocity({1: (0, 1)})
    with pytest.raises(InconsistentSystemError):
        framework.solve_velocity({1: (1, 0)})
    assert len(framework.velocity_basis()) == 2
    assert not any(framework.first_order_residuals(BLOCKED_TRIAL))
    for v in (F(-1, 2), 0, 2):
        for w in (1, 0, v, ratio * v):
            speeds = ((0, 0), (0, v), (0, w), (0, 0))
            assert not any(framework.first_order_residuals(speeds))
            if (w - v) * (w - ratio * v):
                with pytest.raises(InconsistentSystemError, match="second-order"):
                    framework.acceleration_for(speeds)
            else:
                verify_acceleration(framework, speeds, framework.acceleration_for(speeds))


@pytest.mark.parametrize("n", range(-6, 7))
def test_packed_assemblies_against_reflection_and_implicit_constraints(n):
    t = F(n, 4)
    b = ExactComplex((1 - t * t) / (1 + t * t), 2 * t / (1 + t * t))
    vb = ExactComplex(0, 1) * b
    # Independent Euclidean reflection in the line D → B via the dot product.
    d = ExactComplex(3)
    line = b - d
    projection = (b.real * line.real + b.imag * line.imag) / line.determinant
    reflected = d + 2 * projection * line - b
    expected = (d + b, reflected)
    for (c, vc), known in zip(assemblies(b).channels(), expected, strict=True):
        assert c == known and c in [
            ExactComplex(*p)
            for p in circle_intersection2d((b.real, b.imag), 9, (3, 0), 1).rational_points()
        ]
        points = ((0, 0), (b.real, b.imag), (c.real, c.imag), (3, 0))
        framework = BarFramework2D(points, BARS, pins=PINS)
        speeds = ((0, 0), (vb.real, vb.imag), (vc.real, vc.imag), (0, 0))
        assert (
            framework.first_order_residuals(speeds)[:3] == dual_rates(points, speeds) == (0, 0, 0)
        )
        assert len(framework.velocity_basis()) == (1 if b.imag else 2)
        verify_acceleration(framework, speeds, framework.acceleration_for(speeds))
        reference = BarFramework2D(((0, 0), (1, 0), (4, 0), (3, 0)), BARS, pins=PINS)
        assert not any(reference.position_residuals(points))
        if b.imag:
            assert framework.solve_velocity({1: speeds[1]}) == speeds
            # Independent implicit derivative from both output rod constraints.
            hx, hy = c.real - b.real, c.imag - b.imag
            kx, ky = c.real - 3, c.imag
            rate = hx * vb.real + hy * vb.imag
            det = hx * ky - hy * kx
            assert vc == ExactComplex(ky * rate / det, -kx * rate / det)


def test_free_rigid_triangle_pins_and_validation():
    pts = [[0, 0], [3, 0], [0, 4]]
    edges = ((0, 1), (1, 2), (2, 0))
    free = BarFramework2D(pts, edges)
    pts[1][0] = 12
    assert free.points[1] == (3, 0)
    assert len(free.velocity_basis()) == 3
    fixed = BarFramework2D(free.points, edges, pins=(0, 1))
    assert fixed.velocity_basis() == ()
    assert fixed.solve_velocity({}) == ((0, 0),) * 3
    assert fixed.position_residuals([(1, 1), (4, 1), (1, 5)]) == (0, 0, 0, 1, 1, 1, 1)
    assert fixed.position_residuals([(0, 0), (0, 0), (0, 4)])[:3] == (F(-9, 2), F(-9, 2), 0)
    with pytest.raises(ValueError, match="per joint"):
        fixed.position_residuals([])
    with pytest.raises(ValueError, match="index"):
        fixed.solve_velocity({-1: (0, 1)})
    with pytest.raises(InconsistentSystemError):
        fixed.solve_velocity({0: (0, 1)})
    trial = [(0, 0), (1, 0), (-2, 4)]
    assert fixed.first_order_residuals(trial) == (3, 25, 16, 0, 0, 1, 0)
    with pytest.raises(InconsistentSystemError, match="first-order"):
        fixed.acceleration_for(trial)
    with pytest.raises(ValueError, match="per joint"):
        fixed.acceleration_for(trial[:1])
    with pytest.raises(TypeError):
        fixed.first_order_residuals([(0.0, 0), *trial[1:]])
    for bars, pins in [([], ()), ([(0, 0)], ()), ([(0, -1)], ()), (edges, (3,)), (edges, (False,))]:
        with pytest.raises(ValueError):
            BarFramework2D(pts, bars, pins=pins)


def test_committed_offline_experiment_matches_exact_backend():
    html = (Path(__file__).resolve().parents[1] / "docs/gallery/four-bar.html").read_text()
    match = re.search(
        r'<script id="samples" type="application/json">\s*(.*?)\s*</script>', html, re.S
    )
    assert match
    data = json.loads(match[1])
    assert data == samples()
    assert len(data) == 65 and data[0] == data[-1]
    assert [k for k, item in enumerate(data) if item["closures"] == 1] == [0, 32, 64]
