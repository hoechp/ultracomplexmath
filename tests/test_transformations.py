import cmath
import math
from fractions import Fraction as F

import pytest

from ultracomplexmath import (
    EPS,
    ONE,
    QEPS,
    QI,
    QJ,
    QONE,
    QZERO,
    ZERO,
    DomainError,
    ExactUltra,
    Mobius,
    ModeOperator,
    NonInvertibleError,
    ProjectivePoint,
    Ultra,
    cross_ratio,
    evaluate,
)


def test_noncommuting_operators_unify_three_quadratic_types():
    identity = ModeOperator(QONE, QZERO)
    swap = ModeOperator(QZERO, QONE)
    split = ModeOperator(QJ, QZERO)
    circular = split @ swap
    parabolic = split + circular
    assert swap**2 == split**2 == identity
    assert split @ swap == -(swap @ split)
    assert circular**2 == -identity
    assert parabolic**2 == ModeOperator(QZERO, QZERO)
    assert parabolic != ModeOperator(QZERO, QZERO)
    value = ExactUltra(1, 2, 3, 4, 5, 6, 7, 8)
    assert (split @ swap)(value) != (swap @ split)(value)
    assert parabolic.cayley(ExactUltra(F(1, 3)))(value) == value + F(2, 3) * parabolic(value)


def test_general_coupling_matches_independent_matrix_and_composition():
    a, b, c, d = 2 + QEPS * QI, QI, QONE + QEPS, ExactUltra(3)
    operator = ModeOperator.from_matrix(a, b, c, d)
    assert operator.matrix() == ((a, b), (c, d))
    x, y = 2 + QI + QEPS, 3 - QI + QEPS * QI
    p, m = (QONE + QJ) / 2, (QONE - QJ) / 2
    value = x * p + y * m
    assert operator(value) == (a * x + b * y) * p + (c * x + d * y) * m
    assert operator.inverse()(operator(value)) == value
    other = ModeOperator(QI + QJ, QEPS + 1)
    assert (operator @ other)(value) == operator(other(value))
    assert operator**-1 == operator.inverse()
    assert operator**0 == ModeOperator(QONE, QZERO)
    with pytest.raises(ValueError):
        ModeOperator.from_matrix(QJ, QZERO, QZERO, QONE)
    with pytest.raises(NonInvertibleError):
        ModeOperator(QONE, QONE).inverse()


@pytest.mark.parametrize("kappa", [-1, 0, 1])
def test_exact_cayley_motion_across_elliptic_parabolic_hyperbolic_regimes(kappa):
    generator = ModeOperator.from_matrix(QZERO, QONE, ExactUltra(kappa), QZERO)
    t = ExactUltra(F(1, 3))
    transform = generator.cayley(t)
    denominator = F(1) - kappa * F(1, 9)
    a, b = (1 + kappa * F(1, 9)) / denominator, F(2, 3) / denominator
    assert transform.matrix() == (
        (ExactUltra(a), ExactUltra(b)),
        (ExactUltra(kappa * b), ExactUltra(a)),
    )
    assert transform.determinant() == QONE
    assert transform @ generator.cayley(-t) == ModeOperator(QONE, QZERO)


def test_coupled_exact_cayley_carries_parameter_sensitivity():
    # Differentiating the rational map at kappa=0 remains regular: no sqrt(kappa).
    generator = ModeOperator.from_matrix(QZERO, QONE, QEPS, QZERO)
    t = ExactUltra(F(1, 3))
    matrix = generator.cayley(t).matrix()
    assert matrix[0][0] == QONE + F(2, 9) * QEPS
    assert matrix[0][1] == F(2, 3) * QONE + F(2, 27) * QEPS
    assert matrix[1][0] == F(2, 3) * QEPS
    with pytest.raises(ValueError):
        generator.cayley(QJ)
    with pytest.raises(NonInvertibleError):
        ModeOperator.from_matrix(QZERO, QONE, QONE, QZERO).cayley(QONE)


