"""Independent exact checks and deliberate non-generalization of research claims."""

import math
import random
from fractions import Fraction as F

import pytest

from examples.novelty_models import (
    QIDENTITY,
    QNULL,
    corrected_critical_cayley,
    critical_center,
    critical_polynomial,
    direct_reciprocal,
    first_power_defect,
    first_power_rank,
    interval_band,
    interval_band_rank,
    toeplitz_block,
    toeplitz_shape,
)
from tools.novelty_probe import (
    block_exponential_reference,
    interval_graph_rank,
    nilpotent_tensor_matrix,
    rational_rank,
)
from ultracomplexmath import (
    ONE,
    QEPS,
    QI,
    QONE,
    QZERO,
    DomainError,
    ExactUltra,
    ModeOperator,
    NonInvertibleError,
    Ultra,
)


def test_interval_formula_against_two_independent_representations():
    rng = random.Random(419)
    for _ in range(150):
        rows, columns, degree = (rng.randint(1, 13) for _ in range(3))
        allowed = [c for c in range(degree + 1) if 0 <= columns - rows + c <= degree]
        if not allowed:
            continue
        offset = rng.choice(allowed)
        matrix = interval_band(rows, columns, degree, offset)
        rank = rational_rank(matrix)
        assert interval_band_rank(rows, columns, degree, offset) == rank
        assert interval_graph_rank(matrix) == rank
        assert interval_band_rank(columns, rows, degree, degree - offset) == rank


@pytest.mark.parametrize("m,n,d,rank,defect", [(4, 4, 4, 3, 1), (5, 5, 4, 5, 4), (6, 6, 2, 24, 1)])
def test_published_and_additional_rank_losses(m, n, d, rank, defect):
    assert first_power_rank(m, n, d) == rank
    assert first_power_defect(m, n, d) == defect
    assert rational_rank(nilpotent_tensor_matrix(m, n, d)) == rank


def test_published_annihilator_and_higher_power_counterexample():
    # Noferini Example 4.18, beyond that paper's sufficient condition.
    matrix = toeplitz_block(6, 6, 2, 1, 7)
    witness = (1, -1, 0, 1, -1)
    assert all(sum(a * b for a, b in zip(row, witness, strict=True)) == 0 for row in matrix)
    assert rational_rank(matrix) == 4
    # Published Example 4.17 is a separate weighted regression fixture.
    weighted = toeplitz_block(4, 8, 3, 2, 9)
    assert weighted == [[2, 3, 4], [1, 2, 3], [0, 1, 2]]
    assert rational_rank(weighted) == 2
    # A smaller ell=2 counterexample: the all-ones support loses the weights.
    weighted = toeplitz_block(3, 3, 1, 2, 4)
    assert weighted == [[2, 1], [1, 2]]
    assert rational_rank(weighted) == 2
    assert interval_band_rank(2, 2, 2, 1) == 1


def test_rank_zero_boundaries_and_large_parameters_without_matrices():
    for m in range(1, 7):
        for n in range(m, 8):
            assert first_power_rank(m, n, m + n - 1) == 0
            assert first_power_rank(m, n, m + n + 9) == 0
            assert first_power_defect(m, n, m + n) == 0
            if n > m:
                assert first_power_defect(m, n, n - m) == 0
        assert interval_band_rank(m, m, 0, 0) == m
    size = 10**18
    assert first_power_rank(size, size, size - 1) == size
    assert first_power_defect(size, size, size - 1) == (size - 1) ** 2 // 4
    assert interval_band_rank(size, size, 2 * size, size) == 1


@pytest.mark.parametrize("args", [(0, 2, 1, 0), (2, 3, 1, 1), (2, 2, 1, 2)])
def test_band_domain_rejects_outside_theorem(args):
    with pytest.raises(ValueError):
        interval_band_rank(*args)


@pytest.mark.parametrize("args", [(False, 2, 1), (2, 3.0, 1), (2, 3, True)])
def test_rank_parameters_are_integers(args):
    with pytest.raises(TypeError):
        first_power_rank(*args)


def test_jordan_domain():
    with pytest.raises(ValueError):
        first_power_defect(3, 2, 1)
    with pytest.raises(ValueError):
        toeplitz_shape(2, 2, 2, 2, 3)
    with pytest.raises(ValueError):
        first_power_rank(2, 2, 0)


