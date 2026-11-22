"""Check selected research-agenda identities and report the installed API status.

Run after installing the package: python tools/research_probe.py
Only the standard library and ultracomplexmath are required. The local series
below are small-domain verification aids, not proposed production algorithms.
"""

import cmath
import json
import math
import random

from ultracomplexmath import EPS, ONE, ZERO, Binary, I, J, Ultra, __version__

BASELINE = "fb4870cbf8a47a89b4ac10cf3ff34f37fe0cc541"


def generalized_pair(kappa, t):
    """Fixed 40-term series, only for this probe's bounded input set."""
    c, s = ONE, Ultra(t)
    dc, ds = c, s
    for n in range(1, 40):
        dc = dc * kappa * t**2 / ((2 * n - 1) * 2 * n)
        ds = ds * kappa * t**2 / (2 * n * (2 * n + 1))
        c, s = c + dc, s + ds
    return c, s


def main():
    errors = {}

    def check(name, actual, expected, tolerance=1e-11):
        error = abs(actual - expected)
        errors[name] = max(errors.get(name, 0.0), error)
        if error > tolerance:
            raise AssertionError(f"{name}: error {error} > {tolerance}")

    # Direct real formulas, independent of the channel function implementation.
    a = math.pi / 4
    for b in (-2.0, -0.3, 0.0, 1.4):
        check(
            "complex_cosine",
            (a + I * b).cos(),
            math.cos(a) * math.cosh(b) - I * math.sin(a) * math.sinh(b),
        )
        check(
            "split_cosine",
            (a + J * b).cos(),
            math.cos(a) * math.cos(b) - J * math.sin(a) * math.sin(b),
        )
        check("dual_cosine", (a + EPS * b).cos(), math.cos(a) - EPS * b * math.sin(a))

    tangent_products = [Ultra.unit(i) * Ultra.unit(j) for i in range(4, 8) for j in range(4, 8)]
    if any(tangent_products):
        raise AssertionError("The tangent ideal must square to zero")

    r, theta, eta, chi = 0.2, 0.4, -0.3, 0.7
    deformation = Ultra(0.3, -0.1, 0.2, 0.05)
    factorized = (
        math.exp(r)
        * (math.cos(theta) + I * math.sin(theta))
        * (math.cosh(eta) + J * math.sinh(eta))
        * (math.cos(chi) + I * J * math.sin(chi))
        * (ONE + EPS * deformation)
    )
    check(
        "mixed_euler_factorization",
        (r + I * theta + J * eta + I * J * chi + EPS * deformation).exp(),
        factorized,
    )

    # A linear operator with complex-dual entries, checked against explicit
    # body/tangent matrix-vector multiplication and the product rule.
    rng = random.Random(20261003)

    def sample():
        return Ultra(*(rng.uniform(-1, 1) for _ in range(8)))

    def apply(alpha, beta, x):
        return alpha * x + beta * x.conjugate("j")

    for _ in range(24):
        alpha, beta, gamma, delta, x = (sample() for _ in range(5))
        ac, bc, xc = alpha.channels(), beta.channels(), x.channels()
        expected = []
        for n in range(2):
            a0, a1 = ac[n]
            b0, b1 = bc[n]
            z0, z1 = xc[n]
            w0, w1 = xc[1 - n]
            expected.append((a0 * z0 + b0 * w0, a0 * z1 + a1 * z0 + b0 * w1 + b1 * w0))
        check("operator_matrix_action", apply(alpha, beta, x), Ultra.from_channels(*expected))
        composed_alpha = alpha * gamma + beta * delta.conjugate("j")
        composed_beta = alpha * delta + beta * gamma.conjugate("j")
        check(
            "operator_composition",
            apply(alpha, beta, apply(gamma, delta, x)),
            apply(composed_alpha, composed_beta, x),
        )

        def circular(y):
            return J * y.conjugate("j")

        def parabolic(y):
            return J * y + circular(y)

        check("operator_circular_square", circular(circular(x)), -x)
        check("operator_parabolic_square", parabolic(parabolic(x)), ZERO)
        check("operator_swap_j_anticommutator", (J * x).conjugate("j") + J * x.conjugate("j"), ZERO)

        total = x + x.conjugate("j")
        intensity = total * total.conjugate("i")
        z = xc[0][0] + xc[1][0]
        dz = xc[0][1] + xc[1][1]
        expected_intensity = abs(z) ** 2 + EPS * (2 * (z.conjugate() * dz).real)
        check("coherent_intensity_and_tangent", intensity, expected_intensity)

    # An ideal balanced interferometer: H diag(exp(i*phi), 1) H.
    def beam_splitter(x):
        return (J * x + x.conjugate("j")) / math.sqrt(2)

    for phi in (0.0, 0.3, 1.2, math.pi):
        state = beam_splitter(Ultra.from_channels((1, 0), (0, 0)))
        phase = Ultra.from_channels((cmath.exp(1j * phi), 1j * cmath.exp(1j * phi)), (1, 0))
        state = beam_splitter(phase * state)
        powers = (state * state.conjugate("i")).channels()
        check("interferometer_plus_power", powers[0][0], math.cos(phi / 2) ** 2)
        check("interferometer_minus_power", powers[1][0], math.sin(phi / 2) ** 2)
        check("interferometer_plus_derivative", powers[0][1], -math.sin(phi) / 2)
        check("interferometer_minus_derivative", powers[1][1], math.sin(phi) / 2)

    for kappa in (-4.0, -0.1, 0.0, 0.2, 2.0):
        for t in (0.1, 0.7, 1.4):
            c, s = generalized_pair(Ultra(kappa), t)
            if kappa == 0:
                rc, rs = 1, t
            else:
                root = cmath.sqrt(kappa)
                rc, rs = cmath.cosh(root * t), cmath.sinh(root * t) / root
            check("generalized_cosine", c, Ultra.coerce(rc))
            check("generalized_sine", s, Ultra.coerce(rs))
            check("generalized_quadratic_identity", c * c - kappa * s * s, ONE)
    for t in (0.1, 0.7, 1.4):
        c, s = generalized_pair(EPS, t)
        check("critical_cosine_tangent", c, ONE + EPS * t**2 / 2)
        check("critical_sine_tangent", s, t + EPS * t**3 / 6)

    # Oscillator bodies compared with the two-exponential scalar solution;
    # critical gamma derivative compared with its explicit regular limit.
    omega, x0, v0 = 1.0, 1.0, -0.2
    for gamma in (0.2, 1.0, 2.0):
        for t in (0.1, 0.7, 1.4):
            g = gamma + EPS
            kappa = g * g - omega**2
            c, s = generalized_pair(kappa, t)
            position = (-g * t).exp() * (c * x0 + s * (g * x0 + v0))
            if gamma == omega:
                q = gamma * x0 + v0
                body = math.exp(-gamma * t) * (x0 + t * q)
                derivative = math.exp(-gamma * t) * (
                    -t * (x0 + t * q) + gamma * t**2 * x0 + t * x0 + gamma * t**3 * q / 3
                )
                check("critical_oscillator_derivative", position.eps, derivative)
            else:
                root = cmath.sqrt(gamma**2 - omega**2)
                r1, r2 = -gamma + root, -gamma - root
                c1 = (v0 - r2 * x0) / (r1 - r2)
                c2 = (r1 * x0 - v0) / (r1 - r2)
                body = c1 * cmath.exp(r1 * t) + c2 * cmath.exp(r2 * t)
            check("oscillator_body", position.real, body)

    # Nine distinct cube roots of a generic unit, with propagated tangents.
    value = Ultra(2, 0.3, 0.4, 0.1, 0.2, -0.1, 0.3, 0.05)
    roots = []
    channels = value.channels()
    for kp in range(3):
        for km in range(3):
            result = []
            for (z, w), k in zip(channels, (kp, km), strict=True):
                u = cmath.exp((cmath.log(z) + 2j * math.pi * k) / 3)
                result.append((u, w / (3 * u**2)))
            root = Ultra.from_channels(*result)
            roots.append(root)
            check("unit_cube_root_residual", root**3, value)
    separation = min(abs(a - b) for n, a in enumerate(roots) for b in roots[n + 1 :])
    if separation < 0.1:
        raise AssertionError("Expected nine distinct roots in this example")
    for a in (0.0, 0.3, -2.0):
        for b in (-1.0, 2.0):
            check("zero_root_family", (EPS * Ultra(a, b, 2 * a, -b)) ** 2, ZERO)

    # An exact integer calculation, with no conversion through Ultra/float.
    p, a = 7, 3
    correction = -((a * a - 2) // p) * pow(2 * a, -1, p) % p
    lifted = a + p * correction
    if (lifted * lifted - 2) % (p * p):
        raise AssertionError("Hensel lift failed")

    n = 2**53 + 1
    report = {
        "pre_review_commit": BASELINE,
        "evaluated_package_version": __version__,
        "purpose": "Selected identity checks, not a complete audit or production API implementation",
        "absolute_error_limit": 1e-11,
        "max_absolute_errors": errors,
        "tangent_ideal_zero_products": len(tangent_products),
        "operator_samples": 24,
        "unit_cube_roots": len(roots),
        "minimum_root_separation": separation,
        "hensel_example": {"prime": p, "initial_root": a, "lifted_root": lifted, "modulus": p * p},
        "current_observations": {
            "integer_exponent": n,
            "integer_power_actual": str(I**n),
            "integer_power_expected": str(I),
            "integer_power_correct": I**n == I,
            "large_integer_coefficients_collide": Ultra(n) == Ultra(n - 1),
            "abs_dual_returns": type(abs(3 + EPS)).__name__,
            "split_endpoint_square": str(Binary(0, 1) ** 2),
            "ultra_methods_present": {
                name: hasattr(Ultra, name)
                for name in ("roots", "atan2", "sinc", "log1p", "expm1", "primal", "tangent")
            },
        },
    }
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
