"""Componentwise, topological and independent matrix checks for the numerical APIs."""

import cmath
import math
from fractions import Fraction

import pytest

from ultracomplexmath import (
    EPS,
    ONE,
    ZERO,
    DomainError,
    ExactUltra,
    I,
    J,
    ModeOperator,
    PolarForm,
    Ultra,
)


@pytest.mark.parametrize("h", [1e-4, 1e-10, 1e-100, 1e-140])
def test_small_mixed_trig_and_reciprocal(h):
    x = Ultra(1, i=h, ij=h, eps=1)
    sh2 = math.sinh(h) ** 2
    for actual, expected in [
        (x.sin().j, math.sin(1) * sh2),
        (x.sin().eps_j, math.cos(1) * sh2),
        (x.cos().j, math.cos(1) * sh2),
        (x.cos().eps_j, -math.sin(1) * sh2),
    ]:
        assert actual == pytest.approx(expected, rel=3e-15, abs=0)
    # Independently, the + body channel is 1+2ih and the - channel is 1.
    # Subtract the rational expressions symbolically before evaluating them.
    h2 = Fraction(h) ** 2
    j = float(-2 * h2 / (1 + 4 * h2))
    eps_j = float((6 * h2 + 8 * h2 * h2) / (1 + 4 * h2) ** 2)
    for y in [x.inverse(), 1 / x, x**-1]:
        assert (y.j, y.eps_j) == pytest.approx((j, eps_j), rel=4e-15, abs=0)


def test_near_null_body_division_and_scaled_real_quotient():
    x = Ultra(1, j=math.nextafter(1.0, 0.0), eps=2e-12)
    assert x.inverse() == ExactUltra.from_approximate(x).inverse().approximate()
    assert Ultra(1e-310, ij=1e-310) / Ultra(1e-310) == ONE + I * J


@pytest.mark.parametrize("scale", [1e-240, 1.0, 1e240])
def test_full_polar_roundtrip_group_and_windings(scale):
    raw = Ultra(2, 0.3, -0.4, 0.2, 0.7, -0.4, 0.1, 0.8)
    x = scale * raw
    p = x.polar()
    assert p.reconstruct().isclose(x, rel_tol=3e-12, abs_tol=0)
    assert p.shifted(1, -2).reconstruct().isclose(x, rel_tol=3e-12, abs_tol=0)
    q = Ultra(1.1, -0.3, 0.2, 0.1, 0, 0.2).polar()
    assert (p * q).reconstruct().isclose(x * q.reconstruct(), rel_tol=4e-12, abs_tol=0)
    assert not p.v.tangent


def test_tiny_relative_phase_and_stretch_survive():
    h = 1e-30
    p = Ultra(1, j=h, i=0.25, ij=h).polar()
    assert p.rho == pytest.approx(1.25 * h / 1.0625, abs=0)
    assert p.phi == pytest.approx(0.75 * h / 1.0625, abs=0)


@pytest.mark.parametrize(("p", "m", "end"), [(1, 0, -J), (0, 1, J), (1, 1, -ONE), (-1, 1, -ONE)])
def test_cover_roundtrip(p, m, end):
    previous = None
    for k in range(193):
        t = math.tau * k / 96
        x = Ultra.from_channels((cmath.exp(1j * p * t), 0), (cmath.exp(1j * m * t), 0))
        previous = x.polar(previous=previous)
        assert (previous.root() ** 2).isclose(x)
        if k == 96:
            assert previous.root().isclose(end)
    assert previous.root().isclose(ONE)
    assert previous.phases == pytest.approx((p * 2 * math.tau, m * 2 * math.tau))


