import math
from fractions import Fraction as F

import pytest

from ultracomplexmath import (
    CIRCULAR,
    HYPERBOLIC,
    PARABOLIC,
    DomainError,
    PlaneIsometry,
    PlanePolar,
    barycentric2d,
    circumcircle2d,
    incircle2d,
    line_intersection2d,
    metric_dot,
    metric_project,
    metric_reflect,
    orientation2d,
    segment_intersection2d,
)


@pytest.mark.parametrize("plane", [CIRCULAR, HYPERBOLIC, PARABOLIC])
@pytest.mark.parametrize("parameter", [F(-7, 3), F(-1, 3), 0, F(1, 2), F(5, 4)])
def test_exact_cayley_unit_quadrance_and_inverse(plane, parameter):
    rotor = plane.cayley(parameter)
    assert rotor.determinant == 1
    assert rotor * plane.cayley(-parameter) == plane.exact(1)
    # Independently check the defining rational function.
    u = plane.exact(0, 1)
    assert rotor == (1 + parameter * u) / (1 - parameter * u)


def test_three_geometries_have_distinct_angle_meanings():
    assert CIRCULAR.cayley(F(1, 2)) == CIRCULAR.exact(F(3, 5), F(4, 5))
    assert HYPERBOLIC.cayley(F(1, 2)) == HYPERBOLIC.exact(F(5, 3), F(4, 3))
    assert PARABOLIC.cayley(F(1, 2)) == PARABOLIC.exact(1, 1)
    assert CIRCULAR.polar(CIRCULAR.point(1, 1)).parameter == pytest.approx(math.pi / 4)
    assert HYPERBOLIC.polar(HYPERBOLIC.point(2, 1)).parameter == pytest.approx(math.atanh(0.5))
    assert PARABOLIC.polar(PARABOLIC.point(2, 1)).parameter == 0.5
    assert HYPERBOLIC.classify(HYPERBOLIC.exact(1, 1)) == "null"
    assert HYPERBOLIC.classify(HYPERBOLIC.exact(1, 2)) == "spacelike"
    assert HYPERBOLIC.classify(HYPERBOLIC.point(1e-300, 2e-300)) == "spacelike"
    assert PARABOLIC.classify(PARABOLIC.exact(0, 1)) == "null"
    for t in (-1, 1):
        with pytest.raises(DomainError):
            HYPERBOLIC.cayley(t)


@pytest.mark.parametrize("plane", [CIRCULAR, HYPERBOLIC, PARABOLIC])
def test_metric_projection_and_reflection(plane):
    value, direction = plane.exact(F(1, 3), F(7, 5)), plane.exact(2, 1)
    projected = metric_project(value, direction)
    rejected = value - projected
    assert metric_dot(rejected, direction) == 0
    reflected = metric_reflect(value, direction)
    assert reflected.determinant == value.determinant
    assert metric_reflect(reflected, direction) == value
    with pytest.raises(DomainError):
        metric_project(value, plane.exact())
    if plane is not CIRCULAR:
        null = plane.exact(1, 1) if plane is HYPERBOLIC else plane.exact(0, 1)
        with pytest.raises(DomainError):
            metric_project(value, null)


@pytest.mark.parametrize("plane", [CIRCULAR, HYPERBOLIC, PARABOLIC])
@pytest.mark.parametrize("reflected", [False, True])
def test_exact_affine_isometries_and_independent_matrix(plane, reflected):
    transform = PlaneIsometry(plane.cayley(F(1, 3)), plane.exact(F(3, 7), F(2, 9)), reflected)
    second = PlaneIsometry(plane.cayley(F(-2, 5)), plane.exact(3, 4), True)
    p, q = plane.exact(4, 5), plane.exact(-3, 2)
    image = transform(p)
    assert (image - transform(q)).determinant == (p - q).determinant
    assert transform.inverse()(image) == p
    assert (transform @ second)(p) == transform(second(p))
    assert (second @ transform)(p) == second(transform(p))
    coordinates = (p.real, p.imag, F(1))
    matrix_image = tuple(
        sum(a * b for a, b in zip(row, coordinates, strict=True))
        for row in transform.homogeneous_matrix()
    )
    assert matrix_image == (image.real, image.imag, 1)


