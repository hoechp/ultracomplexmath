import cmath
import math
from dataclasses import FrozenInstanceError

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from ultracomplexmath import (
    EPS,
    ONE,
    ZERO,
    DomainError,
    I,
    J,
    NonFiniteError,
    NonInvertibleError,
    Ultra,
)


def close(actual, expected, **kwargs):
    assert actual.isclose(expected, **kwargs), (
        actual.coefficients,
        Ultra.coerce(expected).coefficients,
    )


# Signed one-based basis indices: zero means the zero element. Kept as a
# literal oracle independent of the implementation's bit-mask multiplication.
TABLE = [
    [1, 2, 3, 4, 5, 6, 7, 8],
    [2, 1, 4, 3, 6, 5, 8, 7],
    [3, 4, -1, -2, 7, 8, -5, -6],
    [4, 3, -2, -1, 8, 7, -6, -5],
    [5, 6, 7, 8, 0, 0, 0, 0],
    [6, 5, 8, 7, 0, 0, 0, 0],
    [7, 8, -5, -6, 0, 0, 0, 0],
    [8, 7, -6, -5, 0, 0, 0, 0],
]


@pytest.mark.parametrize("a", range(8))
@pytest.mark.parametrize("b", range(8))
def test_every_basis_product(a, b):
    code = TABLE[a][b]
    expected = ZERO if code == 0 else Ultra.unit(abs(code) - 1) * (1 if code > 0 else -1)
    assert Ultra.unit(a) * Ultra.unit(b) == expected


numbers = st.builds(Ultra, *(st.integers(-5, 5) for _ in range(8)))


@given(numbers, numbers, numbers)
@settings(max_examples=120, derandomize=True)
def test_algebra_laws(a, b, c):
    assert a * b == b * a
    assert (a * b) * c == a * (b * c)
    assert a * (b + c) == a * b + a * c
    assert a * ONE == a
    assert a + ZERO == a
    assert Ultra.from_channels(*a.channels()) == a


@given(numbers)
@settings(max_examples=100, derandomize=True)
def test_inverse_law(a):
    if a.is_invertible:
        close(a * a.inverse(), ONE)
        close(a / a, ONE)
        close(a.inverse().inverse(), a)
    else:
        with pytest.raises(NonInvertibleError):
            a.inverse()


def test_false_singularity_in_legacy_conjugate_algorithm():
    # Java sign-flipping includes factors that are zero divisors even though a
    # has two nonzero body channels (2 and 2i). Its conjugate product is zero.
    a = Ultra(1, 1, 1, -1)
    assert a.inverse() == Ultra(0.25, 0.25, -0.25, 0.25)
    assert a * a.inverse() == ONE


@pytest.mark.parametrize("a", [ZERO, EPS, ONE + J, ONE - J, Ultra(*([0.2] * 8))])
def test_zero_divisors_are_explicit(a):
    assert not a.is_invertible
    with pytest.raises(NonInvertibleError):
        a.inverse()
    with pytest.raises(NonInvertibleError):
        ONE / a


def test_old_ultrabug_case_is_a_real_pole():
    a = Ultra(0.2, 0.2, 0.2, 0.2)
    assert a * (ONE - J) == ZERO
    for operation in (a.csc, a.cot, a.coth):
        with pytest.raises(NonInvertibleError):
            operation()
    close(a.sin() ** 2 + a.cos() ** 2, ONE)


def test_integer_powers_do_not_require_logarithms():
    assert EPS**2 == ZERO
    assert EPS**0 == ONE
    assert ZERO**0 == ONE  # documented convention
    assert ZERO**3 == ZERO
    assert (ONE + J) ** 3 == 4 * (ONE + J)
    assert I**-1 == -I
    assert Ultra(10) ** 3 == Ultra(1000)
    with pytest.raises(NonInvertibleError):
        EPS**-1


def test_embeddings_operators_and_immutability():
    assert Ultra.complex(2, 3) == 2 + 3 * I
    assert Ultra.split(2, 3) == 2 + 3 * J
    assert Ultra.dual(2, 3) == 2 + 3 * EPS
    assert (2 + 3j) + EPS == Ultra(2, 0, 3, 0, 1)
    assert 2 - I == Ultra.complex(2, -1)
    assert 1 / I == -I
    close(2**I, cmath.exp(1j * math.log(2)))
    with pytest.raises(FrozenInstanceError):
        ONE.real = 3
    assert {ONE: "one"}[Ultra(1)] == "one"
    assert Ultra(1) != Ultra(1 + 1e-12)
    assert Ultra(1).isclose(Ultra(1 + 1e-12))
    assert Ultra(1) != 1  # exact value equality only between Ultra instances


@pytest.mark.parametrize("bad", [math.inf, -math.inf, math.nan])
def test_nonfinite_rejected(bad):
    with pytest.raises(NonFiniteError):
        Ultra(bad)


@pytest.mark.parametrize("bad", [True, "2", [1, 2]])
def test_nonnumeric_rejected(bad):
    with pytest.raises(TypeError):
        Ultra(bad)


def test_input_validation():
    with pytest.raises(ValueError):
        Ultra.unit(-1)
    with pytest.raises(ValueError):
        Ultra.unit(True)
    with pytest.raises(ValueError):
        Ultra.from_coefficients([1, 2])
    with pytest.raises(ValueError):
        ONE.log(branches=(0, 0.5))
    with pytest.raises(ValueError):
        ONE.conjugate("x")


