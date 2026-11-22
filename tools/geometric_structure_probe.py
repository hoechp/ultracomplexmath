"""Reproduce bounded examples in the geometry-first research review.

Exact identities use rational coefficients. The unit polar experiment uses
moderate floating-point inputs only; it does not certify global conditioning.
These are research checks, not new public polar, optics or geometry APIs.
"""

import cmath
import hashlib
import json
import math
import random
from fractions import Fraction as F
from itertools import product
from pathlib import Path

from ultracomplexmath import (
    EPS,
    ONE,
    QEPS,
    QI,
    QJ,
    QONE,
    QZERO,
    ExactMatrix,
    ExactUltra,
    I,
    J,
    ModeOperator,
    ProjectivePoint,
    Ultra,
    __version__,
)


def polar_parts(value):
    plus = complex(value.real + value.j, value.i + value.ij)
    minus = complex(value.real - value.j, value.i - value.ij)
    lp, lm = math.log(abs(plus)), math.log(abs(minus))
    ap, am = cmath.phase(plus), cmath.phase(minus)
    return (
        math.exp((lp + lm) / 2),
        (lp - lm) / 2,
        (ap + am) / 2,
        (ap - am) / 2,
        value.tangent / value.primal,
    )


def polar_value(r, rho, theta, phi, tangent):
    # Independent elementary factors, without using Ultra.exp or Ultra.log.
    return (
        r
        * (math.cosh(rho) + J * math.sinh(rho))
        * (math.cos(theta) + I * math.sin(theta))
        * (math.cos(phi) + I * J * math.sin(phi))
        * (ONE + EPS * tangent)
    )


def unit_polar_form():
    rng = random.Random(20261003)
    values = [ONE, -ONE, I, -I, J, -J, I * J, -I * J]
    while len(values) < 72:
        value = Ultra(*(rng.uniform(-2, 2) for _ in range(8)))
        if all(abs(z) > 0.3 for z, _ in value.channels()):
            values.append(value)
    reconstruction_error = 0.0
    multiplication_error = 0.0
    for value in values:
        r, rho, theta, phi, tangent = polar_parts(value)
        rebuilt = polar_value(r, rho, theta, phi, tangent)
        reconstruction_error = max(reconstruction_error, max(map(abs, rebuilt - value)))
        assert rebuilt.isclose(value, rel_tol=2e-13, abs_tol=2e-13)
        logarithm = Ultra(math.log(r), rho, theta, phi).with_tangent(tangent)
        assert logarithm.exp().isclose(value, rel_tol=2e-13, abs_tol=2e-13)
        assert logarithm.isclose(value.log(), rel_tol=2e-13, abs_tol=2e-13)
        for m, n in product((-1, 0, 1), repeat=2):
            equivalent = polar_value(
                r, rho, theta + math.pi * (m + n), phi + math.pi * (m - n), tangent
            )
            assert equivalent.isclose(value, rel_tol=2e-13, abs_tol=2e-13)
    for left, right in zip(values, reversed(values), strict=True):
        r, rho, theta, phi, tangent = polar_parts(left)
        s, sigma, alpha, beta, variation = polar_parts(right)
        rebuilt = polar_value(r * s, rho + sigma, theta + alpha, phi + beta, tangent + variation)
        expected = left * right
        multiplication_error = max(multiplication_error, max(map(abs, rebuilt - expected)))
        assert rebuilt.isclose(expected, rel_tol=3e-13, abs_tol=3e-13)
    assert not (ONE + J).is_invertible and not EPS.is_invertible
    return {
        "unit_samples": len(values),
        "branch_lattice_shifts_per_sample": 9,
        "maximum_reconstruction_coefficient_error": reconstruction_error,
        "maximum_product_coefficient_error": multiplication_error,
        "domain": "Real coefficients, invertible bodies, moderate bounded inputs",
    }


def finite_dual_motion():
    velocity, position = F(2, 3), F(-3, 2)
    state = ExactUltra(velocity, eps=position)
    times = (F(-2), F(0), F(1, 3), F(5))
    for t in times:
        moved = (QONE + t * QEPS) * state
        assert moved == ExactUltra(velocity, eps=position + t * velocity)
        for s in times:
            assert (QONE + t * QEPS) * (QONE + s * QEPS) == QONE + (t + s) * QEPS
    # An operator nilpotent and a coefficient nilpotent can remain independent.
    nilpotent = ModeOperator.from_matrix(QZERO, QONE, QZERO, QZERO)
    assert nilpotent @ nilpotent == ModeOperator(QZERO, QZERO)
    assert nilpotent.scaled(QEPS) != ModeOperator(QZERO, QZERO)
    return {
        "finite_times": [str(t) for t in times],
        "exact_free_motion_and_time_composition": True,
        "independent_operator_and_coefficient_nilpotents": True,
    }