@pytest.mark.parametrize("plane", [CIRCULAR, HYPERBOLIC, PARABOLIC])
@pytest.mark.parametrize("a,b", [(2, 1), (-2, 1), (1, 2), (1, -2)])
def test_polar_sectors_round_trip_and_relative_angle(plane, a, b):
    value = plane.point(a, b)
    form = plane.polar(value)
    rebuilt = form.reconstruct()
    assert (rebuilt.real, rebuilt.imag) == pytest.approx((a, b))
    end = value * plane.rotor(0.25)
    relative = plane.angle_between(value, end)
    assert relative.parameter == pytest.approx(0.25)
    assert relative.radius == pytest.approx(1)
    assert relative.sector == (1, 0)


def test_geometry_domain_boundaries():
    with pytest.raises(TypeError):
        metric_dot(CIRCULAR.exact(1), HYPERBOLIC.exact(1))
    with pytest.raises(TypeError):
        PlaneIsometry(CIRCULAR.exact(1), CIRCULAR.point())
    with pytest.raises(DomainError):
        PlaneIsometry(CIRCULAR.exact(2), CIRCULAR.exact())
    with pytest.raises(TypeError):
        CIRCULAR.polar(CIRCULAR.exact(1, 1))
    with pytest.raises(DomainError):
        HYPERBOLIC.polar(HYPERBOLIC.point(1, 1))
    with pytest.raises(DomainError):
        PlanePolar("dual", 1, 0, (0, 1))


def test_exact_predicates_retain_tiny_separations_after_huge_translations():
    origin = 10**100
    a, b = (origin, origin), (origin + 1, origin + 1)
    c = (origin + 2, origin + 2 + F(1, 10**100))
    assert orientation2d(a, b, c) == F(1, 10**100)
    assert orientation2d(a, c, b) == -F(1, 10**100)
    assert line_intersection2d((0, 0), (3, 2), (1, 0), (0, 1)) == (F(3, 5), F(2, 5))
    with pytest.raises(DomainError):
        line_intersection2d((0, 0), (1, 1), (2, 2), (3, 3))


@pytest.mark.parametrize(
    "a,b,c,d,expected",
    [
        ((0, 0), (2, 2), (0, 2), (2, 0), ((1, 1),)),
        ((0, 0), (1, 1), (2, 2), (3, 3), ()),
        ((0, 0), (2, 2), (1, 1), (3, 3), ((1, 1), (2, 2))),
        ((0, 0), (1, 1), (1, 1), (2, 0), ((1, 1),)),
        ((1, 1), (1, 1), (0, 0), (2, 2), ((1, 1),)),
        ((1, 2), (1, 2), (0, 0), (2, 2), ()),
        ((1, 1), (1, 1), (2, 2), (2, 2), ()),
        ((1, 1), (1, 1), (1, 1), (1, 1), ((1, 1),)),
        ((0, 3), (0, 0), (0, 4), (0, 2), ((0, 2), (0, 3))),
    ],
)
def test_exact_segment_intersections(a, b, c, d, expected):
    assert segment_intersection2d(a, b, c, d) == expected
    assert segment_intersection2d(d, c, b, a) == expected


def test_barycentric_circles_and_winding_independent_incircle():
    triangle = ((0, 0), (2, 0), (0, 2))
    point = (F(1, 3), F(2, 3))
    weights = barycentric2d(point, *triangle)
    assert sum(weights) == 1
    assert (
        tuple(sum(w * p[k] for w, p in zip(weights, triangle, strict=True)) for k in range(2))
        == point
    )
    center, radius_squared = circumcircle2d(*triangle)
    assert center == (1, 1) and radius_squared == 2
    for vertices in (triangle, triangle[::-1]):
        assert incircle2d((1, 1), *vertices) == 1
        assert incircle2d((2, 2), *vertices) == 0
        assert incircle2d((3, 3), *vertices) == -1
    with pytest.raises(DomainError):
        circumcircle2d((0, 0), (1, 1), (2, 2))
    with pytest.raises(TypeError):
        orientation2d((0.1, 0), (1, 1), (2, 2))
