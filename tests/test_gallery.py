"""Independent mathematical checks for the public gallery demonstrations."""

import cmath
import math

import pytest

pytest.importorskip("matplotlib")

from examples.gallery import (  # noqa: E402
    COUPLING,
    OMEGA,
    ROOTS,
    angle_surface,
    cosine_grid,
    coupled_state,
    newton_point,
    verify_math,
)
from ultracomplexmath import EPS, ONE, Binary, Complex, Dual, Ultra  # noqa: E402


@pytest.mark.parametrize("kind", [Complex, Binary, Dual])
def test_gallery_cosine_against_closed_form(kind):
    coordinates, values = cosine_grid(kind, 7)
    for row, y in enumerate(coordinates):
        for col, x in enumerate(coordinates):
            if kind is Complex:
                expected = (math.cos(x) * math.cosh(y), -math.sin(x) * math.sinh(y))
            elif kind is Binary:
                expected = (math.cos(x) * math.cos(y), -math.sin(x) * math.sin(y))
            else:
                expected = (math.cos(x), -y * math.sin(x))
            assert values[row, col] == pytest.approx(expected, abs=1e-12)


@pytest.mark.parametrize("kind,signature", [(Binary, 1), (Dual, 0), (Complex, -1)])
def test_angle_gallery_implicit_surfaces(kind, signature):
    for row in angle_surface(kind, [-2.2, 0.4, 2.7], [-1.3, 0.1, 1.4]):
        for x, y, z in row:
            assert x * x + y * y + signature * z * z == pytest.approx(1)


@pytest.mark.parametrize("t,coupling", [(0, 0.5), (1.7, 0.12), (8.25, COUPLING), (18, 0.9)])
def test_coupled_modes_and_parameter_derivatives(t, coupling):
    state = coupled_state(t, coupling)
    e = cmath.exp(1j * OMEGA * t)
    a = e * math.cos(coupling * t)
    b = 1j * e * math.sin(coupling * t)
    da = -t * e * math.sin(coupling * t)
    db = 1j * t * e * math.cos(coupling * t)
    assert state.coefficients == pytest.approx(
        (a.real, b.real, a.imag, b.imag, da.real, db.real, da.imag, db.imag), abs=1e-12
    )


def test_nine_roots_and_full_nilpotent_newton_convergence():
    for a in range(3):
        for b in range(3):
            root = Ultra.from_channels((ROOTS[a], 0), (ROOTS[b], 0))
            assert (root**3).isclose(ONE)
            seed = root + Ultra(real=0.03, i=-0.02) + EPS
            label, _, result = newton_point(seed)
            assert label == 3 * a + b
            assert result is not None and result.isclose(root, abs_tol=1e-8)
    assert newton_point(EPS)[0] == -1


def test_gallery_error_budget_and_second_order_remainder():
    report = verify_math()
    assert report["closed_form_max_error"] < 1e-11
    assert report["intensity_conservation_max_error"] < 1e-12
    assert 3.8 < report["linearization_error_ratio_when_delta_halves"] < 4.2
