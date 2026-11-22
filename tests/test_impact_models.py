"""Independent physical identities and componentwise checks for the showcase."""

import math
from dataclasses import replace

import pytest

from examples.impact_models import (
    LAYERS,
    Circuit,
    coating_reference,
    coating_response,
    exact_circuit_audit,
    exact_damping_audit,
    fit_impedance,
    impedance,
    impedance_reference,
    information,
    oscillator_path,
    oscillator_reference,
    synthetic_spectrum,
)
from ultracomplexmath import ONE, QZERO


@pytest.mark.parametrize("angle", [0, 35, 70])
@pytest.mark.parametrize("wavelength", [400, 550, 1000])
def test_fresnel_recursion_energy_and_tangent(angle, wavelength):
    result = coating_response(wavelength, angle, 1.13)
    refs = coating_reference(wavelength, angle, 1.13)
    h = 1e-5
    high = coating_reference(wavelength, angle, 1.13 + h)
    low = coating_reference(wavelength, angle, 1.13 - h)
    for (body, tangent), ref, a, b in zip(
        result.reflection.channels(), refs, high, low, strict=True
    ):
        assert body == pytest.approx(ref, rel=1e-12, abs=1e-14)
        assert tangent == pytest.approx((a - b) / (2 * h), rel=2e-8, abs=1e-10)
    assert (result.reflectance + result.transmittance).coefficients == pytest.approx(
        ONE.coefficients, abs=3e-14
    )
    assert result.transfer.determinant().coefficients == pytest.approx(ONE.coefficients, abs=3e-14)


def test_quarter_wave_zero_and_layer_order():
    index = math.sqrt(1.52)
    perfect = coating_response(550, layers=((index, 550 / (4 * index)),))
    assert max(abs(z) for z, _ in perfect.reflection.channels()) < 1e-15
    bare = coating_response(550, layers=())
    assert bare.reflectance.real == pytest.approx(((1 - 1.52) / (1 + 1.52)) ** 2)
    assert bare.reflectance.tangent == 0 * ONE
    forward = coating_response(550).reflectance.real
    reverse = coating_response(550, layers=tuple(reversed(LAYERS))).reflectance.real
    assert abs(forward - reverse) > 0.05


def test_optical_thickness_prediction_is_first_order():
    base = coating_response(740, 50, 1.1).reflectance
    errors = []
    for delta in (0.02, 0.01):
        changed = coating_response(740, 50, 1.1 + delta).reflectance.primal
        errors.append(abs(changed - base.primal - delta * base.tangent))
    assert errors[0] / errors[1] == pytest.approx(4, rel=0.04)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"wavelength_nm": 0},
        {"wavelength_nm": 550, "angle_deg": 90},
        {"wavelength_nm": 550, "scale": -1},
        {"wavelength_nm": 550, "layers": ((0.2, 50),), "angle_deg": 50},
    ],
)
def test_optics_explicit_domain(kwargs):
    with pytest.raises(ValueError):
        coating_response(**kwargs)


@pytest.mark.parametrize("frequency", [0.01, 0.3, 10, 3000, 1e6])
def test_kirchhoff_vs_series_parallel_and_two_analytic_derivatives(frequency):
    (z, u), (duplicate, v) = impedance(frequency).channels()
    ref, ref_u, ref_v = impedance_reference(frequency)
    assert z == pytest.approx(ref, rel=2e-11)
    assert duplicate == z
    # Tiny high-frequency derivatives get their own relative check.
    assert u == pytest.approx(ref_u, rel=2e-9, abs=1e-17)
    # At 1 MHz the second derivative is ~1e-11 beside a ~1e-1 first
    # derivative; recombining float basis coefficients loses relative digits.
    assert v == pytest.approx(ref_v, rel=3e-7, abs=1e-20)


def test_two_log_seeds_and_exact_residual():
    c, f, h = Circuit(), 8, 1e-5
    (_, u), (_, v) = impedance(f, c).channels()
    for field, derivative in (("rp", u), ("rct", v)):
        a = replace(c, **{field: getattr(c, field) * math.exp(h)})
        b = replace(c, **{field: getattr(c, field) * math.exp(-h)})
        fd = (impedance_reference(f, a)[0] - impedance_reference(f, b)[0]) / (2 * h)
        assert derivative == pytest.approx(fd, rel=1e-8)
    audit = exact_circuit_audit()
    assert audit["residual"] == (QZERO,) * 3
    # This fixture has genuinely different nonzero sensitivities.
    assert audit["impedance"].eps_j != 0
    assert audit["impedance"].eps_ij != 0


