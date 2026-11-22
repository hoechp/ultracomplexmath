"""Differentiate a real expression by evaluating it with a dual input."""

import math

from ultracomplexmath import EPS, Formula

f = Formula("exp(x)*sin(x)")
x = 0.7
value = f({"x": x + EPS})
expected_derivative = math.exp(x) * (math.sin(x) + math.cos(x))
assert math.isclose(value.eps, expected_derivative)
print(f"f({x}) = {value.real}")
print(f"f'({x}) = {value.eps}")
