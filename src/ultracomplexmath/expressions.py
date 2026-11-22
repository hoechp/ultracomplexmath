"""Legacy mathematical grammar and live, composable formula parameters.

The grammar is translated to the same validated AST as Formula. It accepts
implicit multiplication, prefix functions, postfix powers and word operators.
No eval, executable attributes, assignment execution or stale result caches.
"""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field

from .core import Scalar, Ultra
from .formula import _FUNCTIONS, ExpressionError, Formula, _modulo
from .numbers import Binary, Complex, Dual, Hypercomplex

_INFIX = {
    "+": (10, "+"),
    "-": (10, "-"),
    "dot": (15, "dot"),
    "*": (20, "*"),
    "/": (20, "/"),
    "%": (20, "%"),
    "_log": (25, "logbase"),
    "^": (30, "**"),
    "**": (30, "**"),
    "mirrored radial to": (25, "mirror_radial"),
    "mirrored orthogonal to": (25, "mirror_orthogonal"),
    "part towards": (25, "project"),
    "part orthogonal to": (25, "reject"),
}
_TOKEN = re.compile(
    r"\s*(mirrored\s+radial\s+to|mirrored\s+orthogonal\s+to|part\s+orthogonal\s+to|part\s+towards|_log|(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?|[A-Za-z_][A-Za-z_0-9]*|\*\*|[()+*/^,%²³-])"
)


@dataclass(frozen=True)
class CalculationNode:
    operator: str
    children: tuple[CalculationNode, ...] = ()

    def __str__(self) -> str:
        if not self.children:
            return self.operator
        if self.operator in {"+", "-", "*", "/", "**", "%"} and len(self.children) == 2:
            return f"({self.children[0]}{self.operator}{self.children[1]})"
        if self.operator in {"+", "-"}:
            return f"({self.operator}{self.children[0]})"
        return f"{self.operator}({','.join(map(str, self.children))})"


def parse(source: str) -> CalculationNode:
    if len(source) > Formula.max_length:
        raise ExpressionError("Expression is too long")
    source = source.translate(
        {
            ord(k): v
            for k, v in {"î": " i ", "Ê": " j ", "ê": " eps ", "ε": " eps ", "π": " pi "}.items()
        }
    ).strip()
    tokens, position = [], 0
    while position < len(source):
        match = _TOKEN.match(source, position)
        if match is None:
            raise ExpressionError(f"Unexpected input at character {position}")
        tokens.append(" ".join(match[1].split()))
        position = match.end()
    if len(tokens) > Formula.max_nodes:
        raise ExpressionError("Too many tokens")
    cursor = 0

    def expression(minimum: int = 0, depth: int = 0) -> CalculationNode:
        nonlocal cursor
        if depth > Formula.max_depth:
            raise ExpressionError("Expression nested too deeply")
        if cursor >= len(tokens):
            raise ExpressionError("Missing operand")
        token = tokens[cursor]
        cursor += 1
        if token in ("+", "-"):
            left = CalculationNode(token, (expression(29, depth + 1),))
        elif token == "(":
            left = expression(0, depth + 1)
            if cursor >= len(tokens) or tokens[cursor] != ")":
                raise ExpressionError("Missing closing parenthesis")
            cursor += 1
        elif token in _FUNCTIONS:
            if cursor < len(tokens) and tokens[cursor] == "(":
                cursor += 1
                args = [expression(0, depth + 1)]
                while cursor < len(tokens) and tokens[cursor] == ",":
                    cursor += 1
                    args.append(expression(0, depth + 1))
                if cursor >= len(tokens) or tokens[cursor] != ")":
                    raise ExpressionError("Missing closing parenthesis")
                cursor += 1
                left = CalculationNode(token, tuple(args))
            else:
                left = CalculationNode(token, (expression(30, depth + 1),))
        elif token[0].isalnum() or token[0] in "._":
            left = CalculationNode(token)
        else:
            raise ExpressionError(f"Unexpected token {token}")
        while cursor < len(tokens):
            token = tokens[cursor]
            if token in ("²", "³"):
                if 40 < minimum:
                    break
                cursor += 1
                left = CalculationNode("**", (left, CalculationNode("2" if token == "²" else "3")))
                continue
            if token in ("(",) or (token not in _INFIX and token not in (",", ")")):
                precedence, op, implicit = 20, "*", True
            elif token in _INFIX:
                precedence, op = _INFIX[token]
                implicit = False
            else:
                break
            if precedence < minimum:
                break
            if not implicit:
                cursor += 1
            right = expression(precedence if op == "**" else precedence + 1, depth + 1)
            left = CalculationNode(op, (left, right))
        return left

    root = expression()
    if cursor != len(tokens):
        raise ExpressionError("Unexpected trailing tokens")
    return root


