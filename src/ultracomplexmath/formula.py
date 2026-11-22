"""Parse once, evaluate repeatedly: a restricted mathematical expression AST."""

from __future__ import annotations

import ast
import math
import operator
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import ClassVar

from .core import EPS, I, J, Scalar, Ultra
from .numbers import Binary, Complex, Dual, Hypercomplex


class ExpressionError(ValueError):
    """Invalid syntax, unsupported operation, missing name or dependency cycle."""


_CONSTANTS = {"pi": Ultra(math.pi), "e": Ultra(math.e), "i": I, "j": J, "eps": EPS}
_FUNCTIONS = {
    name: getattr(Ultra, name)
    for name in (
        "exp log ln sqrt sin cos tan sinh cosh tanh sec csc cot sech csch coth "
        "asin acos atan asinh acosh atanh asec acsc acot asech acsch acoth inverse conjugate "
        "real_part imag_part abs2 amplitude phase"
    ).split()
}
_FUNCTIONS.update(
    {
        "re": lambda x: Ultra(x.real),
        "RE": lambda x: Ultra(x.real),
        "abs": lambda x: Ultra(abs(x)),
        "neg": operator.neg,
        "sqr": lambda x: x * x,
        "cub": lambda x: x * x * x,
    }
)


def _pair(value: Ultra) -> Hypercomplex:
    for kind in (Complex, Binary, Dual):
        if all(c == 0 for k, c in enumerate(value) if k not in (0, kind.unit_index)):
            return kind(value.real, value.coefficients[kind.unit_index])
    raise ExpressionError("This geometric operation requires a two-dimensional number")


def _dot(a: Ultra, b: Ultra) -> Ultra:
    return Ultra(math.fsum(x * y for x, y in zip(a, b, strict=True)))


def _project(a: Ultra, b: Ultra) -> Ultra:
    from .geometry import project

    return Ultra.from_coefficients(project(a.coefficients, b.coefficients))


_FUNCTIONS.update(
    {
        "IM": lambda x: Ultra(_pair(x).imag),
        "im": lambda x: Ultra(_pair(x).imag),
        "length": lambda x: Ultra(abs(x)),
        "angle": lambda x: Ultra(_pair(x).angle),
        "eulerlength": lambda x: Ultra(_pair(x).euler_length),
        "eulerangle": lambda x: Ultra(_pair(x).euler_angle),
        "det": lambda x: Ultra(_pair(x).determinant),
        "normalized": lambda x: x / abs(x),
        "round": lambda x: Ultra(math.floor(x.real + 0.5)),
        "floor": lambda x: Ultra(math.floor(x.real)),
        "ceil": lambda x: Ultra(math.ceil(x.real)),
        "dot": _dot,
        "project": _project,
        "reject": lambda a, b: a - _project(a, b),
        "mirror_radial": lambda a, b: a - 2 * _project(a, b),
        "mirror_orthogonal": lambda a, b: 2 * _project(a, b) - a,
        "logbase": lambda a, b: b.log(a),
        "pairconjugate": lambda x: _pair(x).conjugate().to_ultra(),
    }
)
_TWO_ARGUMENTS = {"dot", "project", "reject", "mirror_radial", "mirror_orthogonal", "logbase"}


def _modulo(a: Ultra, b: Ultra) -> Ultra:
    if any(a.coefficients[1:]) or any(b.coefficients[1:]):
        raise ExpressionError("Modulo requires real operands")
    return Ultra(a.real % b.real)


_BINARY = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: _modulo,
}
_ALIASES = str.maketrans(
    {"^": "**", "²": "**2", "³": "**3", "π": "pi", "ε": "eps", "î": "i", "Ê": "j", "ê": "eps"}
)


