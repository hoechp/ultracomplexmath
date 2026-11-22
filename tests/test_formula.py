import json
import math
import subprocess
import sys

import pytest

from ultracomplexmath import EPS, ExpressionError, Formula, I, J, Ultra, evaluate, evaluate_system


@pytest.mark.parametrize(
    "text,expected",
    [
        ("2 + 2*2^2", 10),
        ("1/2/2", 0.25),
        ("-2^2", -4),
        ("2^3^2", 512),
        ("2^-2", 0.25),
        ("sqrt(-1)", I),
        ("exp(pi*i)", -1),
        ("eps^2", 0),
        ("j*j", 1),
        ("i*j*eps", I * J * EPS),
        ("2³ + 3²", 17),
        ("sin(π/2)", 1),
        ("log(8, 2)", 3),
        ("1e-3 + 2E-3", 0.003),
        ("î*Ê*ê", I * J * EPS),
        ("+0.5", 0.5),
        ("10^3", 1000),
        ("re(1+2*i+3*eps)", 1),
        ("sqr(eps) + cub(j)", J),
        ("abs(3+4*i)", 5),
    ],
)
def test_math_grammar(text, expected):
    assert evaluate(text).isclose(expected)


def test_parse_once_and_supply_different_variables():
    formula = Formula("1 + cos(x)*y^x")
    assert formula.variables == {"x", "y"}
    assert formula({"x": 3, "y": I + 2}).isclose(1 + math.cos(3) * (I + 2) ** 3)
    assert formula({"x": 0, "y": 7}) == Ultra(2)


def test_string_round_trip_all_components():
    a = Ultra(1.23456789012345, -2, 3, -4, 5, -6, 7e-80, -8)
    assert evaluate(str(a)) == a


@pytest.mark.parametrize(
    "expression",
    [
        "__import__('os')",
        "i.__class__",
        "i[0]",
        "[1,2]",
        "1 if 1 else 2",
        "lambda x:x",
        "open(1)",
        "sin(x=1)",
        "sin(1,2)",
        "True",
        "'text'",
        "x:=1",
        "[x for x in y]",
        "1//2",
        "3j",
        "2i",
        "1e999",
        "",
    ],
)
def test_rejected_grammar(expression):
    with pytest.raises(ExpressionError):
        Formula(expression)


def test_missing_variables_and_reserved_constants():
    with pytest.raises(ExpressionError, match="Missing variables"):
        evaluate("x + y", {"x": 1})
    with pytest.raises(ExpressionError, match="override"):
        evaluate("pi", {"pi": 3})


def test_expression_limits():
    for source in ["x" * 4097, "+" * 70 + "1", "+".join(["1"] * 200), "2^10001"]:
        with pytest.raises(ExpressionError):
            evaluate(source)


def test_dependency_system():
    results = evaluate_system({"result": "sqrt(y)", "y": "x^2", "x": "t+1"}, {"t": 3})
    assert results == {"result": Ultra(4), "y": Ultra(16), "x": Ultra(4)}
    assert evaluate_system({"x": Formula("t^2")}, {"t": 2}) == {"x": Ultra(4)}
    for definitions in [{"x": "y", "y": "x"}, {"x": "missing"}, {"i": 2}]:
        with pytest.raises(ExpressionError):
            evaluate_system(definitions)
    with pytest.raises(ExpressionError):
        evaluate_system({"x": 1}, {"x": 2})


def test_cli_success_and_failure():
    result = subprocess.run(
        [sys.executable, "-m", "ultracomplexmath", "i*i", "--json"],
        text=True,
        capture_output=True,
        check=True,
    )
    assert json.loads(result.stdout) == [-1, 0, 0, 0, 0, 0, 0, 0]
    failure = subprocess.run(
        [sys.executable, "-m", "ultracomplexmath", "1/eps"], text=True, capture_output=True
    )
    assert failure.returncode == 2
    assert "zero body" in failure.stderr
    assert "Traceback" not in failure.stderr