@pytest.mark.parametrize("scale", [1e-100, 1e100])
def test_inverse_without_127_factor_overflow(scale):
    a = Ultra(2, 3, 5, 7, 11, 13, 17, 19) * scale
    close(a * a.inverse(), ONE, abs_tol=1e-12)


def test_small_nonzero_value_is_not_silently_zero():
    assert Ultra(1e-14).is_invertible
    close(Ultra(1e-14).inverse(), Ultra(1e14))
    assert Ultra(1e-310) / Ultra(1e-310) == ONE


def test_safe_channel_reconstruction():
    assert Ultra.from_channels((1e308, 0), (1e308, 0)) == Ultra(1e308)
    tiny = math.ulp(0.0)
    assert Ultra.from_channels((tiny, 0), (tiny, 0)) == Ultra(tiny)


@pytest.mark.parametrize("generator", ["i", "j", "eps"])
@given(a=numbers, b=numbers)
@settings(max_examples=40, derandomize=True)
def test_conjugations_are_automorphisms(a, b, generator):
    assert a.conjugate(generator).conjugate(generator) == a
    assert (a * b).conjugate(generator) == a.conjugate(generator) * b.conjugate(generator)


def test_regular_determinant():
    assert Ultra(2).determinant() == 2**8
    assert (ONE + J).determinant() == 0
    assert (ONE + 4 * EPS).determinant() == 1


DIRECT = [
    "exp",
    "log",
    "sqrt",
    "sin",
    "cos",
    "tan",
    "sinh",
    "cosh",
    "tanh",
    "asin",
    "acos",
    "atan",
    "asinh",
    "acosh",
    "atanh",
]


@pytest.mark.parametrize("name", DIRECT)
@pytest.mark.parametrize("z", [0.3 + 0.2j, -2 + 0.4j, 2 - 0.7j, -0.5 - 0.2j])
def test_restriction_to_complex_numbers_matches_cmath(name, z):
    close(getattr(Ultra.coerce(z), name)(), getattr(cmath, name)(z))


@pytest.mark.parametrize("name", DIRECT)
def test_dual_tangent_against_independent_finite_difference(name):
    z, direction, step = 0.4 + 0.3j, 0.2 - 0.15j, 1e-5
    a = Ultra.from_channels((z, direction), (z.conjugate(), -direction))
    f = getattr(cmath, name)
    actual = getattr(a, name)().channels()
    for (value, derivative), (body, tangent) in zip(actual, a.channels(), strict=True):
        expected = (f(body + step * tangent) - f(body - step * tangent)) / (2 * step)
        assert abs(value - f(body)) < 1e-12
        assert abs(derivative - expected) < 1e-8


def test_exact_dual_calculus():
    close((2 + 3 * EPS).exp(), math.exp(2) * (ONE + 3 * EPS))
    close((2 + 3 * EPS).log(), math.log(2) + 1.5 * EPS)
    assert (4 + 8 * EPS).sqrt() == 2 + 2 * EPS
    assert (EPS).sin() == EPS


@pytest.mark.parametrize(
    "a",
    [
        Ultra(7, 5, 3, 2),
        Ultra(2, 1, 1, 1),
        Ultra(0.1, 0, 0.1, 0, 0.1, 0, 0.1),
        Ultra(2, 3, 5, 7, 11, 13, 17, 19),
        ONE + 2 * J,
        -ONE,
    ],
)
def test_log_exp_round_trip_and_square_roots(a):
    close(a.log().exp(), a)
    close(a.sqrt() ** 2, a)
    close(a**0.5, a.sqrt())


def test_log_branch_lattice():
    principal = Ultra(2, 0.3, 0.4, 0.1).log()
    other = Ultra(2, 0.3, 0.4, 0.1).log(branches=(1, 0))
    close(other - principal, math.pi * I * (ONE + J))
    close(other.exp(), principal.exp())
    close(Ultra(8).log(2), Ultra(3))
    with pytest.raises(NonInvertibleError):
        Ultra(8).log(1)


def test_branch_points_and_zero():
    assert ZERO.sqrt() == ZERO
    close(ONE.asin(), math.pi / 2)
    assert (-ONE).sqrt() == I
    assert Ultra(-1, 0, -0.0).sqrt() == I  # canonical zero convention
    for operation in (EPS.sqrt, ZERO.log, (ONE + EPS).asin, (I + EPS).asinh):
        with pytest.raises(DomainError):
            operation()


@pytest.mark.parametrize(
    "forward,inverse",
    [
        ("sin", "asin"),
        ("cos", "acos"),
        ("tan", "atan"),
        ("sinh", "asinh"),
        ("cosh", "acosh"),
        ("tanh", "atanh"),
        ("sec", "asec"),
        ("csc", "acsc"),
        ("cot", "acot"),
        ("sech", "asech"),
        ("csch", "acsch"),
        ("coth", "acoth"),
    ],
)
def test_inverse_functions_in_valid_direction(forward, inverse):
    a = Ultra(0.7, 0.1, 0.2, 0.03, 0.2, 0.1, 0.05, 0.02)
    close(getattr(getattr(a, inverse)(), forward)(), a)


def test_trigonometric_identity_with_all_components():
    a = Ultra(0.7, 0.1, 0.2, 0.03, 0.2, 0.1, 0.05, 0.02)
    close(a.sin() ** 2 + a.cos() ** 2, ONE)
    close(a.cosh() ** 2 - a.sinh() ** 2, ONE)
    close((math.pi * I).exp(), -ONE)
    close(J.exp(), math.cosh(1) + math.sinh(1) * J)
    assert EPS.exp() == ONE + EPS
