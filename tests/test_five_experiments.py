"""Independent coefficient, field, incidence, Mueller and signal checks."""

import cmath
import math
from fractions import Fraction as F
from itertools import product
from pathlib import Path

import pytest

from examples.comb_filter import comb_response, group_delays
from examples.five_experiments import phase_circle, render
from ultracomplexmath import (
    CIRCULAR,
    HYPERBOLIC,
    PARABOLIC,
    QEPS,
    QI,
    QJ,
    QONE,
    QZERO,
    DomainError,
    ExactComplex,
    ExactMatrix,
    ExactPolynomial,
    ExactStokes,
    ExactUltra,
    ModeOperator,
    PolynomialCauchyField,
    ProjectivePoint,
    SegreQuadricPoint,
    Ultra,
)

PLUS, MINUS = (QONE + QJ) / 2, (QONE - QJ) / 2


@pytest.mark.parametrize(
    "x",
    [
        QONE,
        QI,
        QJ + QI / 7 + QEPS,
        ExactUltra(*range(1, 9)),
        ExactUltra(10**100, i=F(-2, 7), eps_ij=5),
    ],
)
def test_rational_unit_squares(x):
    f = (x * x).square_roots()
    expected = {x, -x, QJ * x, -QJ * x}
    assert f.count == 4 and set(f.representatives()) == expected
    assert f.at() == (x * x).sqrt()
    assert {f.at(i, j) for i, j in product(range(2), repeat=2)} == expected


@pytest.mark.parametrize(
    "v", [2 * QONE, QI, QEPS, QEPS * PLUS, 2 * MINUS, QI * PLUS + QEPS * MINUS]
)
def test_no_rational_roots(v):
    f = v.square_roots()
    assert f.count == 0 and list(f.representatives()) == []
    with pytest.raises(DomainError):
        f.at()


def test_free_sheets_and_validation():
    z, w = ExactComplex(1, -3), ExactComplex(F(-2, 7), 1)
    f = PLUS.square_roots()
    assert f.sheet_counts == (2, 1) and f.count == math.inf
    assert list(f.representatives()) == [PLUS, -PLUS]
    for i in (0, 1):
        root = f.at(i, minus_tangent=z)
        assert root * root == PLUS and root.channels()[1][1] == z
    both = QZERO.square_roots().at(plus_tangent=z, minus_tangent=w)
    assert both * both == QZERO and both.channels() == ((ExactComplex(), z), (ExactComplex(), w))
    with pytest.raises(ValueError):
        f.at(plus_tangent=z)
    with pytest.raises(ValueError):
        f.at(minus=1)
    with pytest.raises(ValueError):
        f.at(True)
    with pytest.raises(TypeError):
        f.at(minus_tangent=1j)


@pytest.mark.parametrize("plane", [CIRCULAR, HYPERBOLIC, PARABOLIC])
def test_polynomial_cauchy_against_independent_taylor_solution(plane):
    # Given data: arbitrary rational quartic and cubic. U_yy=s*U_xx fixes all coefficients.
    f, g = ExactPolynomial([7, F(-2, 3), 0, 1, 4]), ExactPolynomial([2, 3, -4, F(5, 2)])
    field = PolynomialCauchyField(plane, f, g)
    s = plane.square
    for x, y in product((F(-4, 3), F(0), F(2, 7)), (F(-3, 5), F(0), F(4, 3))):
        expect = sum(
            s**k * y ** (2 * k) * f.derivative(2 * k)(x).real / math.factorial(2 * k)
            for k in range(3)
        )
        expect += sum(
            s**k * y ** (2 * k + 1) * g.derivative(2 * k)(x).real / math.factorial(2 * k + 1)
            for k in range(2)
        )
        assert field(x, y) == expect
        assert field(x, 0) == f(x).real
    zero = ExactPolynomial([])
    assert PolynomialCauchyField(plane, zero, zero)(-2, 3) == 0
    with pytest.raises(ValueError):
        PolynomialCauchyField(plane, zero, ExactPolynomial([QJ]))
    with pytest.raises(TypeError):
        field(0.25, 1)


@pytest.mark.parametrize("left,right", tuple(product(range(2), repeat=2)))
def test_all_segre_pivots_with_tangents_at_infinity(left, right):
    a = [QEPS * (1 + QI), QEPS * (3 - QI)]
    b = [QEPS * (2 + QI), QEPS * (5 - QI)]
    a[left] += 1 + QI
    b[right] += 2 - QI
    x, y = [a[k] * PLUS + b[k] * MINUS for k in range(2)]
    p = ProjectivePoint(x, y)
    q = SegreQuadricPoint.from_projective(p)
    h = (q.su, q.sv, q.tu, q.tv)
    assert h == tuple(s * t for s, t in product(a, b))
    body, vel = [n.primal for n in h], [n.tangent for n in h]
    assert body[0] * body[3] == body[1] * body[2]
    assert body[0] * vel[3] + vel[0] * body[3] == body[1] * vel[2] + vel[1] * body[2]
    assert q.to_projective().equivalent(p)
    scale = (2 - QI + QEPS) * PLUS + (3 + QEPS * QI) * MINUS
    scaled_p = ProjectivePoint(x * scale, y * scale)
    assert SegreQuadricPoint.from_projective(scaled_p).to_projective().equivalent(p)
    scaled_q = SegreQuadricPoint(*(n * (QI + QEPS) for n in h))
    assert scaled_q.to_projective().equivalent(p)


