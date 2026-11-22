"""Real coordinate domains carrying unchanged eight-component Ultra values.

Fields are rules, not grids. Spatial differentiation uses external real
coordinates and never consumes the algebra's existing epsilon direction.
"""

from __future__ import annotations

import importlib
import keyword
import math
import operator
from collections.abc import Callable, Iterator, Mapping, Sequence
from dataclasses import dataclass, field
from itertools import product
from types import MappingProxyType
from typing import Any

from .core import BASIS, Scalar, Ultra
from .formula import Formula

_RESERVED = frozenset(("i", "j", "eps", "pi", "e", "coefficient"))
type FieldRule = Callable[[SpaceTimePoint], Scalar]


def _real(value: float, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{label} must be a real int or float")
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"{label} must be finite")
    return result


def _name(name: str) -> None:
    if (
        not isinstance(name, str)
        or not name.isidentifier()
        or name.startswith("_")
        or keyword.iskeyword(name)
        or name in _RESERVED
    ):
        raise ValueError(f"Invalid or reserved coordinate/parameter name: {name!r}")


def _weighted_sum(terms: Sequence[tuple[float, Ultra]]) -> Ultra:
    """Accumulate each coefficient separately, including very small tangents."""
    return Ultra(*(math.fsum(w * v.coefficients[k] for w, v in terms) for k in range(8)))


@dataclass(frozen=True, slots=True)
class CoordinateSpace:
    """Named real spatial axes and an optional, separate time coordinate.

    Names identify coordinates, not a metric, units or a physical frame.
    Equality is structural; comparisons of points use exact coordinates.
    """

    spatial_axes: tuple[str, ...] = ("x", "y", "z")
    time_axis: str | None = "t"

    def __post_init__(self) -> None:
        object.__setattr__(self, "spatial_axes", tuple(self.spatial_axes))
        for name in self.coordinate_names:
            _name(name)
        if len(set(self.coordinate_names)) != len(self.coordinate_names):
            raise ValueError("Coordinate names must be distinct")

    @classmethod
    def cartesian(cls, dimensions: int = 3, *, time_axis: str | None = "t") -> CoordinateSpace:
        if type(dimensions) is not int or dimensions < 0:
            raise ValueError("Spatial dimension must be a nonnegative integer")
        axes = (
            ("x", "y", "z")[:dimensions]
            if dimensions <= 3
            else tuple(f"x{k}" for k in range(dimensions))
        )
        return cls(axes, time_axis)

    @property
    def coordinate_names(self) -> tuple[str, ...]:
        return self.spatial_axes + (() if self.time_axis is None else (self.time_axis,))

    def point(self, *position: float, time: float | None = None) -> SpaceTimePoint:
        if time is None and self.time_axis is not None:
            time = 0.0
        return SpaceTimePoint(self, tuple(position), time)

    def from_coordinates(self, coordinates: Mapping[str, float]) -> SpaceTimePoint:
        if set(coordinates) != set(self.coordinate_names):
            raise ValueError(f"Expected exactly these coordinates: {self.coordinate_names}")
        return self.point(
            *(coordinates[name] for name in self.spatial_axes),
            time=None if self.time_axis is None else coordinates[self.time_axis],
        )


@dataclass(frozen=True, slots=True)
class SpaceTimePoint:
    space: CoordinateSpace
    position: tuple[float, ...]
    time: float | None = None

    def __post_init__(self) -> None:
        if len(self.position) != len(self.space.spatial_axes):
            raise ValueError("Position dimension does not match the coordinate space")
        object.__setattr__(self, "position", tuple(_real(v, "Position") for v in self.position))
        if self.space.time_axis is None:
            if self.time is not None:
                raise ValueError("This coordinate space has no time axis")
        elif self.time is None:
            raise ValueError("A point in a space with time requires a time coordinate")
        else:
            object.__setattr__(self, "time", _real(self.time, "Time"))

    @property
    def coordinates(self) -> dict[str, float]:
        result = dict(zip(self.space.spatial_axes, self.position, strict=True))
        if self.space.time_axis is not None:
            assert self.time is not None
            result[self.space.time_axis] = self.time
        return result

    def __getitem__(self, axis: str) -> float:
        return self.coordinates[axis]

    def replace(self, **coordinates: float) -> SpaceTimePoint:
        return self.space.from_coordinates(self.coordinates | coordinates)