def test_cubic_term_is_real_information_not_a_redundant_power():
    b = ModeOperator.from_matrix(QZERO, QONE, QEPS, QZERO)
    assert b**2 == QIDENTITY.scaled(QEPS)
    assert b**3 != QNULL and b**4 == QNULL
    t = F(3, 2)
    expected = ModeOperator.from_matrix(
        QONE + QEPS * t**2 / 2,
        QONE * t + QEPS * t**3 / 6,
        QEPS * t,
        QONE + QEPS * t**2 / 2,
    )
    assert critical_polynomial(b, t) == expected
    uncorrected = b.cayley(QONE * t / 2)
    assert uncorrected - expected == (b**3).scaled(QONE * t**3 / 12)
    assert corrected_critical_cayley(b, t, 1) == expected


@pytest.mark.parametrize("steps", [-13, -1, 0, 1, 17])
def test_critical_damping_variation_and_exact_cayley_correction(steps):
    damping = ModeOperator.from_matrix(QZERO, QONE, -QONE, -2 * (QONE + QEPS))
    mu, b = critical_center(damping)
    assert mu == -QONE - QEPS
    assert b**2 == QIDENTITY.scaled(2 * QEPS)
    assert corrected_critical_cayley(b, F(1, 7), steps) == critical_polynomial(b, F(steps, 7))
    # Independent real block matrix; not ModeOperator composition.
    matrix = b.matrix()
    oracle = block_exponential_reference(
        [[x.real for x in row] for row in matrix],
        [[x.eps for x in row] for row in matrix],
        F(steps, 7),
    )
    actual = critical_polynomial(b, F(steps, 7)).matrix()
    for i in range(2):
        for j in range(2):
            assert actual[i][j] == ExactUltra(oracle[i][j], eps=oracle[i][j + 2])


def test_complex_coefficients_and_independent_nilpotents():
    b = ModeOperator.from_matrix(QZERO, QI, QEPS, QZERO)
    t = F(2, 3)
    assert b**2 == QIDENTITY.scaled(QI * QEPS)
    assert critical_polynomial(b, t).matrix() == (
        (QONE + QI * QEPS * t**2 / 2, QI * t - QEPS * t**3 / 6),
        (QEPS * t, QONE + QI * QEPS * t**2 / 2),
    )


def test_critical_domain_rejects_approximate_bodies_and_wrong_scalar_types():
    near = ModeOperator.from_matrix(QZERO, QONE, QONE / 10**12, QZERO)
    with pytest.raises(ValueError, match="near-critical"):
        critical_polynomial(near, 1)
    with pytest.raises(ValueError, match="full trace"):
        critical_polynomial(QIDENTITY, 1)
    with pytest.raises(TypeError):
        critical_center(ModeOperator(ONE, 0 * ONE))
    with pytest.raises(TypeError):
        critical_polynomial(QNULL, 0.5)
    with pytest.raises(TypeError):
        corrected_critical_cayley(QNULL, 1, True)


@pytest.mark.parametrize("exponent", [4, 8, 10, 40, 100, 140])
def test_tiny_mixed_reciprocal_components_against_exact_float_inputs(exponent):
    h = 10.0**-exponent
    value = Ultra(1, i=h, ij=h, eps=1)
    expected = ExactUltra(1, i=F(h), ij=F(h), eps=1).inverse().approximate()
    actual = direct_reciprocal(value)
    for a, b in zip(actual, expected, strict=True):
        assert math.isclose(a, b, rel_tol=3e-15, abs_tol=0)
    if exponent >= 10:
        assert actual.j != 0 and actual.eps_j != 0


@pytest.mark.parametrize("scale", [1e-150, 1, 1e150])
def test_reciprocal_scaling_and_general_variations(scale):
    rng = random.Random(651)
    for _ in range(20):
        values = [3.0] + [rng.uniform(-0.5, 0.5) for _ in range(7)]
        value = Ultra(*(x * scale for x in values))
        oracle = ExactUltra(*(F(x) for x in value)).inverse().approximate()
        actual = direct_reciprocal(value)
        for a, b in zip(actual, oracle, strict=True):
            assert math.isclose(a, b, rel_tol=2e-13, abs_tol=2e-15 / scale)


def test_reciprocal_domain_separates_singularity_from_experimental_guard():
    for value in (Ultra(), Ultra(1, j=1), Ultra(1, j=-1)):
        with pytest.raises(NonInvertibleError):
            direct_reciprocal(value)
    with pytest.raises(DomainError, match="excludes"):
        direct_reciprocal(Ultra(1, j=1 - 1e-10))
    with pytest.raises(TypeError):
        direct_reciprocal(QONE)
