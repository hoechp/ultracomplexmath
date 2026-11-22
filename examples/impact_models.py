"""Small, auditable engineering models built from the shipped algebra APIs.

These are educational example models, not calibrated engineering solvers.
Units, domains and independent references are documented in docs/gallery/impact.md.
Only fitting/uncertainty analysis imports NumPy; the forward models need no extras.
"""

from __future__ import annotations

import cmath
import math
import random
from dataclasses import dataclass
from fractions import Fraction

from ultracomplexmath import (
    EPS,
    ONE,
    QEPS,
    QI,
    QJ,
    QONE,
    QZERO,
    ZERO,
    ExactMatrix,
    ExactUltra,
    I,
    J,
    Mobius,
    ModeOperator,
    ProjectivePoint,
    Ultra,
    solve,
)

PLUS, MINUS = (ONE + J) / 2, (ONE - J) / 2
QPLUS, QMINUS = (QONE + QJ) / 2, (QONE - QJ) / 2
# Illustrative nondispersive indices, not measured materials data.
LAYERS = ((1.22, 550 / (4 * 1.22)), (1.38, 550 / (4 * 1.38)))


def positive(**values):
    for name, value in values.items():
        if not math.isfinite(value) or value <= 0:
            raise ValueError(f"{name} must be finite and positive")


def optical_media(wavelength_nm, angle_deg, layers, substrate_index, scale):
    """Real propagating s/p admittances; air incidence, no absorption or TIR."""
    positive(wavelength_nm=wavelength_nm, substrate_index=substrate_index, scale=scale)
    if not math.isfinite(angle_deg) or not 0 <= angle_deg < 85:
        raise ValueError("angle_deg must be in [0, 85)")
    transverse = math.sin(math.radians(angle_deg))
    indices = [1.0] + [n for n, _ in layers] + [substrate_index]
    for n, d in layers:
        positive(index=n, thickness_nm=d)
    if any(n <= transverse for n in indices):
        raise ValueError("This example requires real propagating waves in every medium")
    cosines = [math.sqrt(1 - (transverse / n) ** 2) for n in indices]
    return indices, cosines


@dataclass(frozen=True)
class OpticalResponse:
    reflection: Ultra
    transmission: Ultra
    reflectance: Ultra
    transmittance: Ultra
    transfer: Mobius


def coating_response(wavelength_nm, angle_deg=0.0, scale=1.0, layers=LAYERS, substrate_index=1.52):
    """Both polarizations and d/dscale of the *first* layer's thickness.

    e^(+i omega t) convention; tangential E, H. Homogeneous coordinates are [H:E].
    The plus channel is s; the minus channel is p. Scale is dimensionless.
    """
    indices, cosines = optical_media(wavelength_nm, angle_deg, layers, substrate_index, scale)
    admittances = [n * c * PLUS + n / c * MINUS for n, c in zip(indices, cosines, strict=True)]
    total = Mobius(ONE, ZERO, ZERO, ONE)
    for k, (n, d) in enumerate(layers):
        thickness = d * (scale + EPS) if k == 0 else Ultra(d)
        delta = 2 * math.pi * n * cosines[k + 1] * thickness / wavelength_nm
        c, s, q = delta.cos(), delta.sin(), admittances[k + 1]
        total = total @ Mobius(c, I * q * s, I * s / q, c)
    point = total.apply_projective(ProjectivePoint(admittances[-1], ONE))
    denominator = admittances[0] * point.y + point.x
    r = (admittances[0] * point.y - point.x) / denominator
    t = 2 * admittances[0] / denominator
    return OpticalResponse(r, t, r.abs2(), admittances[-1] / admittances[0] * t.abs2(), total)


