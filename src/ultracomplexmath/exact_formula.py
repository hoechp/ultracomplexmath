"""Restricted exact expressions: decimal literals are parsed from their text."""

from __future__ import annotations

import ast
import math
import re
from collections.abc import Mapping
from dataclasses import dataclass, field
from fractions import Fraction
from typing import ClassVar

from .exact import QEPS, QI, QJ, ExactScalar, ExactUltra
from .formula import ExpressionError

_CONSTANTS = {"i": QI, "j": QJ, "eps": QEPS}
_CALLS = {
    "inverse",
    "sqrt",
    "conjugate",
    "conj_j",
    "conj_eps",
    "abs2",
    "real_part",
    "imag_part",
    "primal",
    "tangent",
    "floor",
    "ceil",
}
_OPS = (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow, ast.Mod, ast.FloorDiv)


@dataclass(frozen=True)
class ExactFormula:
    source: str
    _text: str = field(init=False, repr=False)
    _tree: ast.expr = field(init=False, repr=False, compare=False)
    variables: frozenset[str] = field(init=False)
    max_length: ClassVar[int] = 4096
    max_nodes: ClassVar[int] = 512
    max_depth: ClassVar[int] = 64
    max_bits: ClassVar[int] = 1_000_000

    def __post_init__(self) -> None:
        if not isinstance(self.source, str):
            raise TypeError("Expression must be text")
        if len(self.source) > self.max_length:
            raise ExpressionError("Expression is too long")
        translations: dict[str, str | int | None] = {"^": "**", "²": "**2", "³": "**3", "ε": "eps"}
        text = self.source.translate(str.maketrans(translations)).strip()
        try:
            tree = ast.parse(text, mode="eval").body
        except (SyntaxError, RecursionError) as error:
            raise ExpressionError(f"Invalid exact expression: {error}") from error
        if sum(1 for _ in ast.walk(tree)) > self.max_nodes:
            raise ExpressionError("Expression has too many nodes")
        names: set[str] = set()
        object.__setattr__(self, "_text", text)

        def validate(node: ast.expr, depth: int = 0) -> None:
            if depth > self.max_depth:
                raise ExpressionError("Expression is nested too deeply")
            if isinstance(node, ast.Constant):
                self._literal(node)
            elif isinstance(node, ast.Name) and not node.id.startswith("_"):
                if node.id in ("pi", "e"):
                    raise ExpressionError("Transcendental constants require numerical evaluation")
                if node.id not in _CONSTANTS:
                    names.add(node.id)
            elif isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
                validate(node.operand, depth + 1)
            elif isinstance(node, ast.BinOp) and isinstance(node.op, _OPS):
                validate(node.left, depth + 1)
                validate(node.right, depth + 1)
            elif (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id in _CALLS
            ):
                if len(node.args) != 1 or node.keywords:
                    raise ExpressionError("Exact functions take one positional argument")
                validate(node.args[0], depth + 1)
            else:
                raise ExpressionError("Unsupported exact expression")

        validate(tree)
        object.__setattr__(self, "_tree", tree)
        object.__setattr__(self, "variables", frozenset(names))

    def _literal(self, node: ast.Constant) -> Fraction:
        if isinstance(node.value, bool) or not isinstance(node.value, (int, float)):
            raise ExpressionError("Only real numeric literals are permitted")
        if isinstance(node.value, int):
            return Fraction(node.value)
        text = ast.get_source_segment(self._text, node)
        if text is None:
            raise ExpressionError("Missing numeric literal text")
        exponent = re.search(r"[eE]([+-]?[\d_]+)$", text)
        if exponent and abs(int(exponent.group(1))) > 10000:
            raise ExpressionError("Decimal exponent exceeds magnitude limit 10000")
        return Fraction(text.replace("_", ""))

    def evaluate(self, variables: Mapping[str, ExactScalar] | None = None) -> ExactUltra:
        supplied = dict(variables or {})
        if _CONSTANTS.keys() & supplied.keys():
            raise ExpressionError("Cannot override exact constants")
        if missing := self.variables - supplied.keys():
            raise ExpressionError(f"Missing variables: {', '.join(sorted(missing))}")
        values = _CONSTANTS | {key: ExactUltra.coerce(supplied[key]) for key in self.variables}

        def real(value: ExactUltra) -> Fraction:
            if any(value.coefficients[1:]):
                raise ExpressionError("This operation requires a real rational scalar")
            return value.real

        def bounded(value: ExactUltra) -> ExactUltra:
            if any(
                max(c.numerator.bit_length(), c.denominator.bit_length()) > self.max_bits
                for c in value
            ):
                raise ExpressionError("Exact coefficient exceeds bit-size limit")
            return value

        def visit(node: ast.expr) -> ExactUltra:
            if isinstance(node, ast.Constant):
                return bounded(ExactUltra(self._literal(node)))
            if isinstance(node, ast.Name):
                return bounded(values[node.id])
            if isinstance(node, ast.UnaryOp):
                v = visit(node.operand)
                return -v if isinstance(node.op, ast.USub) else v
            if isinstance(node, ast.BinOp):
                a, b = visit(node.left), visit(node.right)
                if isinstance(node.op, ast.Add):
                    result = a + b
                elif isinstance(node.op, ast.Sub):
                    result = a - b
                elif isinstance(node.op, ast.Mult):
                    result = a * b
                elif isinstance(node.op, ast.Div):
                    result = a / b
                elif isinstance(node.op, ast.Mod):
                    result = ExactUltra(real(a) % real(b))
                elif isinstance(node.op, ast.FloorDiv):
                    result = ExactUltra(real(a) // real(b))
                else:
                    power = real(b)
                    if abs(power) > 10000:
                        raise ExpressionError("Expression exponent exceeds magnitude limit 10000")
                    bits = max(max(c.numerator.bit_length(), c.denominator.bit_length()) for c in a)
                    if bits * abs(power) > self.max_bits:
                        raise ExpressionError("Power exceeds exact bit-size budget")
                    result = a**power
                return bounded(result)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                name, value = node.func.id, visit(node.args[0])
                if name in ("floor", "ceil"):
                    return ExactUltra(
                        math.floor(real(value)) if name == "floor" else math.ceil(real(value))
                    )
                if name in ("primal", "tangent"):
                    return value.primal if name == "primal" else value.tangent
                if name in ("conj_j", "conj_eps"):
                    return value.conjugate("j" if name == "conj_j" else "eps")
                if name == "inverse":
                    return bounded(value.inverse())
                if name == "sqrt":
                    return bounded(value.sqrt())
                if name == "abs2":
                    return bounded(value.abs2())
                if name == "real_part":
                    return value.real_part()
                if name == "imag_part":
                    return value.imag_part()
                return value.conjugate()
            raise AssertionError("Unvalidated exact AST")

        return visit(self._tree)

    __call__ = evaluate


def evaluate_exact(source: str, variables: Mapping[str, ExactScalar] | None = None) -> ExactUltra:
    return ExactFormula(source).evaluate(variables)