def test_exact_mobius_cross_ratio_inverse_and_tangent():
    transform = Mobius(2 * QONE, QONE + QEPS, QONE, 3 * QONE)
    values = [ExactUltra(n, i=F(1, n + 2), j=F(1, 10), eps_ij=F(2, 7)) for n in (0, 1, 2, 3)]
    images = [transform(x) for x in values]
    assert cross_ratio(*images) == cross_ratio(*values)
    for x, y in zip(values, images, strict=True):
        assert transform.inverse()(y) == x
    second = Mobius(QI, QJ, QZERO, QONE)
    assert (transform @ second)(values[0]) == transform(second(values[0]))
    # Coefficients of this transform are constant; derivative is det/(cx+d)^2.
    constant = Mobius(2 * QONE, QONE, QONE, 3 * QONE)
    z = ExactUltra(2, 1, 3)
    dz = ExactUltra(3, 4, 5, 6)
    assert constant(z.with_tangent(dz)).tangent == constant.determinant() * dz / (z + 3) ** 2


def test_projective_null_divisor_boundaries_remain_valid_points():
    p, m = (QONE + QJ) / 2, (QONE - QJ) / 2
    point = ProjectivePoint(p, m)
    assert point.charts == ("x", "y")
    with pytest.raises(NonInvertibleError):
        point.affine()
    inversion = Mobius(QZERO, QONE, QONE, QZERO)
    mapped = inversion.apply_projective(point)
    assert mapped == ProjectivePoint(m, p)
    assert inversion.apply_projective(mapped).equivalent(point)
    unit = 2 + QI + QEPS
    assert ProjectivePoint(p * unit, m * unit).equivalent(point)
    assert not ProjectivePoint(QONE, QONE).equivalent(point)
    for x, y in [(QZERO, QZERO), (QEPS, QZERO), (p, QZERO), (p, p)]:
        with pytest.raises(ValueError):
            ProjectivePoint(x, y)
    infinity = ProjectivePoint(QONE, QZERO)
    assert inversion.apply_projective(infinity).affine() == QZERO
    with pytest.raises(NonInvertibleError):
        Mobius(p, QZERO, QZERO, QONE)


def test_numeric_operator_and_projective_variants_and_domain_separation():
    op = ModeOperator(Ultra(2), Ultra(i=1))
    value = Ultra(1, 2, 3, 4, 5, 6, 7, 8)
    assert op.inverse()(op(value)).isclose(value)
    mobius = Mobius(Ultra(2), ONE, ONE, Ultra(3))
    assert mobius.inverse()(mobius(value)).isclose(value)
    point = ProjectivePoint(value, ONE)
    assert mobius.inverse().apply_projective(mobius.apply_projective(point)).equivalent(point)
    with pytest.raises(TypeError):
        ModeOperator(ONE, QZERO)
    with pytest.raises(TypeError):
        Mobius(QONE, QZERO, QZERO, ONE)


def test_observables_preserve_phase_amplitude_and_real_sensitivities():
    value = Ultra.from_channels((3 + 4j, 2 - 1j), (1 + 2j, -2 + 3j))
    assert value.primal.with_tangent(value.tangent) == value
    assert value.real_part() + Ultra(i=1) * value.imag_part() == value
    expected_intensities = ((25 + 0j, 4 + 0j), (5 + 0j, 8 + 0j))
    assert value.abs2().channels() == expected_intensities
    for (z, w), (a, da), (p, dp) in zip(
        value.channels(), value.amplitude().channels(), value.phase().channels(), strict=True
    ):
        assert a.real == pytest.approx(math.hypot(z.real, z.imag))
        assert da.real == pytest.approx((z.real * w.real + z.imag * w.imag) / abs(z))
        assert p.real == pytest.approx(cmath.phase(z))
        assert dp.real == pytest.approx((z.real * w.imag - z.imag * w.real) / abs(z) ** 2)
        assert a.imag == da.imag == p.imag == dp.imag == 0
    assert evaluate("abs2(x)", {"x": value}) == value.abs2()
    assert evaluate("phase(x)", {"x": value}) == value.phase()
    assert ZERO.amplitude() == ZERO
    for operation in (EPS.amplitude, ZERO.phase, EPS.phase):
        with pytest.raises(DomainError):
            operation()
    # The documented tangent is the local unwrapped angle across the branch cut.
    phase = Ultra(-1, eps_i=1).phase()
    assert phase.real == math.pi and phase.eps == -1