def quadratic_dynamics():
    identity = ExactMatrix([[1, 0], [0, 1]])
    zero = identity * 0
    counts = {"elliptic": 0, "hyperbolic": 0, "parabolic": 0, "scalar": 0}
    for a, b, c, d in product((-1, 0, 1), repeat=4):
        matrix = ExactMatrix([[a, b], [c, d]])
        half_trace = F(a + d, 2)
        delta = half_trace**2 - (a * d - b * c)
        reduced = matrix - identity * half_trace
        assert reduced @ reduced == identity * delta
        if reduced == zero:
            kind = "scalar"
        else:
            kind = "elliptic" if delta < 0 else "hyperbolic" if delta > 0 else "parabolic"
        counts[kind] += 1
    damping = []
    for gamma in (F(1, 2), F(1), F(2)):
        matrix = ExactMatrix([[0, 1], [-1, -2 * gamma]])
        reduced = matrix + identity * gamma
        assert reduced @ reduced == identity * (gamma**2 - 1)
        damping.append({"gamma": str(gamma), "omega_0": "1", "delta": str(gamma**2 - 1)})
    for kappa in (-1, 0, 1):
        generator = ExactMatrix([[0, 1], [kappa, 0]])
        metric = ExactMatrix([[-kappa, 0], [0, 1]])
        assert generator.transpose @ metric + metric @ generator == zero
    return {
        "matrices_exhaustively_checked": 81,
        "class_counts": counts,
        "damped_oscillators": damping,
    }


def optical_cells():
    identity = ModeOperator(QONE, QZERO)
    zero = ModeOperator(QZERO, QZERO)
    propagation = ModeOperator.from_matrix(QONE, QONE, QZERO, QONE)
    cases = []
    for focal_length in (F(1), F(1, 4), F(1, 5)):
        lens = ModeOperator.from_matrix(QONE, QZERO, -QONE / focal_length, QONE)
        assert (propagation - identity) ** 2 == zero
        assert (lens - identity) ** 2 == zero
        cell = propagation @ lens
        assert cell != lens @ propagation
        trace = 2 - 1 / focal_length
        delta = trace**2 / 4 - 1
        assert cell.matrix() == (
            (QONE - QONE / focal_length, QONE),
            (-QONE / focal_length, QONE),
        )
        assert cell.determinant() == QONE
        if delta == 0:
            nilpotent = cell + identity
            assert nilpotent != zero and nilpotent**2 == zero
            direct = identity
            for n in range(1, 13):
                direct = direct @ cell
                predicted = (identity - nilpotent.scaled(n * QONE)).scaled((-1) ** n * QONE)
                assert direct == predicted
        cases.append(
            {
                "length": "1",
                "focal_length": str(focal_length),
                "trace": str(trace),
                "delta": str(delta),
            }
        )
    return {"cells": cases, "critical_cell_powers_checked": 12, "order_of_elements_matters": True}


def adjoint(matrix):
    return ExactMatrix([[v.conjugate("i") for v in row] for row in matrix.transpose.rows])


def stokes(matrix):
    (a, b), (c, d) = matrix.rows
    assert a == a.conjugate("i") and d == d.conjugate("i") and c == b.conjugate("i")
    return a + d, a - d, b + c, (b - c) / QI


def minkowski(vector):
    s0, s1, s2, s3 = vector
    return s0**2 - s1**2 - s2**2 - s3**2


def polarization():
    phase = ExactUltra(F(3, 5), i=F(4, 5))
    phase_shift = ExactMatrix([[phase, 0], [0, phase.conjugate("i")]])
    squeeze = ExactMatrix([[2, 0], [0, F(1, 2)]])
    shear = ExactMatrix([[1, F(2, 3)], [0, 1]])
    u, v = QONE + QI, 2 * QONE - QI
    plus, minus = (QONE + QJ) / 2, (QONE - QJ) / 2
    state = u * plus + v * minus
    diagonal_actions = (
        (phase_shift, F(3, 5) * QONE + F(4, 5) * QI * QJ),
        (squeeze, F(5, 4) * QONE + F(3, 4) * QJ),
    )
    for matrix, scalar in diagonal_actions:
        out_u, out_v = matrix.apply((u, v))
        assert scalar * state == out_u * plus + out_v * minus
    for matrix in (phase_shift, squeeze, shear):
        (a, b), (c, d) = matrix.rows
        operator = ModeOperator.from_matrix(a, b, c, d)
        out_u, out_v = matrix.apply((u, v))
        assert operator(state) == out_u * plus + out_v * minus
    pure = ExactMatrix(
        [[u * u.conjugate("i"), u * v.conjugate("i")], [v * u.conjugate("i"), v * v.conjugate("i")]]
    )
    mixed = pure + ExactMatrix([[1, 0], [0, 1]])
    assert minkowski(stokes(pure)) == QZERO
    assert minkowski(stokes(mixed)).real > 0
    for coherency, transform in product((pure, mixed), (phase_shift, squeeze, shear)):
        assert transform.determinant() == QONE
        transformed = transform @ coherency @ adjoint(transform)
        before, after = stokes(coherency), stokes(transformed)
        assert minkowski(before) == 4 * coherency.determinant()
        assert minkowski(after) == minkowski(before)
        s0, s1, s2, s3 = before
        if transform == squeeze:
            # cosh(2 log 2)=17/8, sinh(2 log 2)=15/8.
            assert after == (F(17, 8) * s0 + F(15, 8) * s1, F(15, 8) * s0 + F(17, 8) * s1, s2, s3)
        elif transform == phase_shift:
            # Cross term gains phase**2=(-7+24i)/25.
            assert after == (
                s0,
                s1,
                F(-7, 25) * s2 - F(24, 25) * s3,
                F(24, 25) * s2 + F(-7, 25) * s3,
            )
    return {
        "exact_Jones_transformations": 3,
        "coherency_states": ["pure", "partially_polarized"],
        "CS_scalar_phase_and_boost_match_Jones_action": True,
        "mode_operator_matches_all_three_Jones_actions": True,
        "determinant_and_Stokes_Lorentz_invariants": True,
    }


