"""Independent oracles for the application demos and their inverse problems."""

import math

import pytest

pytest.importorskip("matplotlib")
import numpy as np  # noqa: E402

from examples.applications import (  # noqa: E402
    LENGTHS,
    arm_path,
    arm_position_jacobian,
    arm_reference,
    fit_separation,
    interference_intensity,
    interference_observations,
    interference_reference,
    wave_reference,
    wave_state,
)
from ultracomplexmath import EPS, I, J  # noqa: E402


@pytest.mark.parametrize("unit,index,signature", [(I, 2, -1), (J, 1, 1), (EPS, 4, 0)])
def test_cosine_slice_has_claimed_geometry(unit, index, signature):
    for y in [-math.pi, -0.7, 0, 1.3, math.pi]:
        value = (math.pi / 4 + y * unit).cos()
        a, b = value.real, value.coefficients[index]
        if signature:
            assert a * a + signature * b * b == pytest.approx(0.5, abs=1e-12)
        else:
            assert a == pytest.approx(1 / math.sqrt(2))


@pytest.mark.parametrize("x,t,c", [(-1.2, 2.1, 0.8), (0.1, 3.0, 1.0), (2.7, 4.8, 1.1)])
def test_wave_channels_and_speed_derivatives(x, t, c):
    actual, expected = wave_state(x, t, c).channels(), wave_reference(x, t, c)
    for pair, reference in zip(actual, expected, strict=True):
        assert pair == pytest.approx(reference, abs=1e-12)


def test_wave_field_satisfies_wave_equation_numerically():
    x, t, c, h = 0.4, 2.35, 1.17, 0.0001
    u = wave_state(x, t, c).real
    tt = (wave_state(x, t + h, c).real - 2 * u + wave_state(x, t - h, c).real) / h**2
    xx = (wave_state(x + h, t, c).real - 2 * u + wave_state(x - h, t, c).real) / h**2
    assert tt == pytest.approx(c * c * xx, rel=2e-6, abs=2e-5)


@pytest.mark.parametrize("theta", [[0.2, 0.7], [-0.4, 1.2], [1.4, 0.01]])
def test_robot_jacobian_against_analytic_kinematics(theta):
    actual, expected = arm_position_jacobian(theta), arm_reference(theta)
    for value, reference in zip(actual, expected, strict=True):
        np.testing.assert_allclose(value, reference, atol=1e-12)
    assert np.linalg.det(actual[1]) == pytest.approx(LENGTHS[0] * LENGTHS[1] * math.sin(theta[1]))


def test_straight_robot_has_rank_one_jacobian():
    _, jacobian = arm_position_jacobian([0.7, 0])
    assert np.linalg.matrix_rank(jacobian, tol=1e-12) == 1


def test_robot_tracks_entire_closed_curve():
    targets, angles, errors, _ = arm_path(81)
    assert max(errors) < 1e-10
    for target, theta in zip(targets, angles, strict=True):
        independent_position, _ = arm_reference(theta)
        np.testing.assert_allclose(independent_position, target, atol=1e-10)
    np.testing.assert_allclose(targets[0], targets[-1], atol=1e-12)


@pytest.mark.parametrize("x,z,d", [(1.3, 8, 2.4), (-0.7, 1.2, 1.8), (0, 3.4, 2.6), (5, 9, 1.9)])
def test_interference_and_gradient_against_scalar_propagators(x, z, d):
    assert interference_intensity(x, z, d) == pytest.approx(
        interference_reference(x, z, d), abs=1e-11
    )


def test_inverse_fit_recovers_clean_independent_data():
    xs = np.linspace(-6, 6, 41)
    observed = np.array([interference_reference(x, 8, 2.4)[0] for x in xs])
    fitted, history = fit_separation(xs, observed, 8)
    assert fitted == pytest.approx(2.4, abs=1e-9)
    assert np.all(np.diff(history[:, 1]) <= 0)


def test_inverse_fit_recovers_separation_with_noise():
    xs, observed, truth, distance = interference_observations()
    fitted, history = fit_separation(xs, observed, distance)
    assert abs(fitted - truth) < 0.005
    assert history[-1, 1] < history[0, 1] / 100
    assert np.all(np.diff(history[:, 1]) <= 0)