def test_segre_requires_both_orders_and_central_coordinates():
    for bad in [(QONE, QZERO, QZERO, QEPS), (QONE, QZERO, QZERO, QONE), (QEPS, QZERO, QZERO, QEPS)]:
        with pytest.raises(ValueError):
            SegreQuadricPoint(*bad)
    with pytest.raises(TypeError):
        SegreQuadricPoint(QJ, QZERO, QZERO, QZERO)
    with pytest.raises(TypeError):
        SegreQuadricPoint.from_projective(ProjectivePoint(Ultra(1), Ultra(0)))


def test_stokes_mixing_retarder_diattenuator_and_singular_analyzer():
    u, v = 1 + QI, 2 * QONE - QI
    state = u * PLUS + v * MINUS
    pure = ExactStokes.from_jones(state)
    assert pure == ExactStokes(7, -3, 2, 6) and pure.interval == QZERO
    assert ExactStokes.from_jones((QI + QEPS) * state) == pure
    mixed = ExactStokes(9, -3, 2, 6)
    assert ExactStokes.from_coherency(mixed.coherency()) == mixed
    phase = ModeOperator.from_matrix(QI * (1 + QI * QEPS), QZERO, QZERO, QONE)
    s = mixed.through(phase)
    assert s == ExactStokes(9, -3, -6 - 2 * QEPS, 2 - 6 * QEPS)
    assert s.interval == mixed.interval == 4 * mixed.coherency().determinant()
    shear = ModeOperator.from_matrix(QONE, QEPS + QONE / 3, QZERO, QONE)
    assert pure.through(shear) == ExactStokes.from_jones(shear(state))
    attenuate = ModeOperator.from_matrix(QONE / 2, QZERO, QZERO, QONE)
    assert mixed.through(attenuate).interval == mixed.interval / 4
    analyzer = ModeOperator.from_matrix(QONE, QZERO, QZERO, QZERO)
    assert mixed.through(analyzer) == ExactStokes(3, 3, 0, 0)
    assert ExactStokes(1, -1, 0, 0).through(analyzer) == ExactStokes(0, 0, 0, 0)


@pytest.mark.parametrize(
    "invalid",
    [
        (-1, 0, 0, 0),
        (1, 2, 0, 0),
        (QI, 0, 0, 0),
        (1, QJ, 0, 0),
        (1, 1 + QEPS, 0, 0),
        (QEPS, 0, 0, 0),
    ],
)
def test_stokes_physical_domain(invalid):
    with pytest.raises(ValueError):
        ExactStokes(*invalid)


def test_coherency_domain():
    with pytest.raises(ValueError):
        ExactStokes.from_coherency(ExactMatrix([[1, 1], [0, 1]]))
    with pytest.raises(ValueError):
        ExactStokes.from_coherency(ExactMatrix([[1 + QI, 0], [0, 1]]))
    with pytest.raises(ValueError):
        ExactStokes.from_coherency(ExactMatrix([[1]]))


def test_comb_filters_against_discrete_fourier_sum_and_analytic_delays():
    d = 48

    def impulse_dft(w, sign, g):
        return (1 + sign * float(g) * cmath.exp(-1j * d * w)) / (1 + float(g))

    for z, g in product(phase_circle(3), (F(0), F(1, 2), F(1))):
        response = comb_response(z, d, g)
        delays = group_delays(response)
        omega = -math.atan2(z.imag, z.real) / d
        for sign, (h, dh), delay in zip((1, -1), response.channels(), delays, strict=True):
            assert complex(h.real, h.imag) == pytest.approx(impulse_dft(omega, sign, g), abs=1e-14)
            step = 1e-7
            reference = (
                impulse_dft(omega + step, sign, g) - impulse_dft(omega - step, sign, g)
            ) / (2 * step)
            assert complex(dh.real, dh.imag) == pytest.approx(reference, abs=1e-8)
            denom = 1 + g**2 + 2 * sign * g * z.real
            assert delay == (d * (g**2 + sign * g * z.real) / denom if denom else None)
        if g == 1:
            assert sum(z.determinant for z, _ in response.channels()) == 1


def test_comb_null_and_arbitrarily_close_to_null():
    assert group_delays(comb_response(ExactComplex(-1), 48)) == (None, 24)
    assert group_delays(comb_response(ExactComplex(1), 48)) == (24, None)
    near = CIRCULAR.cayley(F(1, 10**75))
    assert group_delays(comb_response(ExactComplex(near.real, near.imag), 48)) == (24, 24)
    for p, d, g in [(ExactComplex(2), 48, 1), (ExactComplex(1), 0, 1), (ExactComplex(1), 48, 2)]:
        with pytest.raises(ValueError):
            comb_response(p, d, g)


def test_shipped_offline_gallery_is_reproducible(tmp_path):
    path = tmp_path / "lab.html"
    render(path)
    shipped = Path(__file__).resolve().parents[1] / "docs/gallery/five-experiments.html"
    assert shipped.read_text(encoding="utf-8") == path.read_text(encoding="utf-8")
