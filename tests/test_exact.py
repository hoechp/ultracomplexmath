import json
import subprocess
import sys
from fractions import Fraction as F
from itertools import permutations

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

# An independent literal multiplication table, shared with the numerical oracle.
from test_core import TABLE

from ultracomplexmath import (
    QEPS,
    QI,
    QJ,
    QONE,
    QZERO,
    DomainError,
    ExactBinary,
    ExactComplex,
    ExactDual,
    ExactFormula,
    ExactMatrix,
    ExactPolynomial,
    ExactUltra,
    ExpressionError,
    InconsistentSystemError,
    NonInvertibleError,
    SingularSystemError,
    Ultra,
    evaluate_exact,
    exact_solution_space,
    exact_solve,
)


@pytest.mark.parametrize("a", range(8))
@pytest.mark.parametrize("b", range(8))
def test_exact_basis(a, b):
    code = TABLE[a][b]
    expected = QZERO if not code else ExactUltra.unit(abs(code) - 1) * (1 if code > 0 else -1)
    assert ExactUltra.unit(a) * ExactUltra.unit(b) == expected


rationals = st.builds(F, st.integers(-12, 12), st.integers(1, 13))
numbers = st.builds(ExactUltra, *(rationals for _ in range(8)))


@given(numbers, numbers, numbers)
@settings(max_examples=45, derandomize=True)
def test_exact_algebra_including_mixed_directions(a, b, c):
    assert a * b == b * a
    assert a * (b + c) == a * b + a * c
    assert (a * b) * c == a * (b * c)
    assert ExactUltra.from_channels(*a.channels()) == a
    for generator in ("i", "j", "eps"):
        assert (a * b).conjugate(generator) == a.conjugate(generator) * b.conjugate(generator)
    if a.is_invertible:
        assert a * a.inverse() == QONE
        assert a / a == QONE
    else:
        with pytest.raises(NonInvertibleError):
            a.inverse()


def test_arbitrary_integer_and_fraction_precision_and_boundaries():
    n = 10**400 + 1
    x = ExactUltra(n, F(1, n), F(n, 7), eps_ij=F(2, 13))
    assert x.real == n
    assert x * x.inverse() == QONE
    assert QI**n == QI
    assert (-QONE) ** -n == -QONE
    assert QJ**n == QJ
    assert QEPS**n == QZERO
    assert ExactUltra.from_json(x.to_json()) == x
    payload = json.loads(x.to_json())
    assert all(isinstance(v, str) for pair in payload["coefficients"] for v in pair)
    for value in (True, 0.1, Ultra(1), complex(1, 2)):
        with pytest.raises(TypeError):
            ExactUltra(value)
        with pytest.raises(TypeError):
            _ = QONE + value
    assert ExactUltra.from_approximate(Ultra(0.1)).real == F.from_float(0.1)
    assert ExactUltra(F(1, 8)).approximate() == Ultra(0.125)


@pytest.mark.parametrize(
    "kind,square,index", [(ExactComplex, -1, 2), (ExactBinary, 1, 1), (ExactDual, 0, 4)]
)
def test_closed_exact_types(kind, square, index):
    u = kind(0, 1)
    assert u * u == kind(square)
    value = kind(F(7, 3), F(2, 5))
    assert value * value.inverse() == kind(1)
    assert value.to_ultra() == ExactUltra(F(7, 3)) + ExactUltra.unit(index) * F(2, 5)
    assert kind.from_ultra(value.to_ultra()) == value
    assert value.approximate().real == float(F(7, 3))
    assert value.to_ultra() * QEPS == value.real * QEPS + value.imag * QEPS * ExactUltra.unit(index)
    with pytest.raises(TypeError):
        kind(0.1)