@dataclass(frozen=True, slots=True, init=False)
class LocatedUltra:
    """A value at one point, usable without any field.

    Two located values can combine only at exactly the same point. Relocation
    is explicit and retains the value; it is not physical parallel transport.
    """

    value: Ultra
    point: SpaceTimePoint

    def __init__(self, value: Scalar, point: SpaceTimePoint) -> None:
        object.__setattr__(self, "value", Ultra.coerce(value))
        object.__setattr__(self, "point", point)

    def _value(self, other: LocatedUltra | Scalar) -> Ultra:
        if isinstance(other, LocatedUltra):
            if self.point != other.point:
                raise ValueError("Located arithmetic requires exactly the same point")
            return other.value
        return Ultra.coerce(other)

    def map(self, rule: Callable[[Ultra], Scalar]) -> LocatedUltra:
        return LocatedUltra(rule(self.value), self.point)

    def relocated(self, point: SpaceTimePoint) -> LocatedUltra:
        return LocatedUltra(self.value, point)

    def __add__(self, other: LocatedUltra | Scalar) -> LocatedUltra:
        return LocatedUltra(self.value + self._value(other), self.point)

    __radd__ = __add__

    def __neg__(self) -> LocatedUltra:
        return LocatedUltra(-self.value, self.point)

    def __sub__(self, other: LocatedUltra | Scalar) -> LocatedUltra:
        return LocatedUltra(self.value - self._value(other), self.point)

    def __rsub__(self, other: Scalar) -> LocatedUltra:
        return LocatedUltra(Ultra.coerce(other) - self.value, self.point)

    def __mul__(self, other: LocatedUltra | Scalar) -> LocatedUltra:
        return LocatedUltra(self.value * self._value(other), self.point)

    __rmul__ = __mul__

    def __truediv__(self, other: LocatedUltra | Scalar) -> LocatedUltra:
        return LocatedUltra(self.value / self._value(other), self.point)

    def __rtruediv__(self, other: Scalar) -> LocatedUltra:
        return LocatedUltra(Ultra.coerce(other) / self.value, self.point)

    def __pow__(self, power: Scalar) -> LocatedUltra:
        return LocatedUltra(self.value**power, self.point)