def coating_reference(wavelength_nm, angle_deg=0.0, scale=1.0, layers=LAYERS, substrate_index=1.52):
    """Independent ordinary-complex Fresnel reflection recursion, no matrices."""
    ns, cs = optical_media(wavelength_nm, angle_deg, layers, substrate_index, scale)
    result = []
    for polarization in ("s", "p"):
        qs = [n * c if polarization == "s" else n / c for n, c in zip(ns, cs, strict=True)]
        r = (qs[-2] - qs[-1]) / (qs[-2] + qs[-1])
        for k in reversed(range(len(layers))):
            n, d = layers[k]
            delta = 2 * math.pi * n * cs[k + 1] * d * (scale if k == 0 else 1) / wavelength_nm
            interface = (qs[k] - qs[k + 1]) / (qs[k] + qs[k + 1])
            propagation = cmath.exp(-2j * delta)
            r = (interface + r * propagation) / (1 + interface * r * propagation)
        result.append(r)
    return tuple(result)


@dataclass(frozen=True)
class Circuit:
    """Rs + (Cf || (Rp + (Rct || Cdl))); ohms and farads."""

    rs: float = 20.0
    rp: float = 2400.0
    rct: float = 9000.0
    cf: float = 8e-9
    cdl: float = 4e-6

    def __post_init__(self):
        positive(rs=self.rs, rp=self.rp, rct=self.rct, cf=self.cf, cdl=self.cdl)


DEFAULT_CIRCUIT = Circuit()
INITIAL_CIRCUIT = Circuit(rp=1200, rct=5000)


def circuit_system(omega, rs, rp, rct, cf, cdl, imaginary, zero, one):
    """Three-node Kirchhoff system; works with Ultra or ExactUltra scalars."""
    gs, gp, gct = one / rs, one / rp, one / rct
    matrix = (
        (gs, -gs, zero),
        (-gs, gs + gp + imaginary * omega * cf, -gp),
        (zero, -gp, gp + gct + imaginary * omega * cdl),
    )
    return matrix, (one, zero, zero)


def impedance(frequency_hz, circuit=DEFAULT_CIRCUIT):
    """Z, dZ/dlog(Rp), dZ/dlog(Rct) in one solve; both bodies coincide."""
    positive(frequency_hz=frequency_hz)
    matrix, rhs = circuit_system(
        2 * math.pi * frequency_hz,
        circuit.rs,
        circuit.rp * (ONE + EPS * PLUS),
        circuit.rct * (ONE + EPS * MINUS),
        circuit.cf,
        circuit.cdl,
        I,
        ZERO,
        ONE,
    )
    return solve(matrix, rhs)[0]


def impedance_reference(frequency_hz, circuit=DEFAULT_CIRCUIT):
    """Independent series/parallel reduction and its explicit derivatives."""
    positive(frequency_hz=frequency_hz)
    omega = 2 * math.pi * frequency_hz
    d = 1 + 1j * omega * circuit.rct * circuit.cdl
    branch = circuit.rp + circuit.rct / d
    y = 1j * omega * circuit.cf + 1 / branch
    z = circuit.rs + 1 / y
    return z, circuit.rp / (y * branch) ** 2, circuit.rct / (y * branch * d) ** 2


def synthetic_spectrum(frequencies, circuit=DEFAULT_CIRCUIT, seed=2317, relative_noise=0.006):
    """Independent Gaussian real/imag noise; sigma is known per component."""
    positive(relative_noise=relative_noise)
    rng = random.Random(seed)
    observations, sigmas = [], []
    for frequency in frequencies:
        z = impedance_reference(frequency, circuit)[0]
        sigma = relative_noise * abs(z)
        observations.append(z + complex(rng.gauss(0, sigma), rng.gauss(0, sigma)))
        sigmas.append(sigma)
    return tuple(observations), tuple(sigmas)


def impedance_design(frequencies, circuit, sigmas):
    """Whitened real/imag Jacobian for the two log resistances."""
    import numpy as np

    if len(frequencies) != len(sigmas) or len(frequencies) < 2:
        raise ValueError("At least two frequencies and matching sigmas are required")
    values, jacobian = [], []
    for frequency, sigma in zip(frequencies, sigmas, strict=True):
        positive(sigma=sigma)
        (z, u), (_, v) = impedance(frequency, circuit).channels()
        values.append(z)
        jacobian.extend(((u.real / sigma, v.real / sigma), (u.imag / sigma, v.imag / sigma)))
    return np.array(values), np.array(jacobian)


