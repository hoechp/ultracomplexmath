"""Metric, topology and surface-calculus checks against independent formulas."""

import math

import pytest

from ultracomplexmath import (
    EPS,
    CoordinateSpace,
    I,
    ParametricSurface,
    Ultra,
    UltraField,
    mobius_strip,
    torus,
)


def test_stretched_plane_gradient_and_area_are_geometric():
    plane = ParametricSurface(
        lambda p: (3 * p[0], 4 * p[1], 0),
        lambda p: ((3, 0), (0, 4), (0, 0)),
        ((0, 1), (0, 2)),
    )
    ambient = UltraField.from_formula("(x**2+y**2)*(1+eps*i)")
    f = plane.pullback(ambient)
    p = plane.space.point(0.5, 0.25)
    assert plane.metric(p) == ((9, 0), (0, 16))
    assert plane.area_density(p) == 12
    gradient = plane.gradient(f, p)
    expected = (3 * (1 + EPS * I), 2 * (1 + EPS * I), Ultra())
    for result, wanted in zip(gradient, expected, strict=True):
        assert result.isclose(wanted, abs_tol=1e-10)
    assert plane.laplacian(f)(p).isclose(4 * (1 + EPS * I), abs_tol=1e-8)
    assert f.laplacian()(p).isclose(50 * (1 + EPS * I), abs_tol=1e-7)
    assert plane.integrate(UltraField.constant(1 + EPS * I, plane.space), shape=(4, 5)).isclose(
        24 * (1 + EPS * I), abs_tol=1e-12
    )


def test_torus_embedding_jacobian_metric_and_area():
    major, minor = 2.3, 0.7
    surface = torus(major, minor)
    for u, v in [(0, 0), (0.5, 1.2), (3.1, 4.7)]:
        p = surface.space.point(u, v, time=1.5)
        embedded = surface.coordinate_map(p)
        x, y, z = embedded.position
        assert embedded.time == 1.5
        assert (math.hypot(x, y) - major) ** 2 + z * z == pytest.approx(minor**2)
        metric = surface.metric(p)
        assert metric[0] == pytest.approx(((major + minor * math.cos(v)) ** 2, 0), abs=1e-14)
        assert metric[1] == pytest.approx((0, minor**2), abs=1e-14)
        assert surface.area_density(p) == pytest.approx(minor * (major + minor * math.cos(v)))
    area = surface.integrate(UltraField.constant(1, surface.space), shape=(12, 16))
    assert area.real == pytest.approx(4 * math.pi**2 * major * minor)


@pytest.mark.parametrize("surface", [torus(), mobius_strip()])
def test_analytic_surface_jacobians_against_embedding_differences(surface):
    p = (0.7, 0.3)
    h = 1e-5
    columns = []
    for a in range(2):
        left, right = list(p), list(p)
        left[a] -= h
        right[a] += h
        columns.append(
            [
                (y - x) / (2 * h)
                for x, y in zip(
                    surface.embedding(tuple(left)), surface.embedding(tuple(right)), strict=True
                )
            ]
        )
    for row, col in zip(surface.jacobian(p), zip(*columns, strict=True), strict=True):
        assert row == pytest.approx(col, abs=2e-10)


def test_torus_laplace_beltrami_against_closed_expressions():
    major, minor = 2.0, 0.65
    surface = torus(major, minor)
    mode = UltraField.from_formula("exp(2*i*u)*(1+eps*i*j)", space=surface.space)
    height = surface.pullback(UltraField.from_formula("z"))
    p = surface.space.point(0.7, 1.2)
    radial = major + minor * math.cos(p["v"])
    assert surface.laplacian(mode)(p).isclose(mode(p) * (-4 / radial**2), abs_tol=2e-8)
    v = p["v"]
    expected = -math.sin(v) / minor - math.cos(v) * math.sin(v) / radial
    assert surface.laplacian(height)(p).real == pytest.approx(expected, abs=2e-8)


def test_torus_seam_conditions_and_bad_half_angle():
    surface = torus()
    good = UltraField.from_formula(
        "exp(i*(2*u-3*v-t)+j*cos(u)/4)*(1+eps*sin(v))", space=surface.space
    )
    report = surface.check_seams(good, samples=7, times=(0, 0.7))
    assert report.comparisons == 28
    assert report.within(atol=1e-9)
    bad = UltraField.from_formula("exp(i*u/2)", space=surface.space)
    assert not surface.check_seams(bad).within()