def projective_quadric():
    z, w = QONE + 2 * QI, 3 * QONE - QI
    reciprocal = (z + QEPS * w).inverse()
    assert reciprocal == z.inverse() - QEPS * w / z**2
    plus, minus = (QONE + QJ) / 2, (QONE - QJ) / 2
    # Include finite, infinite and mixed charts; s,t and u,v are CD pairs.
    pairs = ((z + QEPS * w, QONE), (QONE + QEPS * w, QZERO), (QEPS * w, QONE))
    cases = 0
    chart_pairs = set()
    for (s, t), (u, v) in product(pairs, repeat=2):
        point = ProjectivePoint(s * plus + u * minus, t * plus + v * minus)
        chart_pairs.add(point.charts)
        x = (s * u, s * v, t * u, t * v)
        assert x[0] * x[3] - x[1] * x[2] == QZERO
        a = tuple(value.primal for value in x)
        b = tuple(value.tangent for value in x)
        assert a[0] * a[3] - a[1] * a[2] == QZERO
        assert a[0] * b[3] + b[0] * a[3] - a[1] * b[2] - b[1] * a[2] == QZERO
        scale = (2 * QONE + QEPS) * plus + (QI - 3 * QEPS) * minus
        assert point.equivalent(ProjectivePoint(point.x * scale, point.y * scale))
        cases += 1
    assert chart_pairs == set(product(("x", "y"), repeat=2))
    return {
        "homogeneous_examples": cases,
        "chart_pairs": sorted(chart_pairs),
        "quadric_body_and_tangent_equations": True,
        "reciprocal_chart_tangent_law": True,
    }


def analytic_field_equations():
    # F(x+u*y)=(x+u*y)^3, u^2=s. Differentiate its two real polynomials.
    count = 0
    for square, x, y in product((-1, 0, 1), (F(-2), F(0), F(1, 3)), (F(-1), F(0), F(2, 3))):
        unit = {-1: QI, 0: QEPS, 1: QJ}[square]
        z = x * QONE + y * unit
        f, g = x**3 + 3 * square * x * y**2, 3 * x**2 * y + square * y**3
        assert z**3 == f * QONE + g * unit
        fx, fy = 3 * x**2 + 3 * square * y**2, 6 * square * x * y
        gx, gy = 6 * x * y, 3 * x**2 + 3 * square * y**2
        fxx, fyy, gxx, gyy = 6 * x, 6 * square * x, 6 * y, 6 * square * y
        assert fx * QONE + gx * unit == 3 * z**2
        assert fy * QONE + gy * unit == unit * (3 * z**2)
        assert fy == square * gx and gy == fx
        assert fyy == square * fxx and gyy == square * gxx
        count += 1
    return {
        "exact_cubic_samples": count,
        "squares": [-1, 0, 1],
        "dual_case_is_not_the_heat_equation": True,
    }


def main():
    root = Path(__file__).resolve().parents[1]
    sources = [
        root / "src/ultracomplexmath" / name
        for name in ("core.py", "exact.py", "exact_linalg.py", "transformations.py")
    ]
    sources.append(Path(__file__).resolve())
    print(
        json.dumps(
            {
                "package_version": __version__,
                "base_commit": "fee69d99a90198b0b02945f897f0d84b06dfb122",
                "source_sha256": {
                    str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest()
                    for path in sources
                },
                "unit_polar_form": unit_polar_form(),
                "finite_dual_motion": finite_dual_motion(),
                "quadratic_dynamics": quadratic_dynamics(),
                "optical_cells": optical_cells(),
                "polarization": polarization(),
                "projective_quadric": projective_quadric(),
                "analytic_field_equations": analytic_field_equations(),
                "scope": "Bounded examples complement the proofs; no production geometry/physics solver or global numerical guarantee",
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