@dataclass(frozen=True, slots=True)
class UltraField:
    """A callable rule M -> Ultra; the default domain has three axes and time.

    ``partials`` optionally supplies analytic first partial derivatives by
    coordinate name. Other derivatives use explicit real finite differences.
    Rules and supplied derivatives should be pure functions of their point.
    """

    rule: FieldRule
    space: CoordinateSpace = field(default_factory=CoordinateSpace)
    name: str = "F"
    partials: Mapping[str, FieldRule] = field(default_factory=dict, repr=False, compare=False)

    def __post_init__(self) -> None:
        if not callable(self.rule):
            raise TypeError("A field requires a callable rule")
        if set(self.partials) - set(self.space.coordinate_names):
            raise ValueError("Unknown derivative coordinate")
        if any(not callable(rule) for rule in self.partials.values()):
            raise TypeError("Analytic partial derivatives must be callable")
        object.__setattr__(self, "partials", MappingProxyType(dict(self.partials)))

    @classmethod
    def from_formula(
        cls,
        source: str,
        *,
        space: CoordinateSpace | None = None,
        parameters: Mapping[str, Scalar] | None = None,
        name: str = "F",
    ) -> UltraField:
        domain = CoordinateSpace() if space is None else space
        expression = Formula(source)
        bound = dict(parameters or {})
        for key in bound:
            _name(key)
        if set(bound) & set(domain.coordinate_names):
            raise ValueError("Parameters cannot override coordinates")
        bound = {key: Ultra.coerce(value) for key, value in bound.items()}
        if missing := expression.variables - set(domain.coordinate_names) - set(bound):
            raise ValueError(f"Unbound field variables: {', '.join(sorted(missing))}")
        return cls(lambda p: expression.evaluate(bound | p.coordinates), domain, name)

    @classmethod
    def constant(cls, value: Scalar, space: CoordinateSpace | None = None) -> UltraField:
        scalar = Ultra.coerce(value)
        return cls(lambda p: scalar, CoordinateSpace() if space is None else space)

    def __call__(self, point: SpaceTimePoint) -> Ultra:
        if point.space != self.space:
            raise ValueError("Point and field use different coordinate spaces")
        return Ultra.coerce(self.rule(point))

    def evaluate(self, **coordinates: float) -> Ultra:
        """Evaluate at a complete, named coordinate assignment (including time)."""
        return self(self.space.from_coordinates(coordinates))

    def at(self, *position: float, time: float | None = None) -> LocatedUltra:
        point = self.space.point(*position, time=time)
        return LocatedUltra(self(point), point)

    def map(self, rule: Callable[[Ultra], Scalar], *, name: str | None = None) -> UltraField:
        return UltraField(lambda p: rule(self(p)), self.space, name or self.name)

    def _binary(
        self, other: UltraField | Scalar, op: Callable[[Ultra, Ultra], Ultra]
    ) -> UltraField:
        if isinstance(other, UltraField):
            if self.space != other.space:
                raise ValueError("Field arithmetic requires the same coordinate space")
            return UltraField(lambda p: op(self(p), other(p)), self.space)
        scalar = Ultra.coerce(other)
        return self.map(lambda v: op(v, scalar))

    def __add__(self, other: UltraField | Scalar) -> UltraField:
        return self._binary(other, operator.add)

    __radd__ = __add__

    def __neg__(self) -> UltraField:
        return self.map(operator.neg)

    def __sub__(self, other: UltraField | Scalar) -> UltraField:
        return self._binary(other, operator.sub)

    def __rsub__(self, other: Scalar) -> UltraField:
        scalar = Ultra.coerce(other)
        return self.map(lambda v: scalar - v)

    def __mul__(self, other: UltraField | Scalar) -> UltraField:
        return self._binary(other, operator.mul)

    __rmul__ = __mul__

    def __truediv__(self, other: UltraField | Scalar) -> UltraField:
        return self._binary(other, operator.truediv)

    def __rtruediv__(self, other: Scalar) -> UltraField:
        scalar = Ultra.coerce(other)
        return self.map(lambda v: scalar / v)

    def __pow__(self, power: Scalar) -> UltraField:
        return self.map(lambda v: v**power)

    def exp(self) -> UltraField:
        return self.map(Ultra.exp)

    def partial(self, axis: str, *, order: int = 1, step: float = 1e-3) -> UltraField:
        """Analytic first partial if supplied, otherwise a fourth-order stencil.

        Stencils require values at x +/- h and x +/- 2h. No boundary extension
        or error estimate is assumed. A smaller step is not always more accurate.
        """
        if axis not in self.space.coordinate_names:
            raise ValueError(f"Unknown coordinate: {axis}")
        if type(order) is not int or order not in (1, 2):
            raise ValueError("Derivative order must be 1 or 2")
        h = _real(step, "Derivative step")
        scale = 12 * h if order == 1 else 12 * h * h
        if h <= 0 or not math.isfinite(scale) or scale == 0:
            raise ValueError("Derivative step must have a finite positive stencil scale")
        if order == 1 and axis in self.partials:
            return UltraField(self.partials[axis], self.space, f"d{self.name}/d{axis}")
        offsets = (-2, -1, 1, 2) if order == 1 else (-2, -1, 0, 1, 2)
        weights = (1, -8, 8, -1) if order == 1 else (-1, 16, -30, 16, -1)

        def derivative(p: SpaceTimePoint) -> Ultra:
            coordinates = tuple(p[axis] + k * h for k in offsets)
            if len(set(coordinates + (p[axis],))) != 5:
                raise ValueError("Derivative step is not resolved at this coordinate")
            values = [self(p.replace(**{axis: x})) for x in coordinates]
            # Subtract the central value before summing to reduce cancellation
            # of constant terms. Never divide through Ultra's channel conversion.
            center = self(p)
            return Ultra(
                *(
                    math.fsum(
                        w * (v.coefficients[k] - center.coefficients[k])
                        for w, v in zip(weights, values, strict=True)
                    )
                    / scale
                    for k in range(8)
                )
            )

        return UltraField(derivative, self.space, f"d{order}{self.name}/d{axis}{order}")

    def gradient(self, *, step: float = 1e-3) -> tuple[UltraField, ...]:
        """Spatial partials in axis order; assumes Cartesian Euclidean axes."""
        return tuple(self.partial(axis, step=step) for axis in self.space.spatial_axes)

    def laplacian(self, *, step: float = 1e-3) -> UltraField:
        derivatives = [self.partial(axis, order=2, step=step) for axis in self.space.spatial_axes]
        return UltraField(lambda p: _weighted_sum([(1, d(p)) for d in derivatives]), self.space)

    def wave_operator(self, *, speed: float = 1.0, step: float = 1e-3) -> UltraField:
        """Flat-space (1/c^2) d_t^2 F - spatial Laplacian; units are caller-defined."""
        c = _real(speed, "Wave speed")
        if c <= 0 or not math.isfinite(c * c) or c * c == 0:
            raise ValueError("Wave speed must have a finite positive square")
        if self.space.time_axis is None:
            raise ValueError("The wave operator requires a time axis")
        temporal = self.partial(self.space.time_axis, order=2, step=step)
        spatial = self.laplacian(step=step)
        return UltraField(
            lambda p: _weighted_sum([(1 / (c * c), temporal(p)), (-1, spatial(p))]), self.space
        )

    def slice(self, **fixed: float) -> FieldView:
        return FieldView(self, fixed)

    def iter_samples(
        self, axes: Mapping[str, Sequence[float]], *, fixed: Mapping[str, float] | None = None
    ) -> Iterator[LocatedUltra]:
        """Stream a Cartesian product in supplied axis order, last axis fastest."""
        names, coordinates, constants = _sampling(self.space, axes, fixed or {})
        for values in product(*coordinates):
            point = self.space.from_coordinates(constants | dict(zip(names, values, strict=True)))
            yield LocatedUltra(self(point), point)

    def sample(
        self,
        axes: Mapping[str, Sequence[float]],
        *,
        fixed: Mapping[str, float] | None = None,
        max_points: int = 1_000_000,
    ) -> FieldGrid:
        names, coordinates, constants = _sampling(self.space, axes, fixed or {})
        if type(max_points) is not int or max_points < 1:
            raise ValueError("max_points must be a positive integer")
        if math.prod(map(len, coordinates)) > max_points:
            raise ValueError("Sampling exceeds max_points; use fewer points or iter_samples")
        copied = dict(zip(names, coordinates, strict=True))
        values = tuple(sample.value for sample in self.iter_samples(copied, fixed=constants))
        return FieldGrid(self.space, tuple(copied.items()), constants, values)