def test_mobius_seam_values_derivatives_and_ambient_gradient_agree():
    surface = mobius_strip()
    f = UltraField.from_formula(
        "exp(i*(2*u-t)+j*v*cos(u/2))*(1+eps*v*sin(u/2))", space=surface.space
    )
    assert surface.check_seams(f, samples=9, times=(0, 1)).within(atol=2e-9)
    left = surface.space.point(0, 0.3, time=0.7)
    right = surface.space.point(math.tau, -0.3, time=0.7)
    assert surface.coordinate_map(left).position == pytest.approx(
        surface.coordinate_map(right).position, abs=1e-14
    )
    for a, b in zip(surface.gradient(f, left), surface.gradient(f, right), strict=True):
        assert a.isclose(b, abs_tol=2e-9)
    assert surface.laplacian(f)(left).isclose(surface.laplacian(f)(right), abs_tol=2e-7)
    bad = UltraField.from_formula("j*v", space=surface.space)
    assert not surface.check_seams(bad).within()
    same_values_bad_derivative = UltraField.from_formula("u*(u-2*pi)", space=surface.space)
    assert surface.check_seams(same_values_bad_derivative, derivatives=False).within()
    assert not surface.check_seams(same_values_bad_derivative).within()


def test_mobius_metric_and_integration_needs_no_normal_orientation():
    radius = 2
    surface = mobius_strip(radius, 0.4, time_axis=None)
    p = surface.space.point(1.1, 0.2)
    a = (radius + 0.2 * math.cos(1.1 / 2)) ** 2 + 0.2**2 / 4
    metric = surface.metric(p)
    assert metric[0] == pytest.approx((a, 0), abs=1e-14)
    assert metric[1] == pytest.approx((0, 1), abs=1e-14)
    assert surface.area_density(p) == pytest.approx(math.sqrt(a))
    f = UltraField.from_formula("v*sin(u/2)*(1+eps*i)", space=surface.space)
    # Reflection u -> 2*pi-u, v -> -v reverses height and preserves dA.
    assert surface.integrate(f, shape=(16, 16)).isclose(Ultra(), abs_tol=1e-13)


def test_surface_failures_are_explicit():
    for constructor in [lambda: torus(1, 1), lambda: torus(1, 0), lambda: mobius_strip(1, 2)]:
        with pytest.raises(ValueError):
            constructor()
    degenerate = ParametricSurface(
        lambda p: (p[0], p[0], 0), lambda p: ((1, 0), (1, 0), (0, 0)), ((0, 1), (0, 1))
    )
    with pytest.raises(ValueError, match="Degenerate"):
        degenerate.metric(degenerate.space.point(0.5, 0.5))
    surface = torus()
    with pytest.raises(ValueError):
        surface.gradient(UltraField.constant(1), surface.space.point(0, 0))
    with pytest.raises(ValueError):
        surface.metric(CoordinateSpace().point(0, 0, 0))
    with pytest.raises(ValueError):
        surface.integrate(UltraField.constant(1, surface.space), shape=(0, 2))
    with pytest.raises(ValueError):
        surface.integrate(UltraField.constant(1, surface.space), shape=(10, 10), max_points=99)
    with pytest.raises(ValueError):
        surface.check_seams(UltraField.constant(1, surface.space), samples=1)


def test_sheared_parameter_chart_requires_off_diagonal_metric_terms():
    plane = ParametricSurface(
        lambda p: (p[0] + 2 * p[1], p[1], 0),
        lambda p: ((1, 2), (0, 1), (0, 0)),
        ((0, 1), (0, 1)),
    )
    field = plane.pullback(UltraField.from_formula("(x*x+y*y)*(1+eps*i)"))
    p = plane.space.point(0.3, 0.4)
    assert plane.metric(p) == ((1, 2), (2, 5))
    expected = ((1 + EPS * I) * 2.2, (1 + EPS * I) * 0.8, Ultra())
    for actual, wanted in zip(plane.gradient(field, p), expected, strict=True):
        assert actual.isclose(wanted, abs_tol=1e-9)
    assert plane.laplacian(field)(p).isclose(4 * (1 + EPS * I), abs_tol=3e-8)