def test_cuts_singularities_and_ambiguous_sample():
    with pytest.raises(DomainError):
        (-ONE).polar(previous=ONE.polar())
    with pytest.raises(DomainError):
        (ONE + J).polar()
    with pytest.raises(ValueError):
        PolarForm(1, 0, 0, 0, EPS)
    assert set(ONE.roots().representatives()) == {ONE, -ONE, J, -J}
    assert list(EPS.roots().representatives()) == []
    with pytest.raises(DomainError):
        EPS.roots().at()
    root = ZERO.roots()
    assert root.count == math.inf and root.at(plus_tangent=3 - 2j, minus_tangent=7j) ** 2 == ZERO
    p = (ONE + J) * 0.5
    mixed = p.roots(3)
    assert mixed.count == math.inf and mixed.sheet_counts == (3, 1)
    for i in range(3):
        assert (mixed.at(i, minus_tangent=4j) ** 3).isclose(p)
    assert EPS.roots(1).at() == EPS
    tiny = Ultra(1, j=1e-80)
    assert list(tiny.roots(1).representatives()) == [tiny]
    with pytest.raises(ValueError):
        p.roots(0)
    with pytest.raises(ValueError):
        mixed.at(plus_tangent=1)
    z = Ultra(2, 0.1, 0.4, 0.7, -0.1, 0.2, 0.6, 0.3)
    for n in [2, 3, 5]:
        roots = list(z.roots(n).representatives())
        assert len(roots) == z.roots(n).count == n * n
        assert all((v**n).isclose(z) for v in roots)


def taylor_reference(operator, time):
    """Independent 4x4 complex block exponential for the body and its variation."""
    matrix = operator.matrix()
    body = [[complex(x.real, x.i) * time for x in row] for row in matrix]
    tangent = [[complex(x.eps, x.eps_i) * time for x in row] for row in matrix]
    block = [body[k] + tangent[k] for k in range(2)] + [[0, 0] + row for row in body]
    result = [[complex(i == j) for j in range(4)] for i in range(4)]
    term = result
    for n in range(1, 70):
        term = [
            [
                sum(x * y for x, y in zip(row, column, strict=True)) / n
                for column in zip(*block, strict=True)
            ]
            for row in term
        ]
        result = [
            [x + y for x, y in zip(row, t, strict=True)]
            for row, t in zip(result, term, strict=True)
        ]
    return result


@pytest.mark.parametrize("zeta", [0, 0.5, 1 - 1e-12, 1.0, 1 + 1e-12, 1.7])
@pytest.mark.parametrize("time", [-0.5, 0, 1.25])
def test_flow_across_damping_transition(zeta, time):
    generator = ModeOperator.from_matrix(ZERO, ONE, -ONE, -2 * (zeta + EPS))
    _compare_flow(generator, time)
    first = generator.flow(time / 2)
    assert (first @ first).alpha.isclose(generator.flow(time).alpha)
    assert (first @ first).beta.isclose(generator.flow(time).beta)


def _compare_flow(generator, time):
    actual = generator.flow(time).matrix()
    ref = taylor_reference(generator, time)
    for i, row in enumerate(actual):
        for j, x in enumerate(row):
            assert complex(x.real, x.i) == pytest.approx(ref[i][j], abs=8e-13, rel=1e-12)
            assert complex(x.eps, x.eps_i) == pytest.approx(ref[i][j + 2], abs=8e-13, rel=1e-12)


def test_noncommuting_complex_variation_and_physical_critical_solution():
    _compare_flow(ModeOperator.from_matrix(I + EPS, 1 + I * EPS, -0.3 * I, EPS * (1 + I)), 0.8)
    for time in [0.0, 1.0, 3.0]:
        m = ModeOperator.from_matrix(ZERO, ONE, -ONE, -2 * (ONE + EPS)).flow(time).matrix()
        assert m[0][0].real == pytest.approx((1 + time) * math.exp(-time))
        assert m[0][0].eps == pytest.approx(time**3 * math.exp(-time) / 3, abs=1e-14)
    with pytest.raises(TypeError):
        ModeOperator(ExactUltra(1), ExactUltra()).flow(1)
    with pytest.raises(ValueError):
        ModeOperator(ONE, ZERO).flow(math.inf)