def test_no_reinterpretation_between_closed_types():
    with pytest.raises(TypeError):
        _ = ExactComplex(1, 2) + ExactDual(3, 4)
    result = ExactComplex(1, 2).to_ultra() * ExactDual(3, 4).to_ultra()
    assert result == ExactUltra(real=3, i=6, eps=4, eps_i=8)
    with pytest.raises(DomainError):
        ExactDual.from_ultra(QI)


@pytest.mark.parametrize(
    "value,expected",
    [
        (ExactUltra(4, eps=2), ExactUltra(2, eps=F(1, 2))),
        (ExactUltra.complex(3, 4), ExactUltra.complex(2, 1)),
        (ExactUltra.complex(3, -4), ExactUltra.complex(2, -1)),
        (-QONE, QI),
        (QZERO, QZERO),
        ((QONE + QJ) / 2, (QONE + QJ) / 2),
    ],
)
def test_exact_square_roots(value, expected):
    assert value.sqrt() == expected
    assert value ** F(1, 2) == expected
    assert expected**2 == value


def test_irrational_and_nonexistent_roots_are_explicit():
    for value in (ExactUltra(2), QEPS):
        with pytest.raises(DomainError):
            value.sqrt()
    with pytest.raises(DomainError):
        QONE ** F(1, 3)
    with pytest.raises(NonInvertibleError):
        QEPS**-1
    with pytest.raises(TypeError):
        QONE**True


def test_exact_differentials_and_real_observables():
    body = ExactUltra(2, 1, 3, 4)
    tangent = ExactUltra(7, 8, 9, 10)
    x = body.with_tangent(tangent)
    assert x.primal == body
    assert x.tangent == tangent
    assert (x**3).tangent == 3 * body**2 * tangent
    assert x.real_part() + QI * x.imag_part() == x
    assert x.abs2().tangent == body.conjugate() * tangent + body * tangent.conjugate()
    assert x.abs2().conjugate() == x.abs2()
    with pytest.raises(ValueError):
        body.with_tangent(QEPS)


@pytest.mark.parametrize(
    "source,expected",
    [
        ("0.1 + 0.2 - 0.3", QZERO),
        ("1e-400 * 1e400", QONE),
        ("9007199254740993 - 9007199254740992", QONE),
        ("(i+j+eps)^2", 2 * QI * QJ + 2 * QEPS * (QI + QJ)),
        ("sqrt(3+4*i)", 2 + QI),
        ("floor(-7/3)", ExactUltra(-3)),
        ("ceil(-7/3)", ExactUltra(-2)),
        ("7/3 % (1/2)", ExactUltra(F(1, 3))),
        ("(7/3)//(1/2)", ExactUltra(4)),
        ("tangent((2+eps)^3)", ExactUltra(12)),
        ("conj_j(1+j)", QONE - QJ),
        ("ε²", QZERO),
    ],
)
def test_exact_formula_literals(source, expected):
    assert evaluate_exact(source) == expected


def test_exact_formula_variables_and_restrictions():
    f = ExactFormula("x^3 + abs2(y)")
    assert f({"x": F(2, 3), "y": QI}) == ExactUltra(F(35, 27))
    for source in (
        "True",
        "__import__('os')",
        "x.real",
        "pi",
        "sin(1)",
        "[1]",
        "2**10001",
        "1e10001",
    ):
        with pytest.raises(ExpressionError):
            evaluate_exact(source)
    with pytest.raises(ExpressionError):
        f({"x": 1})
    with pytest.raises(ExpressionError):
        evaluate_exact("1", {"i": QJ})
    with pytest.raises(TypeError):
        f({"x": 0.5, "y": QI})
    with pytest.raises(ExpressionError):
        evaluate_exact("floor(i)")


def test_exact_cli_and_lossless_json():
    result = subprocess.run(
        [sys.executable, "-m", "ultracomplexmath", "--exact", "--json", "0.1+0.2"],
        text=True,
        capture_output=True,
        check=True,
    )
    assert ExactUltra.from_json(result.stdout) == ExactUltra(F(3, 10))


