# UltraField: values in space and time

[Documentation](README.md) · [API map](api.md) · [Field showcase](gallery/fields.md) · [Mathematical consequences](research/fields.md)

An `UltraField` is a rule assigning an ordinary, unchanged `Ultra` value to a real point:

$$F:M\times T\longrightarrow\mathcal A_{\mathbb R}.$$

Space and time are **additional inputs**. The eight coefficients and the multiplication laws of `Ultra` retain their existing meanings. In particular, `i`, `j` and `eps` never become spatial coordinate axes. This release provides numerical fields; it does not implicitly convert `ExactUltra` to floating point.

## A value with a location, without a field

```python
from ultracomplexmath import CoordinateSpace, LocatedUltra, Ultra, I, J, EPS

spacetime = CoordinateSpace()  # x, y, z; separate time t
point = spacetime.point(1, 2, 3, time=0.5)
value = LocatedUltra(2 + I + J / 3 + EPS * I, point)
assert (value * 2).point == point
assert (value * 2).value == value.value * 2
```

`LocatedUltra(value, point)` exists independently of fields. Arithmetic with another located value requires **exactly the same point and coordinate space**. Arithmetic with a scalar preserves the location. `.map(Ultra.exp)` transforms the value. `.relocated(new_point)` explicitly attaches the same value to another point; it does not calculate propagation or parallel transport.

`SpaceTimePoint` and `CoordinateSpace` are immutable. Coordinate names identify a chart, not units, a metric or a physical reference frame. Spaces with identical names and axis roles compare equal. Distinct physical frames therefore need an explicit `CoordinateMap` (and, when useful, different coordinate names); matching names alone do not prove physical compatibility.

## Dimensions and time

```python
plane = CoordinateSpace.cartesian(2, time_axis=None)  # x, y
clock = CoordinateSpace.cartesian(0)  # t only
single_point = CoordinateSpace.cartesian(0, time_axis=None)
many_axes = CoordinateSpace.cartesian(5)  # x0 ... x4, t
parameters = CoordinateSpace(("u", "v"), time_axis="clock")
assert single_point.point().coordinates == {}
```

There can be zero through n spatial axes and zero or one time axis. Up to three Cartesian axes use `x, y, z`; higher dimensions use `x0, x1, ...`. Names must be distinct identifiers. Algebra constants, names beginning with `_`, Python keywords and the array dimension name `coefficient` are reserved. Coordinates must be finite real `int`/`float` values, excluding booleans.

`space.point(*position, time=...)` defaults time to zero when time exists. In contrast, `space.from_coordinates({...})` requires every coordinate explicitly. Time cannot be supplied to a space without a time axis.

## Define a field by a finite rule

```python
from ultracomplexmath import UltraField

wave = UltraField.from_formula(
    "exp(i*(2*x-speed*2*t))+j*y+eps*i*j*z",
    parameters={"speed": 1.5},
)
sample = wave.at(0.2, 0.3, 0.4, time=0.5)  # LocatedUltra
assert wave(sample.point) == sample.value
assert wave.evaluate(x=0.2, y=0.3, z=0.4, t=0.5) == sample.value

# A Python rule can use other real geometry or existing numerical libraries.
radial = UltraField(lambda p: Ultra(-sum(x * x for x in p.position)).exp())
assert radial.at(0, 0, 0).value == Ultra(1)
```

The formula path uses the existing restricted `Formula` parser. Parameters are copied at construction; they cannot override coordinates or algebra constants. Unbound variables are rejected. Alternatively, pass a pure Python callable receiving a `SpaceTimePoint` and returning `Ultra`, `int`, `float` or `complex`.

Fields support lazy pointwise `+`, `-`, `*`, `/`, scalar powers, `.exp()` and `.map(function)`. The operands must use the same coordinate space. Division retains the scalar algebra's zero-divisor restrictions. No grid is created until explicitly requested. A formula can still have singularities; a rule is only evaluable where its operations are defined.

## Slices, views and samples

```python
view = wave.slice(z=0.4, t=0.5)
sample = view.at(0.2, 0.3)
assert sample.point.coordinates == {"x": 0.2, "y": 0.3, "z": 0.4, "t": 0.5}

grid = view.sample({"x": [-1, 0, 1], "y": [-2, 2]})
assert grid.shape == (3, 2)
assert grid.at_index(2, 1) == wave.at(1, 2, 0.4, time=0.5)
assert view.slice(x=0.2, y=0.3).sample({}).shape == ()
```

A `FieldView` fixes coordinates while keeping full original locations in `.at()`, `.sample()` and `.iter_samples()`. Chained slices cannot overwrite coordinates already fixed. `.as_field()` explicitly exposes a rule on the reduced coordinate space, useful for further arithmetic or differentiation.

`sample` requires every coordinate to be either sampled or fixed, exactly once. Axis order follows the supplied mapping; the last axis varies fastest, as in NumPy's `indexing="ij"`. Empty sample axes are rejected. A fully fixed view has shape `()` and contains one value. All eight coefficients remain in every sample.

`FieldGrid` is a snapshot, not an interpolant. The default budget is one million points; `.iter_samples()` streams the Cartesian product when materializing it would be inappropriate. Rules still define the field between all sample points.

Optional interoperability:

```sh
python -m pip install -e '.[arrays]'
```