@dataclass(frozen=True, slots=True)
class Formula:
    """Explicit operators, names and whitelisted calls; no Python eval/exec.

    Multiplication must be explicit (``2*i``). ``^`` is accepted as ``**``.
    Powers associate right; unary minus binds less tightly than powers.
    """

    source: str
    _tree: ast.expr = field(init=False, repr=False, compare=False)
    variables: frozenset[str] = field(init=False)
    max_length: ClassVar[int] = 4096
    max_nodes: ClassVar[int] = 512
    max_depth: ClassVar[int] = 64

    def __post_init__(self) -> None:
        if not isinstance(self.source, str):
            raise TypeError("Expression must be a string")
        if len(self.source) > self.max_length:
            raise ExpressionError("Expression is too long")
        try:
            tree = ast.parse(self.source.translate(_ALIASES).strip(), mode="eval").body
        except (SyntaxError, RecursionError) as error:
            raise ExpressionError(f"Invalid expression: {error}") from error
        if sum(1 for _ in ast.walk(tree)) > self.max_nodes:
            raise ExpressionError("Expression has too many nodes")
        variables: set[str] = set()

        def validate(node: ast.expr, depth: int = 0) -> None:
            if depth > self.max_depth:
                raise ExpressionError("Expression is nested too deeply")
            if isinstance(node, ast.Constant):
                if not isinstance(node.value, (int, float)) or isinstance(node.value, bool):
                    raise ExpressionError(
                        "Only real numeric literals are allowed; use i for sqrt(-1)"
                    )
                try:
                    Ultra.coerce(node.value)
                except (ArithmeticError, TypeError, ValueError) as error:
                    raise ExpressionError("Numeric literals must fit finite floats") from error
            elif isinstance(node, ast.Name):
                if node.id.startswith("_"):
                    raise ExpressionError("Names starting with '_' are reserved")
                if node.id not in _CONSTANTS:
                    variables.add(node.id)
            elif isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
                validate(node.operand, depth + 1)
            elif isinstance(node, ast.BinOp) and type(node.op) in _BINARY:
                validate(node.left, depth + 1)
                validate(node.right, depth + 1)
            elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                name = node.func.id
                if name not in _FUNCTIONS:
                    raise ExpressionError(f"Unknown function: {name}")
                arities = (
                    (1, 2) if name in ("log", "ln") else (2,) if name in _TWO_ARGUMENTS else (1,)
                )
                if node.keywords or len(node.args) not in arities:
                    raise ExpressionError(f"Wrong arguments for {name}")
                for argument in node.args:
                    validate(argument, depth + 1)
            else:
                raise ExpressionError(f"Unsupported expression: {type(node).__name__}")

        validate(tree)
        object.__setattr__(self, "_tree", tree)
        object.__setattr__(self, "variables", frozenset(variables))

    def evaluate(self, variables: Mapping[str, Scalar] | None = None) -> Ultra:
        supplied = dict(variables or {})
        if reserved := _CONSTANTS.keys() & supplied.keys():
            raise ExpressionError(f"Cannot override constants: {', '.join(sorted(reserved))}")
        if missing := self.variables - supplied.keys():
            raise ExpressionError(f"Missing variables: {', '.join(sorted(missing))}")
        values = _CONSTANTS | {name: Ultra.coerce(supplied[name]) for name in self.variables}

        def visit(node: ast.expr) -> Ultra:
            if isinstance(node, ast.Constant):
                assert isinstance(node.value, (int, float))
                return Ultra.coerce(node.value)
            if isinstance(node, ast.Name):
                return values[node.id]
            if isinstance(node, ast.UnaryOp):
                value = visit(node.operand)
                return -value if isinstance(node.op, ast.USub) else value
            if isinstance(node, ast.BinOp):
                left, right = visit(node.left), visit(node.right)
                if isinstance(node.op, ast.Pow) and abs(right) > 10000:
                    raise ExpressionError("Expression exponent exceeds magnitude limit 10000")
                return Ultra.coerce(_BINARY[type(node.op)](left, right))
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                return Ultra.coerce(_FUNCTIONS[node.func.id](*(visit(arg) for arg in node.args)))
            raise AssertionError("AST was not validated")

        return visit(self._tree)

    __call__ = evaluate


def evaluate(source: str, variables: Mapping[str, Scalar] | None = None) -> Ultra:
    """One-shot expression evaluation; reuse Formula for repeated calculations."""
    return Formula(source).evaluate(variables)


def evaluate_system(
    definitions: Mapping[str, str | Formula | Scalar],
    inputs: Mapping[str, Scalar] | None = None,
) -> dict[str, Ultra]:
    """Evaluate named formula dependencies, rejecting cycles and missing names.

    Inputs and definitions must have disjoint names. Only definition results
    are returned; intermediate values are evaluated once within this call.
    """
    if len(definitions) > 256:
        raise ExpressionError("At most 256 definitions are allowed")
    values = {name: Ultra.coerce(value) for name, value in (inputs or {}).items()}
    if definitions.keys() & values.keys():
        raise ExpressionError("Inputs and definitions overlap")
    if _CONSTANTS.keys() & (definitions.keys() | values.keys()):
        raise ExpressionError("A system cannot redefine constants")
    for name in definitions.keys() | values.keys():
        if not name.isidentifier() or name.startswith("_"):
            raise ExpressionError(f"Invalid variable name: {name}")
    pending = dict(definitions)
    active: list[str] = []

    def resolve(name: str) -> Ultra:
        if name in values:
            return values[name]
        if name in active:
            raise ExpressionError("Dependency cycle: " + " -> ".join([*active, name]))
        if name not in pending:
            raise ExpressionError(f"Missing variable: {name}")
        active.append(name)
        expression = pending[name]
        if isinstance(expression, str):
            expression = Formula(expression)
        if isinstance(expression, Formula):
            context = {key: resolve(key) for key in sorted(expression.variables)}
            value = expression.evaluate(context)
        else:
            value = Ultra.coerce(expression)
        active.pop()
        values[name] = value
        return value

    return {name: resolve(name) for name in definitions}
