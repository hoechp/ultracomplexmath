import math

import pytest

from ultracomplexmath import EPS, ExpressionError, I, J, Ultra, evaluate
from ultracomplexmath.expressions import (
    BoundFormula,
    Calculation,
    FormulaSystem,
    Parameter,
    SimpleCalculation,
)
from ultracomplexmath.linalg import InconsistentSystemError, real_solution, solution_space
from ultracomplexmath.numbers import Binary, Complex, Dual
from ultracomplexmath.polynomial import Polynomial, guess


@pytest.mark.parametrize(
    "source,expected",
    [
        ("2î+3Ê+4ê", 2 * I + 3 * J + 4 * EPS),
        ("cos pi", -1),
        ("10_log(100)", 2),
        ("(1+î) dot (2+3î)", 5),
        ("(2+3î) part towards 1", 2),
        ("(2+3î) part orthogonal to 1", 3 * I),
        ("(2+3î) mirrored radial to 1", -2 + 3 * I),
        ("(2+3î) mirrored orthogonal to 1", 2 - 3 * I),
        ("2(3+4)", 14),
        ("2³", 8),
        ("-2²", -4),
        ("2^3^2", 512),
        ("1/2/2", 0.25),
        ("IM((1+î)^7)", -8),
        ("12%5", 2),
        ("round(-1.5)", -1),
        ("eulerlength(3+2Ê)", math.sqrt(5)),
        ("det(3+2Ê)", 5),
    ],
)
def test_legacy_grammar(source, expected):
    assert Calculation(source).result().isclose(expected)


@pytest.mark.parametrize(
    "source",
    [
        "open('x')",
        "x.__class__",
        "1;2",
        "x[1]",
        "?",
        "sin()",
        "x=1",
        "a" * 5000,
        "(" * 70 + "1" + ")" * 70,
    ],
)
def test_grammar_is_not_python_execution(source):
    with pytest.raises(ExpressionError):
        Calculation(source)


def test_simple_algebras_are_closed():
    assert SimpleCalculation("conjugate(1+2j)").result() == Binary(1, -2)
    assert SimpleCalculation("eulerlength(-2)").result(kind=Dual) == Dual(-2)
    assert SimpleCalculation("exp(2+eps)").result().isclose(Dual(math.exp(2), math.exp(2)))
    assert SimpleCalculation("sqrt(-1)").result() == Complex(0, 1)
    with pytest.raises(ValueError):
        SimpleCalculation("sqrt(-1)").result(kind=Binary)
    with pytest.raises(ExpressionError):
        SimpleCalculation("i+j").result()
    assert evaluate("12%5") == Ultra(2)
    with pytest.raises(ExpressionError):
        evaluate("i%2")


def test_mutable_parameter_dependencies_and_cycles():
    parameter = Parameter("x", 2)
    inner = BoundFormula("?²", ["x"]).set("x", parameter)
    outer = BoundFormula("sqrt(y)").set("y", inner)
    assert outer.result() == Ultra(2)
    parameter.set(4)
    assert outer.result() == Ultra(4)
    assert outer.result({"x": 9}) == Ultra(9)
    inner.set("x", outer)
    with pytest.raises(ExpressionError, match="cycle"):
        outer.result()
    assert BoundFormula("sin(x)", default_zero=True).result() == Ultra()
    with pytest.raises(ExpressionError, match="Missing"):
        BoundFormula("sin(x)").result()
    system = FormulaSystem("f=x²; x=sqrt(y), y=e^z; z=ln(a); a=b*c; b=sqrt(-1); c=(1+î)²")
    assert system.result().isclose(-2)
    system.set("y", 5)
    assert system.result().isclose(5)
    assert system.result({"x": 3}).isclose(9)
    system.set("x", "f")
    with pytest.raises(ExpressionError):
        system.result()


def test_rectangular_and_zero_divisor_solution_spaces():
    a = [[1, 2, 3], [2, 4, 6]]
    solution = real_solution(a, [4, 8])
    assert len(solution.basis) == 2
    for params in [(0, 0), (1, -3), (10, 5)]:
        x = solution.at(*params)
        assert [sum(v * w for v, w in zip(row, x, strict=True)) for row in a] == pytest.approx(
            [4, 8]
        )
    with pytest.raises(InconsistentSystemError):
        real_solution(a, [4, 9])
    assert real_solution([[1], [2]], [3, 6]).particular == (3,)
    for coefficient, rhs in [(EPS, EPS), (1 + J, 1 + J), (0, 0)]:
        answer = solution_space([[coefficient]], [rhs])
        x = answer.at(*range(len(answer.basis)))[0]
        assert (Ultra.coerce(coefficient) * x).isclose(rhs)
        for direction in answer.basis:
            assert (Ultra.coerce(coefficient) * direction[0]).isclose(0)
    with pytest.raises(InconsistentSystemError):
        solution_space([[EPS]], [1])
    with pytest.raises(InconsistentSystemError):
        solution_space([[1]], [I], basis_indices=(0,))
    complex_space = solution_space([[1, 1]], [2 + I], basis_indices=(0, 2))
    assert len(complex_space.basis) == 2
    x, y = complex_space.at(3, 4)
    assert (x + y).isclose(2 + I)


def test_interpolation_and_original_guesser():
    assert guess([1, 4, 9, 16]).isclose(25)
    assert guess([999, 4, 9, 16], 3).isclose(25)
    assert guess([2.53, 3.04, 3.70, 4.45, 5.31, 6.12, 6.90], 3).isclose(7.65)
    poly = Polynomial.interpolate([0, 1, 2], [I, 1 + I + EPS, 4 + I + 2 * EPS])
    assert poly(3).isclose(9 + I + 3 * EPS)
    assert poly(1 + EPS).isclose(1 + I + 3 * EPS)
    with pytest.raises(ValueError):
        Polynomial.interpolate([1, 1], [2, 3])