`grid.to_numpy()` returns a copy with shape `(*grid.shape, 8)` and basis order `BASIS`. `grid.to_xarray()` returns a `DataArray` with named coordinate dimensions, a final `coefficient` dimension and fixed coordinates such as `z` and `t` retained as scalar coordinates. For example, `grid.to_xarray().sel(coefficient="eps*i*j")` selects one explicitly named component. These are real coefficient arrays; ordinary array multiplication is **not** ultracomplex multiplication. Use field arithmetic before sampling for algebraic operations.

The core imports neither NumPy nor xarray. Their official [indexing](https://numpy.org/doc/stable/reference/generated/numpy.meshgrid.html) and [coordinate conventions](https://docs.xarray.dev/en/stable/user-guide/data-structures.html) are used only in optional adapters.

## Differentiate coordinates without consuming epsilon

```python
f = UltraField.from_formula("(1+eps*i)*(x**2+y**2+z**2)")
p = f.space.point(1, 2, 3)
assert f.partial("x")(p).isclose(2 * (1 + EPS * I), abs_tol=1e-8)
assert f.laplacian()(p).isclose(6 * (1 + EPS * I), abs_tol=1e-7)
gradient = f.gradient()  # three UltraFields, one per real spatial axis
```

`.partial(axis, order=1 or 2, step=...)` differentiates a real coordinate. It uses a centered fourth-order finite-difference stencil at offsets up to `2*step`. Each coefficient is accumulated separately. This includes the four existing epsilon coefficients: epsilon is never reused as an independent coordinate seed. For smooth functions the truncation error is fourth order, but floating-point cancellation, branch cuts and domain boundaries still matter. There is no automatic error estimate, boundary extension or adaptive step selection. Reducing the step indefinitely makes accuracy worse. Unresolved shifts and invalid stencil scales fail explicitly.

An optional `partials={"x": callable, ...}` mapping supplies analytic first partial derivatives. These are used directly by `.partial("x")`, spatial gradients and surface calculus. Second partials still use the numerical second-derivative stencil; arithmetic, maps and slices do not propagate analytic derivative metadata automatically.

`.gradient()` returns spatial partials and `.laplacian()` their second-derivative sum. They assume Euclidean Cartesian coordinates, regardless of axis names. In zero spatial dimensions these return `()` and the zero field. `.wave_operator(speed=c)` constructs

$$\Box_cF=c^{-2}\partial_t^2F-\sum_a\partial_{x_a}^2F.$$

The caller chooses the positive real speed and compatible units. This is one flat-space model operator; adding a time coordinate alone does not assert a spacetime metric or an equation of motion.

## Coordinate maps and surfaces

`CoordinateMap(source, target, rule)` maps real points and validates both domains. `.pullback(field)` implements composition `field(map(point))`. `.locate(located_value)` changes the point while preserving the value. A pullback is also how an ambient field is restricted to a surface.

```python
from ultracomplexmath import torus, mobius_strip

ring = torus(major_radius=2, minor_radius=0.65)
ambient = UltraField.from_formula("x+i*y+eps*z")
on_ring = ring.pullback(ambient)
local = on_ring.at(0.3, 0.7, time=1)
embedded = ring.locate(local)
assert embedded.value == ambient(embedded.point)

mode = UltraField.from_formula("exp(2*i*u)*(1+eps*i*j)", space=ring.space)
p = ring.space.point(0.3, 0.7)
tangent_gradient = ring.gradient(mode, p)  # ambient components, each Ultra
curved_laplacian = ring.laplacian(mode)  # UltraField on (u, v, t)
area = ring.integrate(UltraField.constant(1, ring.space), shape=(16, 16))
assert area.real > 0
```

`ParametricSurface` accepts a static embedding, its analytic Jacobian, two integration bounds, and optional seams. Built-ins provide a regular ring torus and a Möbius strip in three-dimensional Euclidean space. The parameter domain has two spatial coordinates plus optional time. Generic embeddings can have more ambient dimensions.

Surface gradients, area quadrature and the Laplace–Beltrami operator use the real induced metric `g = J.T @ J`. They therefore account for actual lengths, angles and area, rather than treating parameters as Cartesian distances. Quadrature uses midpoint samples and is approximate. No global normal orientation is required. Singular charts, excessive conditioning (scaled determinant at or below `1e-14 * trace²`) and metrics outside the float range raise errors.

## The Möbius seam is part of the mathematics

```python
strip = mobius_strip()
valid = UltraField.from_formula("exp(i*(2*u-t)+j*v*cos(u/2))*(1+eps*v*sin(u/2))", space=strip.space)
assert strip.check_seams(valid, samples=9, times=(0, 1)).within(atol=1e-8)
invalid = UltraField.from_formula("j*v", space=strip.space)
assert not strip.check_seams(invalid).within()
```

For the torus, both parameters are periodic. On the Möbius strip, `(u+2*pi, v)` and `(u, -v)` represent the same point. An ordinary scalar field must have equal values there. The transverse partial derivative changes sign, while the resulting ambient tangent gradient agrees. No automatic conjugation or sign change is applied to `Ultra` itself.

`check_seams` compares values and, by default, first derivatives at finite samples. It reports absolute errors **per coefficient**. Passing is a diagnostic, not a proof of global smoothness. A formula must satisfy the transition law for all points. The implementation neither wraps an incompatible formula silently nor treats a displayed surface as evidence of compatibility. Stencils near boundaries require a smooth extension of the rule; the built-in formulas have one on the parameter cover.

This release does not provide an arbitrary manifold atlas, evolving surfaces, general curved spacetime metrics, geodesic transport, spinor bundles, mesh-based PDE solvers or boundary-condition solvers. The current field, coordinate-map and surface contracts leave those extensions possible without changing the eight-dimensional algebra.
