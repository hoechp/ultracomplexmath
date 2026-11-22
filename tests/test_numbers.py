import cmath
import math

import pytest

from ultracomplexmath import DomainError, NonInvertibleError, Ultra
from ultracomplexmath.coordinates import Cartesian2D, Polar2D
from ultracomplexmath.numbers import Binary, Complex, Dual


@pytest.mark.parametrize("kind,square", [(Complex, -1), (Binary, 1), (Dual, 0)])
def test_algebra_arithmetic(kind, square):
    a, b = kind(3, 2), kind(2, -1)
    assert a * b == kind(6 - 2 * square, 1)
    assert a + b == kind(5, 1)
    assert (a / b * b).isclose(a)
    assert (1 / a * a).isclose(1)
    assert a.conjugate() == kind(3, -2)
    assert (a**-3 * a**3).isclose(1)
    assert a**0 == kind(1)
    assert a.determinant == 9 - 4 * square
    assert kind.from_ultra(a.to_ultra()) == a
    assert kind.parse(str(a)) == a
    assert 2 ** kind(3) == kind(8)
    assert kind(1e-310) / kind(1e-310) == kind(1)


@pytest.mark.parametrize("kind", [Complex, Binary, Dual])
@pytest.mark.parametrize("scale", [1e-120, 1e120])
def test_inverse_scaling(kind, scale):
    a = kind(3 * scale, scale)
    assert (a * a.inverse()).isclose(1)


@pytest.mark.parametrize("value", [Binary(1, 1), Dual(0, 2), Complex()])
def test_zero_divisors(value):
    with pytest.raises(NonInvertibleError):
        value.inverse()


@pytest.mark.parametrize(
    "name", "exp sin cos tan sinh cosh tanh asin acos atan asinh acosh atanh".split()
)
def test_complex_reference(name):
    z = complex(0.4, 0.2)
    assert complex(getattr(Complex(z.real, z.imag), name)()) == pytest.approx(
        getattr(cmath, name)(z)
    )


@pytest.mark.parametrize(
    "name,x",
    [
        ("sin", 0.4),
        ("cos", 0.4),
        ("exp", 0.4),
        ("log", 2),
        ("sqrt", 2),
        ("asin", 0.4),
        ("acosh", 2),
        ("atanh", 0.4),
    ],
)
def test_dual_derivative(name, x):
    h = 1e-6
    scalar = getattr(math, name)
    expected = (scalar(x + h) - scalar(x - h)) / (2 * h)
    result = getattr(Dual(x, 2), name)()
    assert result.real == pytest.approx(scalar(x))
    assert result.imag == pytest.approx(2 * expected)


@pytest.mark.parametrize(
    "value", [Complex(3, 2), Binary(3, 2), Binary(-3, -2), Dual(3, 2), Dual(-3, 2)]
)
@pytest.mark.parametrize("degree", [1, 2, 3, 4, 5])
def test_roots_satisfy_equation(value, degree):
    roots = value.roots(degree)
    for root in roots.values:
        assert (root**degree).isclose(value)
    if value.real > 0 or isinstance(value, Complex) or degree % 2:
        assert roots.values


def test_root_cardinality_and_domain():
    assert len(Complex(-1).roots(4).values) == 4
    assert len(Binary(4).roots(2).values) == 4
    assert len(Binary(1, 1).roots(2).values) == 2
    assert len(Dual(4, 4).roots(2).values) == 2
    assert not Dual(0, 1).roots(2).values
    assert Dual().roots(2).at(23) ** 2 == Dual()
    assert Complex(4).rational_power(1, 2).values[0].isclose(2)
    for value in (Binary(-1), Dual(-1)):
        with pytest.raises(DomainError):
            value.log()
    with pytest.raises(TypeError):
        _ = Complex(1) + Binary(1)
    with pytest.raises(DomainError):
        Binary.from_ultra(Ultra(i=1))


@pytest.mark.parametrize("value", [Binary(3, 2), Binary(-3, 2), Binary(2, 3), Binary(2, -3)])
def test_split_forms(value):
    assert Binary.from_diagonal(*value.diagonal) == value
    assert Binary.from_null_basis(*value.null_basis) == value
    assert Binary.from_hyperbolic(*value.hyperbolic_form()).isclose(value)


def test_geometry_branches_and_serialization():
    a = Complex(2, 3)
    assert a.log(branch=2).imag == pytest.approx(a.angle + 4 * math.pi)
    assert a.log(branch=2).exp().isclose(a)
    assert a.power(0.5, branch=1).isclose(-a.sqrt())
    assert a.part_in_direction(Complex(1)) == Complex(2)
    assert a.part_orthogonal_to(Complex(1)) == Complex(0, 3)
    assert a.mirrored_radial_to(Complex(1)) == Complex(-2, 3)
    first, second = a.hilbert(Complex(-1, 4))
    assert first.dot(second) == pytest.approx(0, abs=1e-12)
    assert a.turned_by(math.pi / 2).isclose(Complex(-3, 2))
    for kind in (Complex, Binary, Dual):
        precise = kind(1.23456789012345, -1.234e-100)
        assert kind.parse(str(precise)) == precise
    for value in (Dual(), Dual(1, 2), Dual(-3, 1)):
        assert Dual.from_unit_sphere(*value.unit_sphere_position()).isclose(value)
    assert Cartesian2D(3, 4).polar.radius == 5
    assert Polar2D(-2, 0).cartesian.x == pytest.approx(-2)
    assert Complex(0).color() == (255, 255, 255)


def test_euler_component_factorization():
    assert 2 ** Ultra(3) == Ultra(8)
    assert Dual(1, 1e200).determinant == 1
    value = Ultra(3, 0.2, 0.4, 0.1, 0.3, -0.1, 0.2, 0.05)
    product = Ultra(1)
    for i in range(8):
        product *= (Ultra.unit(i) * value.euler_angle_component(i)).exp()
    assert product.isclose(value)
    assert value.euler_length == math.exp(value.log().real)
