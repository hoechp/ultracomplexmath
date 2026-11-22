import math

import pytest

from ultracomplexmath import EPS, ONE, DomainError, I, J, NonInvertibleError, evaluate
from ultracomplexmath import geometry as g
from ultracomplexmath.numbers import Binary, Complex, Dual


@pytest.mark.parametrize("n", [2**53 + 1, 2**100 + 3, 10**400 + 1, -(2**100 + 1)])
def test_integer_exponents_preserve_all_bits(n):
    assert I**n == (ONE, I, -ONE, -I)[n % 4]
    assert (-ONE) ** n == (-ONE if n % 2 else ONE)
    assert J**n == (J if n % 2 else ONE)
    assert Complex(0, 1) ** n == (Complex(1), Complex(0, 1), Complex(-1), Complex(0, -1))[n % 4]
    for branch in (-3, 1, 20):
        assert Complex(0, 1).power(n, branch=branch) == Complex(0, 1) ** n
    assert Binary(0, 1).power(n) == (Binary(0, 1) if n % 2 else Binary(1))
    assert Dual(-1).power(n) == (Dual(-1) if n % 2 else Dual(1))


def test_integer_power_domains_and_bool():
    assert EPS ** (2**80) == 0 * ONE
    assert Complex().power(2, branch=1) == Complex()
    assert Complex().power(0, branch=-1) == Complex(1)
    with pytest.raises(TypeError):
        Complex(1).power(2, branch=True)
    with pytest.raises(NonInvertibleError):
        _ = EPS ** (-(2**80))
    for value in (ONE, Complex(1), Binary(1), Dual(1)):
        with pytest.raises(TypeError):
            _ = value**True
    for kind in (Complex, Binary, Dual):
        with pytest.raises(ValueError):
            kind(1).roots(True)


@pytest.mark.parametrize("scale", [1e-310, 1e-200, 1, 1e200, 1e308])
def test_normalization_and_projection_do_not_square_scale(scale):
    direction = (scale, scale, 0)
    assert g.unit(direction) == pytest.approx((1 / math.sqrt(2), 1 / math.sqrt(2), 0))
    assert g.project((1, 0, 2), direction) == pytest.approx((0.5, 0.5, 0))
    for kind in (Complex, Binary, Dual):
        projected = kind(1).part_in_direction(kind(scale, scale))
        assert (projected.real, projected.imag) == pytest.approx((0.5, 0.5))
        normal = kind(scale, scale).normalized()
        assert (normal.real, normal.imag) == pytest.approx((1 / math.sqrt(2),) * 2)
    assert evaluate("project(1, b)", {"b": scale * (ONE + I)}).isclose((ONE + I) / 2)


@pytest.mark.parametrize("scale", [1e-200, 1, 1e200, 1e307])
def test_complex_vector_angle_scaled_minkowski_radius(scale):
    angle, radius = g.angle_from_vector((2 * scale, 0, scale), Complex)
    assert radius == pytest.approx(math.sqrt(3) * scale, rel=1e-14, abs=0)
    assert angle.imag == pytest.approx(math.asinh(1 / math.sqrt(3)))


def test_small_angles_are_not_rounded_to_zero():
    theta = 1e-12
    assert g.angle((1, 0), (1, theta)) == pytest.approx(math.atan(theta), rel=1e-13, abs=0)
    assert g.angle((1, 0), (-1, theta)) == pytest.approx(math.pi - theta, abs=1e-15)
    with pytest.raises(DomainError):
        g.unit((0, 0))


@pytest.mark.parametrize("scale", [1e-200, 1, 1e200])
@pytest.mark.parametrize("a,b", [(2, 1), (-2, 1), (1, 2), (1, -2)])
def test_split_polar_forms_do_not_underflow_or_overflow_quadrance(scale, a, b):
    value = Binary(a * scale, b * scale)
    radius, sector, theta = value.hyperbolic_form()
    assert radius == pytest.approx(math.sqrt(3) * scale, rel=1e-14, abs=0)
    rebuilt = Binary.from_hyperbolic(radius, sector, theta)
    assert rebuilt.real == pytest.approx(value.real, rel=1e-14, abs=0)
    assert rebuilt.imag == pytest.approx(value.imag, rel=1e-14, abs=0)