def information(frequencies, circuit, sigmas):
    """Local, known-noise log-parameter covariance from the whitened Jacobian.

    A finite number does not establish global identifiability or model validity.
    No pseudoinverse silently substitutes for a rank-deficient information matrix.
    """
    import numpy as np

    _, jacobian = impedance_design(frequencies, circuit, sigmas)
    _, s, vh = np.linalg.svd(jacobian, full_matrices=False)
    if s[-1] <= s[0] * max(jacobian.shape) * np.finfo(float).eps:
        raise ValueError("Frequency selection does not identify both parameters locally")
    covariance = (vh.T / s**2) @ vh
    return {
        "condition": float(s[0] / s[-1]),
        "log_sigma": np.sqrt(np.diag(covariance)).tolist(),
        "covariance": covariance.tolist(),
    }


def fit_impedance(frequencies, observations, sigmas, initial=INITIAL_CIRCUIT, max_iter=25):
    """Damped Gauss–Newton using the Ultra tangent Jacobian and an SVD solve."""
    import numpy as np

    if len(observations) != len(frequencies) or len(frequencies) != len(sigmas):
        raise ValueError("Frequencies, observations and sigmas must have matching lengths")
    if len(frequencies) < 2 or max_iter < 1:
        raise ValueError("At least two frequencies and one iteration are required")
    if not np.isfinite(np.asarray(observations)).all():
        raise ValueError("Observations must be finite")
    theta = np.log([initial.rp, initial.rct])

    def evaluate(parameters):
        model = Circuit(initial.rs, *np.exp(parameters), initial.cf, initial.cdl)
        predicted, jacobian = impedance_design(frequencies, model, sigmas)
        delta = (np.asarray(observations) - predicted) / np.asarray(sigmas)
        residual = np.column_stack((delta.real, delta.imag)).ravel()
        return model, jacobian, residual, float(residual @ residual)

    costs, converged = [], False
    model, jacobian, residual, cost = evaluate(theta)
    for _ in range(max_iter):
        costs.append(cost)
        step, _, rank, _ = np.linalg.lstsq(jacobian, residual, rcond=None)
        if rank != 2:
            raise ValueError("Fit Jacobian does not identify both parameters")
        if np.linalg.norm(step, ord=np.inf) < 1e-9:
            converged = True
            break
        step /= max(1, np.linalg.norm(step, ord=np.inf))
        accepted = False
        for power in range(16):
            candidate = theta + step * 0.5**power
            new_model, new_j, new_r, new_cost = evaluate(candidate)
            if new_cost < cost:
                improvement = cost - new_cost
                theta, model, jacobian, residual, cost = (
                    candidate,
                    new_model,
                    new_j,
                    new_r,
                    new_cost,
                )
                accepted = True
                if improvement < 1e-11 * max(1, cost):
                    converged = True
                break
        if converged or not accepted:
            break
    if costs[-1] != cost:
        costs.append(cost)
    return {
        "circuit": model,
        "costs": costs,
        "converged": converged,
        "reduced_chi_squared": cost / (2 * len(frequencies) - 2),
        "information": information(frequencies, model, sigmas),
    }


def exact_circuit_audit():
    """A separate rational fixture at omega=20 rad/s, not the noisy fit data."""
    matrix, rhs = circuit_system(
        20,
        1,
        4 * (QONE + QEPS * QPLUS),
        9 * (QONE + QEPS * QMINUS),
        Fraction(1, 50),
        Fraction(1, 20),
        QI,
        QZERO,
        QONE,
    )
    a = ExactMatrix(matrix)
    solution = a.solve(rhs)
    residual = tuple(x - y for x, y in zip(a.apply(solution), rhs, strict=True))
    # Direct rational series/parallel circuit, independent of Gaussian elimination.
    rp, rct = 4 * (QONE + QEPS * QPLUS), 9 * (QONE + QEPS * QMINUS)
    reference = 1 + 1 / (QI * Fraction(2, 5) + 1 / (rp + 1 / (1 / rct + QI)))
    if any(x != QZERO for x in residual) or solution[0] != reference:
        raise AssertionError("Exact circuit identity failed")
    return {"impedance": solution[0], "residual": residual}


