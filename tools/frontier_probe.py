"""Bounded, reproducible experiments behind the renewed research agenda.

This is evidence for specific identities and numerical gaps, not a generic
higher-derivative, ODE, or finite-coefficient backend.
"""

import cmath
import hashlib
import json
import math
from fractions import Fraction as F
from pathlib import Path

from ultracomplexmath import (
    EPS,
    ONE,
    QEPS,
    QONE,
    QZERO,
    DomainError,
    ExactMatrix,
    ExactUltra,
    I,
    J,
    Mobius,
    ModeOperator,
    Ultra,
    __version__,
)


def mixed_derivatives():
    samples = []
    for h in (1e-3, 1e-5, 1e-8, 1e-10, 1e-100):
        x = ONE + I * h + I * J * h
        # Reproduce the earlier channel algorithm with the current primitives.
        channels = [(cmath.exp(z), 0j) for z, _ in x.channels()]
        old = Ultra.from_channels(*channels)
        value = (x + EPS).exp()
        expected = math.e * (math.sin(h) / h) ** 2
        second, third = -value.j / h**2, -value.eps_j / h**2
        assert math.isclose(second, expected, rel_tol=4e-15)
        assert math.isclose(third, expected, rel_tol=4e-15)
        samples.append(
            {
                "h": h,
                "previous_channel_exp_second": -old.j / h**2,
                "current_exp_second": second,
                "current_exp_third_via_epsilon": third,
                "finite_step_exp_reference": expected,
                "current_log_second": -x.log().j / h**2,
                "log_derivative_at_one": -1,
                "current_inverse_second": -x.inverse().j / h**2,
                "inverse_derivative_at_one": 2,
            }
        )
    return samples


def exact_motion():
    omega = ExactMatrix([[QZERO, QONE], [-QONE, QZERO]])
    cases = []
    for k in (-2, 0, 2):
        kappa = k * QONE + QEPS
        generator = ModeOperator.from_matrix(QZERO, QONE, kappa, QZERO)
        dt = ExactUltra(F(1, 5))
        forward, backward = generator.cayley(dt / 2), generator.cayley(-dt / 2)
        matrix = ExactMatrix(forward.matrix())
        assert matrix.transpose @ omega @ matrix == omega
        assert backward @ forward == ModeOperator(QONE, QZERO)
        form = ExactMatrix([[-kappa, QZERO], [QZERO, QONE]])
        assert matrix.transpose @ form @ matrix == form
        (a, b), (c, d) = forward.matrix()
        x, y = 2 * QONE, 3 * QONE
        ratio = Mobius(a, b, c, d)(x / y)
        assert ratio == (a * x + b * y) / (c * x + d * y)
        cases.append({"kappa_body": k, "kappa_tangent": 1, "time_step": "1/5"})
    return {"cases": cases, "symplectic_reversible_quadratic_and_projective_checks": True}


def f2_product(x, y, *, original_basis=False):
    """Bit vectors in either (1,s,r,rs,e,es,er,ers) or (1,j,i,ij,e,ej,ei,eij)."""
    result = 0
    for a in range(8):
        if not x & (1 << a):
            continue
        for b in range(8):
            if not y & (1 << b):
                continue
            common = a & b
            if common & (4 if original_basis else 7):
                continue
            result ^= 1 << (a ^ b)
    return result


def finite_coefficients():
    # r=i+1, s=j+1. Check the change of basis against the original relations.
    r, s, eps = 1 ^ (1 << 2), 1 ^ (1 << 1), 1 << 4
    images = []
    for index in range(8):
        value = 1
        for flag, generator in ((1, s), (2, r), (4, eps)):
            if index & flag:
                value = f2_product(value, generator, original_basis=True)
        images.append(value)

    def change(x):
        result = 0
        for index, value in enumerate(images):
            if x & (1 << index):
                result ^= value
        return result

    assert len({change(x) for x in range(256)}) == 256
    for a in range(8):
        for b in range(8):
            assert change(f2_product(1 << a, 1 << b)) == f2_product(
                images[a], images[b], original_basis=True
            )
    units = [x for x in range(256) if any(f2_product(x, y) == 1 for y in range(256))]
    assert units == list(range(1, 256, 2))
    assert all(f2_product(x, x) == 1 for x in units)
    radical = range(0, 256, 2)
    assert all(f2_product(x, x) == 0 for x in radical)
    cube = f2_product(f2_product(1 << 1, 1 << 2), 1 << 4)
    assert cube == 1 << 7 and cube != 0
    assert all(f2_product(cube, x) == 0 for x in radical)
    return {
        "elements_exhaustively_checked": 256,
        "units_found_by_exhaustive_inverse_search": len(units),
        "all_units_square_to_one": True,
        "each_radical_element_squares_to_zero": True,
        "radical_cube_nonzero_radical_fourth_zero": True,
        "change_of_basis_bijective_and_preserves_all_basis_products": True,
        "implementation_status": "Probe only; no public modular Ultra backend",
    }


def main():
    root = Path(__file__).resolve().parents[1]
    names = ["core.py", "exact.py", "transformations.py", "plane_geometry.py"]
    sources = {
        name: hashlib.sha256((root / "src/ultracomplexmath" / name).read_bytes()).hexdigest()
        for name in names
    }
    try:
        result = ExactUltra(8) ** F(1, 3)
        cube_root = {"supported": True, "result": str(result)}
    except DomainError as error:
        cube_root = {"supported": False, "error": str(error)}
    print(
        json.dumps(
            {
                "package_version": __version__,
                "pre_review_commit": "fb4870cbf8a47a89b4ac10cf3ff34f37fe0cc541",
                "source_sha256": sources,
                "mixed_derivatives": mixed_derivatives(),
                "exact_motion": exact_motion(),
                "characteristic_two": finite_coefficients(),
                "rational_cube_root_of_eight": cube_root,
                "scope": "Selected bounded checks; not a global accuracy or performance guarantee",
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