def test_exact_matrix_inverse_despite_every_entry_being_a_zero_divisor():
    p, m = (QONE + QJ) / 2, (QONE - QJ) / 2
    matrix = ExactMatrix([[p, m], [m, p]])
    assert all(not v.is_invertible for row in matrix.rows for v in row)
    assert matrix.determinant() == QJ
    assert matrix @ matrix.inverse() == ExactMatrix.identity(2)
    assert matrix**-1 == matrix
    rhs = (QI + QEPS, ExactUltra(F(1, 3)))
    assert matrix.apply(matrix.solve(rhs)) == rhs


def test_exact_determinant_against_leibniz_permutation_formula():
    matrix = ExactMatrix([[QEPS, QJ, 2], [QI, F(1, 3), 4 + QEPS * QJ], [5, 6, 7 + QI]])
    reference = QZERO
    for permutation in permutations(range(3)):
        inversions = sum(permutation[i] > permutation[j] for i in range(3) for j in range(i + 1, 3))
        product = ExactUltra((-1) ** inversions)
        for row, col in enumerate(permutation):
            product *= matrix.rows[row][col]
        reference += product
    assert matrix.determinant() == reference
    assert matrix @ matrix.inverse() == ExactMatrix.identity(3)


def test_complete_exact_solution_families_and_inconsistency():
    solution = exact_solution_space([[QEPS]], [QEPS])
    assert len(solution.basis) == 4
    assert QEPS * solution.at(F(1, 3), 2, -3, 4)[0] == QEPS
    assert all(QEPS * v[0] == QZERO for v in solution.basis)
    with pytest.raises(SingularSystemError):
        exact_solve([[QEPS]], [QEPS])
    with pytest.raises(InconsistentSystemError):
        exact_solve([[QEPS]], [QONE])
    closed = exact_solution_space([[QEPS]], [QEPS], basis_indices=(0, 4))
    assert len(closed.basis) == 1
    assert exact_solve([[F(1, 10**400)]], [1]) == (ExactUltra(10**400),)
    rectangular = exact_solution_space([[1, 2]], [3], basis_indices=(0,))
    x, y = rectangular.at(F(1, 7))
    assert x + 2 * y == ExactUltra(3)


def test_exact_polynomial_calculus_interpolation_and_division():
    polynomial = ExactPolynomial([F(1, 3), QI, QJ, QEPS, 7])
    assert polynomial.integral().derivative() == polynomial
    x = ExactUltra(2, 1, 3)
    assert polynomial(x + QEPS).tangent == polynomial(x).tangent + polynomial.derivative()(x).primal
    assert polynomial.derivative(100).degree == -1
    nodes = [F(-3, 2), 0, F(2, 3), 2, 5]
    assert ExactPolynomial.interpolate(nodes, [polynomial(t) for t in nodes]) == polynomial
    divisor = ExactPolynomial([QI, 1])
    quotient, remainder = divmod(polynomial, divisor)
    assert quotient * divisor + remainder == polynomial
    assert remainder.degree < divisor.degree
    assert divmod(polynomial, ExactPolynomial([1])) == (polynomial, ExactPolynomial([]))
    with pytest.raises(NonInvertibleError):
        divmod(polynomial, ExactPolynomial([1, QEPS]))


def test_exact_hermite_matches_values_and_tangents():
    xs = [F(1, 3), F(2, 3)]
    ys, ds = [QI + QJ, QEPS * QI], [QEPS + 2, 3 * QJ]
    p = ExactPolynomial.hermite(xs, ys, ds)
    for x, y, d in zip(xs, ys, ds, strict=True):
        assert p(x) == y
        assert p.derivative()(x) == d


@pytest.mark.parametrize(
    "payload",
    ["{}", '{"algebra":"wrong"}', '{"algebra":"Q[i,j,eps]","version":1,"coefficients":[]}'],
)
def test_invalid_serialization(payload):
    with pytest.raises(ValueError):
        ExactUltra.from_json(payload)