def oscillator_reference(tau, damping):
    """Independent continuous solution for q(0)=1, v(0)=0, v=dq/dtau."""
    if not math.isfinite(damping) or damping < 0 or not math.isfinite(tau) or tau < 0:
        raise ValueError("tau and damping must be finite and nonnegative")
    delta = damping * damping - 1
    decay = math.exp(-damping * tau)
    if delta == 0:
        return decay * (1 + tau), -decay * tau
    if abs(delta) * tau * tau < 1e-6:
        # Entire C_delta/S_delta series removes cancellation close to criticality.
        x = delta * tau * tau
        c = 1 + x / 2 + x * x / 24 + x**3 / 720
        s = tau * (1 + x / 6 + x * x / 120 + x**3 / 5040)
        return decay * (c + damping * s), -decay * s
    if delta < 0:
        w = math.sqrt(-delta)
        c, s = math.cos(w * tau), math.sin(w * tau) / w
        return decay * (c + damping * s), -decay * s
    k = math.sqrt(delta)
    # Decaying eigenvalues avoid overflow in exp(-z*t)*cosh(k*t).
    slow, fast = -1 / (damping + k), -damping - k
    e1, e2 = math.exp(slow * tau), math.exp(fast * tau)
    return (-fast * e1 + slow * e2) / (2 * k), -(e1 - e2) / (2 * k)


def oscillator_path(damping=1.0, step=0.05, steps=240):
    """Implicit-midpoint trajectory and damping sensitivity, no eigenvalue branch.

    q and v are *explicitly chosen* state slots p+ and p-, not spatial axes.
    The tangent is the exact first derivative of the discrete update (up to roundoff).
    """
    positive(step=step)
    if not math.isfinite(damping) or damping < 0:
        raise ValueError("damping must be finite and nonnegative")
    if isinstance(steps, bool) or not isinstance(steps, int) or steps < 0:
        raise ValueError("steps must be a nonnegative integer")
    generator = ModeOperator.from_matrix(ZERO, ONE, -ONE, -2 * (damping + EPS))
    update = generator.cayley(Ultra(step / 2))
    state, rows = PLUS, []
    for _ in range(steps + 1):
        (q, dq), (v, dv) = state.channels()
        rows.append((q.real, v.real, dq.real, dv.real))
        state = update(state)
    return tuple(rows)


def exact_damping_audit():
    """Critical Jordan generator and coefficient epsilon are distinct nilpotents."""
    damping, h = QONE + QEPS, ExactUltra(Fraction(1, 10))
    generator = ModeOperator.from_matrix(QZERO, QONE, -QONE, -2 * damping)
    state = QPLUS
    next_state = generator.cayley(h / 2)(state)

    def coordinates(value):
        return (value + value.conjugate("j")) / 2 + QJ * (value - value.conjugate("j")) / 2, (
            value + value.conjugate("j")
        ) / 2 - QJ * (value - value.conjugate("j")) / 2

    q0, v0 = coordinates(state)
    q1, v1 = coordinates(next_state)
    energy_residual = (q1 * q1 + v1 * v1 - q0 * q0 - v0 * v0) / 2 + 2 * damping * h * (
        (v1 + v0) / 2
    ) ** 2
    critical = ModeOperator.from_matrix(QZERO, QONE, -QONE, -2 * QONE)
    identity = ModeOperator.from_matrix(QONE, QZERO, QZERO, QONE)
    nilpotent = critical + identity
    zero_op = ModeOperator.from_matrix(QZERO, QZERO, QZERO, QZERO)
    if (
        energy_residual != QZERO
        or nilpotent @ nilpotent != zero_op
        or nilpotent.scaled(QEPS) == zero_op
    ):
        raise AssertionError("Critical damping invariant failed")
    return {
        "energy_residual": energy_residual,
        "jordan_square_zero": True,
        "epsilon_times_jordan_nonzero": True,
    }