def test_inverse_fit_and_frequency_information():
    np = pytest.importorskip("numpy")
    fs = np.geomspace(0.01, 1e6, 65)
    observed, sigma = synthetic_spectrum(fs)
    result = fit_impedance(fs, observed, sigma)
    assert result["converged"]
    fitted = result["circuit"]
    assert fitted.rp == pytest.approx(Circuit().rp, rel=0.01)
    assert fitted.rct == pytest.approx(Circuit().rct, rel=0.01)
    assert all(a > b for a, b in zip(result["costs"], result["costs"][1:], strict=False))
    assert 0.6 < result["reduced_chi_squared"] < 1.4
    full = information(fs, fitted, sigma)
    restricted = information(fs[-17:], fitted, sigma[-17:])
    assert full["log_sigma"][1] < 0.01
    assert restricted["log_sigma"][1] > 100
    assert restricted["condition"] > 1e5 * full["condition"]


def test_noise_free_fit_and_fit_failures():
    pytest.importorskip("numpy")
    fs = (0.1, 1, 10, 100, 10000)
    truth = Circuit(rp=1700, rct=6000)
    observations = [impedance_reference(f, truth)[0] for f in fs]
    fit = fit_impedance(fs, observations, [10] * len(fs))
    assert fit["converged"]
    assert fit["circuit"].rp == pytest.approx(truth.rp, rel=1e-8)
    assert fit["circuit"].rct == pytest.approx(truth.rct, rel=1e-8)
    with pytest.raises(ValueError):
        fit_impedance(fs, observations[:-1], [1] * len(fs))
    with pytest.raises(ValueError):
        information(fs, truth, [0] * len(fs))
    with pytest.raises(ValueError):
        Circuit(cf=-1)
    with pytest.raises(ValueError):
        impedance(0)


@pytest.mark.parametrize("damping", [0, 0.4, 1 - 1e-9, 1, 1 + 1e-9, 2])
def test_midpoint_second_order_accuracy_and_dissipation(damping):
    reference = oscillator_reference(3, damping)
    errors = []
    for h in (0.05, 0.025):
        path = oscillator_path(damping, h, round(3 / h))
        errors.append(max(abs(a - b) for a, b in zip(path[-1][:2], reference, strict=True)))
        for (q0, v0, *_), (q1, v1, *_) in zip(path, path[1:], strict=False):
            change = (q1 * q1 + v1 * v1 - q0 * q0 - v0 * v0) / 2
            dissipation = -2 * damping * h * ((v1 + v0) / 2) ** 2
            assert change == pytest.approx(dissipation, abs=5e-16)
            assert change <= 5e-16
    assert errors[0] / errors[1] == pytest.approx(4, rel=0.015)


def test_critical_derivative_and_independent_nilpotents():
    tau = 2.0
    dq = math.exp(-tau) * tau**3 / 3
    dv = math.exp(-tau) * (tau**2 - tau**3 / 3)
    path = oscillator_path(1, 0.005, 400)
    assert path[-1][2] == pytest.approx(dq, rel=2e-6)
    assert path[-1][3] == pytest.approx(dv, rel=1e-5)
    audit = exact_damping_audit()
    assert audit["energy_residual"] == QZERO
    assert audit["jordan_square_zero"]
    assert audit["epsilon_times_jordan_nonzero"]


@pytest.mark.parametrize("damping", [0.4, 1, 1.8])
def test_discrete_damping_derivative(damping):
    delta = 1e-5
    a = oscillator_path(damping + delta, 0.05, 120)[-1]
    b = oscillator_path(damping - delta, 0.05, 120)[-1]
    result = oscillator_path(damping, 0.05, 120)[-1]
    for index in (0, 1):
        assert result[index + 2] == pytest.approx(
            (a[index] - b[index]) / (2 * delta), rel=1e-7, abs=1e-9
        )


@pytest.mark.parametrize("kwargs", [{"damping": -1}, {"step": 0}, {"steps": 1.5}, {"steps": True}])
def test_damping_explicit_domain(kwargs):
    with pytest.raises(ValueError):
        oscillator_path(**kwargs)