def _sampling(
    space: CoordinateSpace,
    axes: Mapping[str, Sequence[float]],
    fixed: Mapping[str, float],
) -> tuple[tuple[str, ...], tuple[tuple[float, ...], ...], dict[str, float]]:
    if set(axes) & set(fixed) or set(axes) | set(fixed) != set(space.coordinate_names):
        raise ValueError("Every coordinate must be sampled or fixed, exactly once")
    coordinates = tuple(tuple(_real(v, name) for v in values) for name, values in axes.items())
    if any(not values for values in coordinates):
        raise ValueError("Sample axes must be nonempty")
    return tuple(axes), coordinates, {name: _real(value, name) for name, value in fixed.items()}


@dataclass(frozen=True, slots=True)
class FieldView:
    """A restriction retaining full source coordinates in every located sample."""

    source: UltraField
    fixed: Mapping[str, float]

    def __post_init__(self) -> None:
        if set(self.fixed) - set(self.source.space.coordinate_names):
            raise ValueError("Unknown fixed coordinate")
        object.__setattr__(
            self,
            "fixed",
            MappingProxyType({name: _real(value, name) for name, value in self.fixed.items()}),
        )

    @property
    def space(self) -> CoordinateSpace:
        original = self.source.space
        return CoordinateSpace(
            tuple(axis for axis in original.spatial_axes if axis not in self.fixed),
            None if original.time_axis in self.fixed else original.time_axis,
        )

    def __call__(self, point: SpaceTimePoint) -> Ultra:
        if point.space != self.space:
            raise ValueError("Point does not belong to the view's coordinate space")
        return self.source.evaluate(**(dict(self.fixed) | point.coordinates))

    def evaluate(self, **coordinates: float) -> Ultra:
        return self(self.space.from_coordinates(coordinates))

    def at(self, *position: float, time: float | None = None) -> LocatedUltra:
        point = self.space.point(*position, time=time)
        original = self.source.space.from_coordinates(dict(self.fixed) | point.coordinates)
        return LocatedUltra(self.source(original), original)

    def as_field(self) -> UltraField:
        """A rule on the reduced coordinate space, for further field arithmetic."""
        return UltraField(self, self.space, self.source.name)

    def slice(self, **fixed: float) -> FieldView:
        if set(fixed) & set(self.fixed):
            raise ValueError("A view cannot override coordinates already fixed")
        return FieldView(self.source, dict(self.fixed) | fixed)

    def sample(
        self, axes: Mapping[str, Sequence[float]], *, max_points: int = 1_000_000
    ) -> FieldGrid:
        return self.source.sample(axes, fixed=self.fixed, max_points=max_points)

    def iter_samples(self, axes: Mapping[str, Sequence[float]]) -> Iterator[LocatedUltra]:
        return self.source.iter_samples(axes, fixed=self.fixed)


