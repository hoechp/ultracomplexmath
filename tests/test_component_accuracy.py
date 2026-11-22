"""Check small coefficients independently of a norm dominated by the body."""

import cmath
import math

import pytest

from ultracomplexmath import EPS, ONE, I, J, Ultra


@pytest.mark.parametrize("h", [1e-3, 1e-8, 1e-10, 1e-100])
def test_bicomplex_exponential_second_and_third_derivative(h):
    # k=i*j is a second commuting square root of -1; i*k=-j.
    result = (ONE + I * h + I * J * h + EPS).exp()
    expected = -math.e * math.sin(h) ** 2
    assert result.j == pytest.approx(expected, rel=3e-15, abs=0)
    assert result.eps_j == pytest.approx(expected, rel=3e-15, abs=0)
    assert result.i == pytest.approx(math.e * math.sin(h) * math.cos(h), rel=3e-15)


@pytest.mark.parametrize("b", [-1000, -2, -0.5, -0.1, 0, 0.1, 0.5, 2, 1000])
def test_exponential_scaled_factors_against_complex_channel_oracle(b):
    a = -abs(b) if abs(b) > 500 else 0.3
    value = Ultra(a, b, 0.7, -0.2, 0.1, -0.3, 0.4, 0.2)
    actual = value.exp().channels()
    for (z, w), (body, tangent) in zip(value.channels(), actual, strict=True):
        expected = cmath.exp(z)
        assert body == pytest.approx(expected, abs=1e-14, rel=1e-14)
        assert tangent == pytest.approx(expected * w, abs=1e-14, rel=1e-14)


def test_exponential_preserves_tiny_split_and_tangent_coefficients():
    value = Ultra(1, j=1e-100, eps=1e-100, eps_j=1e-200).exp()
    assert value.j == pytest.approx(math.e * 1e-100, rel=3e-15, abs=0)
    assert value.eps == pytest.approx(math.e * 1e-100, rel=3e-15, abs=0)
    assert value.eps_j == pytest.approx(2 * math.e * 1e-200, rel=3e-15, abs=0)