@dataclass
class Calculation:
    source: str
    node: CalculationNode = field(init=False)
    formula: Formula = field(init=False)

    def __post_init__(self) -> None:
        self.node = parse(self.source)
        self.formula = Formula(str(self.node))

    def result(self, variables: Mapping[str, Scalar] | None = None) -> Ultra:
        return self.formula(variables)


class SimpleCalculation:
    """Evaluate in one closed two-dimensional algebra, inferred from its unit.

    Pass ``kind=Dual`` or ``kind=Binary`` for expressions containing only real
    literals. Mixed units are rejected; Calculation provides the full algebra.
    """

    def __init__(self, source: str) -> None:
        calculation = Calculation(source)
        self.source, self.node = source, calculation.node

    def result(
        self,
        variables: Mapping[str, Scalar] | None = None,
        *,
        kind: type[Hypercomplex] | None = None,
    ) -> Hypercomplex:
        import math

        supplied = {n: Ultra.coerce(v) for n, v in (variables or {}).items()}
        units: set[str] = set()

        def find_units(node: CalculationNode) -> None:
            if not node.children and node.operator in ("i", "j", "eps"):
                units.add(node.operator)
            for child in node.children:
                find_units(child)

        find_units(self.node)
        for value in supplied.values():
            units.update(
                symbol
                for index, symbol in ((2, "i"), (1, "j"), (4, "eps"))
                if value.coefficients[index]
            )
        if len(units) > 1:
            raise ExpressionError("SimpleCalculation requires a single algebra")
        algebra = kind or {"i": Complex, "j": Binary, "eps": Dual}.get(
            next(iter(units), "i"), Complex
        )
        if units - {algebra.symbol}:
            raise ExpressionError("Unit does not belong to the selected algebra")

        def walk(node: CalculationNode) -> Hypercomplex:
            op = node.operator
            if not node.children:
                if op in supplied:
                    return algebra.from_ultra(supplied[op])
                if op in ("i", "j", "eps"):
                    return algebra(0, 1)
                if op in ("pi", "e"):
                    return algebra(math.pi if op == "pi" else math.e)
                try:
                    return algebra(float(op))
                except ValueError as error:
                    raise ExpressionError(f"Missing variable: {op}") from error
            args = [walk(child) for child in node.children]
            a = args[0]
            if len(args) == 1:
                if op in ("-", "neg"):
                    return -a
                if op == "+":
                    return a
                if op in ("conjugate", "pairconjugate"):
                    return a.conjugate()
                properties = {
                    "det": "determinant",
                    "eulerlength": "euler_length",
                    "eulerangle": "euler_angle",
                    "angle": "angle",
                    "length": "length",
                    "IM": "imag",
                    "im": "imag",
                }
                if op in properties:
                    return algebra(getattr(a, properties[op]))
            elif len(args) == 2:
                b = args[1]
                if op == "+":
                    return a + b
                if op == "-":
                    return a - b
                if op == "*":
                    return a * b
                if op == "/":
                    return a / b
                if op == "**":
                    return a**b
                if op == "%":
                    return algebra.from_ultra(_modulo(a.to_ultra(), b.to_ultra()))
                if op in ("log", "logbase"):
                    return a.log(b) if op == "log" else b.log(a)
            return algebra.from_ultra(_FUNCTIONS[op](*(a.to_ultra() for a in args)))

        return walk(self.node)


