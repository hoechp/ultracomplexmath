"""Sampling for the former applets, independent of any graphical backend."""

from __future__ import annotations

import colorsys
import math
from collections.abc import Callable, Mapping
from dataclasses import dataclass

from .core import Scalar, Ultra
from .expressions import Calculation, FormulaSystem
from .formula import ExpressionError, evaluate_system
from .numbers import Binary, Complex, Dual, Hypercomplex

ALGEBRAS: dict[str, type[Hypercomplex]] = {"complex": Complex, "split": Binary, "dual": Dual}
type RGB = tuple[float, float, float]


def linspace(start: float, stop: float, count: int) -> tuple[float, ...]:
    if not all(map(math.isfinite, (start, stop))) or start >= stop or not 2 <= count <= 10000:
        raise ValueError("Expected finite increasing bounds and 2..10000 samples")
    return tuple(start + (stop - start) * i / (count - 1) for i in range(count))


def _evaluator(source: str, parameters: Mapping[str, Scalar] | None) -> Callable[[Ultra], Ultra]:
    system = FormulaSystem(source)
    definitions = {
        name: Calculation(value).formula if isinstance(value, str) else value
        for name, value in system.definitions.items()
    }
    supplied: dict[str, Scalar] = dict(parameters or {})
    available = set(definitions) | set(supplied) | {"x"}
    for definition in definitions.values():
        if hasattr(definition, "variables") and definition.variables - available:
            raise ExpressionError(f"Missing variables: {sorted(definition.variables - available)}")

    def evaluate(x: Ultra) -> Ultra:
        inputs = {**supplied, "x": x}
        selected = {key: value for key, value in definitions.items() if key not in inputs}
        if system.root in inputs:
            return Ultra.coerce(inputs[system.root])
        return evaluate_system(selected, inputs)[system.root]

    # Resolve dependency errors before masking numerical singularities in a plot.
    try:
        evaluate(Ultra(0.37))
    except ExpressionError:
        raise
    except (ArithmeticError, ValueError):
        pass
    return evaluate


@dataclass(frozen=True)
class Curve:
    parameters: tuple[float, ...]
    values: tuple[Ultra | None, ...]

    def component(self, index: int) -> tuple[float, ...]:
        Ultra.unit(index)
        return tuple(v.coefficients[index] if v is not None else math.nan for v in self.values)

    @property
    def undefined_count(self) -> int:
        return self.values.count(None)


def sample_curve(
    source: str,
    start: float = -math.pi,
    stop: float = math.pi,
    count: int = 401,
    *,
    parameters: Mapping[str, Scalar] | None = None,
) -> Curve:
    xs, evaluate = linspace(start, stop, count), _evaluator(source, parameters)
    values: list[Ultra | None] = []
    for x in xs:
        try:
            values.append(evaluate(Ultra(x)))
        except ExpressionError:
            raise
        except (ArithmeticError, ValueError):
            values.append(None)
    return Curve(xs, tuple(values))


@dataclass(frozen=True)
class DomainGrid:
    xs: tuple[float, ...]
    ys: tuple[float, ...]
    values: tuple[tuple[Hypercomplex | None, ...], ...]
    colors: tuple[tuple[RGB, ...], ...]


def domain_color_grid(
    source: str = "x",
    *,
    kind: type[Hypercomplex] = Complex,
    bounds: tuple[float, float, float, float] = (-2, 2, -2, 2),
    resolution: int = 65,
    parameters: Mapping[str, Scalar] | None = None,
    legacy_colors: bool = False,
    input_basis: tuple[Ultra, Ultra] | None = None,
    components: tuple[int | None, int | None] | None = None,
    contours: tuple[int, float, float] | None = None,
) -> DomainGrid:
    """Color a plane; optionally project any two Ultra coefficients (None = norm).

    ``contours=(spokes, rings_per_unit, phase)`` reproduces the two original
    domain grid overlays with phase 0 or 0.5. Numerical failures are gray.
    """
    if not 2 <= resolution <= 256:
        raise ValueError("Domain resolution must be in 2..256")
    xs, ys = linspace(*bounds[:2], resolution), linspace(*bounds[2:], resolution)
    evaluate = _evaluator(source, parameters)
    if components is not None:
        for index in components:
            if index is not None:
                Ultra.unit(index)
    if contours is not None:
        spokes, rings, phase = contours
        if spokes < 1 or rings <= 0 or not all(map(math.isfinite, (rings, phase))):
            raise ValueError("Contours require positive spokes and rings")
    rows, colors = [], []
    for y in ys:
        values: list[Hypercomplex | None] = []
        pixels: list[RGB] = []
        for x in xs:
            try:
                argument = (
                    kind(x, y).to_ultra()
                    if input_basis is None
                    else input_basis[0] * x + input_basis[1] * y
                )
                result = evaluate(argument)
                value = (
                    kind.from_ultra(result)
                    if components is None
                    else Complex(
                        *(abs(result) if i is None else result.coefficients[i] for i in components)
                    )
                )
                values.append(value)
                if legacy_colors:
                    r, g, b = value.color()
                    pixels.append((r / 255, g / 255, b / 255))
                else:
                    magnitude = abs(value)
                    shade = 0.25 + 0.7 * magnitude / (1 + magnitude)
                    pixels.append(colorsys.hsv_to_rgb((value.angle / math.tau) % 1, 0.8, shade))
                if contours is not None:
                    angle_period, radius_period = math.tau / spokes, 1 / rings
                    if abs((value.angle + math.tau) % angle_period - phase * angle_period) < 0.01:
                        pixels[-1] = (0, 0, 0)
                    elif abs(abs(value) % radius_period - phase * radius_period) < 0.01:
                        pixels[-1] = (1, 1, 1)
            except ExpressionError:
                raise
            except (ArithmeticError, ValueError):
                values.append(None)
                pixels.append((0.85, 0.85, 0.85))
        rows.append(tuple(values))
        colors.append(tuple(pixels))
    return DomainGrid(xs, ys, tuple(rows), tuple(colors))