@dataclass(frozen=True, slots=True)
class FieldGrid:
    """Finite evaluation result, with all eight coefficients and full coordinates.

    This is a snapshot, not an interpolant or a new definition of the field.
    Optional array adapters use ij indexing and a final coefficient axis.
    """

    space: CoordinateSpace
    axes: tuple[tuple[str, tuple[float, ...]], ...]
    fixed: Mapping[str, float]
    values: tuple[Ultra, ...]

    def __post_init__(self) -> None:
        if len(dict(self.axes)) != len(self.axes):
            raise ValueError("Duplicate sample axes")
        names, coordinates, constants = _sampling(self.space, dict(self.axes), self.fixed)
        object.__setattr__(self, "axes", tuple(zip(names, coordinates, strict=True)))
        object.__setattr__(self, "fixed", MappingProxyType(constants))
        object.__setattr__(self, "values", tuple(Ultra.coerce(v) for v in self.values))
        if len(self.values) != math.prod(self.shape):
            raise ValueError("Sample count does not match grid shape")

    @property
    def shape(self) -> tuple[int, ...]:
        return tuple(len(values) for _, values in self.axes)

    def at_index(self, *indices: int) -> LocatedUltra:
        if len(indices) != len(self.axes):
            raise IndexError("One index per sampled axis is required")
        flat = 0
        coordinates = dict(self.fixed)
        for index, (name, values) in zip(indices, self.axes, strict=True):
            if type(index) is not int or not 0 <= index < len(values):
                raise IndexError("Sample index out of bounds")
            flat = flat * len(values) + index
            coordinates[name] = values[index]
        return LocatedUltra(self.values[flat], self.space.from_coordinates(coordinates))

    def to_numpy(self) -> Any:
        """Copy to float64 array of shape ``(*shape, 8)``; requires NumPy."""
        np = importlib.import_module("numpy")
        return np.array([v.coefficients for v in self.values], dtype=float).reshape(*self.shape, 8)

    def to_xarray(self) -> Any:
        """Copy to a named DataArray; requires the optional 'arrays' extra."""
        xr = importlib.import_module("xarray")
        coordinates: dict[str, Any] = {name: list(values) for name, values in self.axes}
        coordinates.update(self.fixed)
        coordinates["coefficient"] = list(BASIS)
        return xr.DataArray(
            self.to_numpy(),
            dims=[name for name, _ in self.axes] + ["coefficient"],
            coords=coordinates,
            name="ultra",
        )


@dataclass(frozen=True, slots=True)
class CoordinateMap:
    """An explicit real coordinate map; pullback is composition F(map(p))."""

    source: CoordinateSpace
    target: CoordinateSpace
    rule: Callable[[SpaceTimePoint], SpaceTimePoint]

    def __call__(self, point: SpaceTimePoint) -> SpaceTimePoint:
        if point.space != self.source:
            raise ValueError("Coordinate map received a point in the wrong space")
        result = self.rule(point)
        if result.space != self.target:
            raise ValueError("Coordinate map returned a point in the wrong space")
        return result

    def pullback(self, field: UltraField) -> UltraField:
        if field.space != self.target:
            raise ValueError("Field must live on the map's target")
        return UltraField(lambda p: field(self(p)), self.source, field.name)

    def locate(self, value: LocatedUltra) -> LocatedUltra:
        return value.relocated(self(value.point))