SimpleCalculationNode = CalculationNode


@dataclass
class Parameter:
    identifier: str
    value: str | Scalar | BoundFormula = 0.0

    def set(self, value: str | Scalar | BoundFormula) -> None:
        self.value = value


@dataclass(init=False)
class BoundFormula:
    calculation: Calculation
    parameters: dict[str, Parameter]
    default_zero: bool

    def __init__(
        self, source: str, names: Sequence[str] = (), *, default_zero: bool = False
    ) -> None:
        if source.count("?") != len(names):
            raise ExpressionError("One name is required per ? placeholder")
        for name in names:
            source = source.replace("?", name, 1)
        self.calculation = Calculation(source)
        self.parameters = {}
        self.default_zero = default_zero

    def set(self, name: str, value: str | Scalar | BoundFormula | Parameter) -> BoundFormula:
        self.parameters[name] = value if isinstance(value, Parameter) else Parameter(name, value)
        return self

    def result(self, inputs: Mapping[str, Scalar] | None = None) -> Ultra:
        supplied = dict(inputs or {})
        active: set[tuple[int, str]] = set()

        def evaluate_bound(bound: BoundFormula) -> Ultra:
            def resolve(name: str) -> Ultra:
                if name in supplied:
                    return Ultra.coerce(supplied[name])
                key = id(bound), name
                if key in active:
                    raise ExpressionError(f"Dependency cycle at {name}")
                if name not in bound.parameters:
                    if bound.default_zero:
                        return Ultra()
                    raise ExpressionError(f"Missing variable: {name}")
                active.add(key)
                value = bound.parameters[name].value
                if isinstance(value, BoundFormula):
                    result = evaluate_bound(value)
                elif isinstance(value, str):
                    c = Calculation(value)
                    result = c.result({n: resolve(n) for n in c.formula.variables})
                else:
                    result = Ultra.coerce(value)
                active.remove(key)
                return result

            return bound.calculation.result(
                {n: resolve(n) for n in bound.calculation.formula.variables}
            )

        return evaluate_bound(self)


def split_commands(source: str) -> list[str]:
    depth, start, commands = 0, 0, []
    for i, char in enumerate(source):
        if char == "(":
            depth += 1
        if char == ")":
            depth -= 1
        if char in ",;\n" and depth == 0:
            if source[start:i].strip():
                commands.append(source[start:i].strip())
            start = i + 1
    if source[start:].strip():
        commands.append(source[start:].strip())
    return commands


class FormulaSystem:
    def __init__(self, *commands: str) -> None:
        self.definitions: dict[str, str | Scalar] = {}
        self.root = "formula"
        flattened = [command for source in commands for command in split_commands(source)] or ["0"]
        for i, command in enumerate(flattened):
            pair = re.split(r":?=", command, maxsplit=1)
            if len(pair) == 1:
                if i:
                    raise ExpressionError("Expected a named definition")
                self.definitions[self.root] = command
            else:
                name, value = map(str.strip, pair)
                if i == 0:
                    self.root = name
                self.set(name, value)

    def set(self, name: str, value: str | Scalar) -> FormulaSystem:
        if not name.isidentifier() or name.startswith("_"):
            raise ExpressionError("Invalid name")
        self.definitions[name] = value
        return self

    def results(self, inputs: Mapping[str, Scalar] | None = None) -> dict[str, Ultra]:
        from .formula import evaluate_system

        definitions = {
            name: Calculation(value).formula if isinstance(value, str) else value
            for name, value in self.definitions.items()
            if name not in (inputs or {})
        }
        results = evaluate_system(definitions, inputs)
        return {**{n: Ultra.coerce(v) for n, v in (inputs or {}).items()}, **results}

    def result(self, inputs: Mapping[str, Scalar] | None = None) -> Ultra:
        return self.results(inputs)[self.root]
