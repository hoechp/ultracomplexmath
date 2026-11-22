"""Independent coordinate, indexing, calculus and value-preservation checks."""

import math

import pytest

from ultracomplexmath import (
    BASIS,
    EPS,
    CoordinateMap,
    CoordinateSpace,
    FieldGrid,
    I,
    J,
    LocatedUltra,
    SpaceTimePoint,
    Ultra,
    UltraField,
)


def assert_coefficients(actual, expected, *, rel=1e-8, abs=1e-9):
    for a, b in zip(actual, expected, strict=True):
        assert a == pytest.approx(b, rel=rel, abs=abs)


@pytest.mark.parametrize("dimension", [0, 1, 2, 3, 4, 7])
@pytest.mark.parametrize("time_axis", [None, "t", "clock"])
def test_dimensions_and_time_are_external(dimension, time_axis):
    space = CoordinateSpace.cartesian(dimension, time_axis=time_axis)
    p = space.point(*range(dimension), time=None if time_axis is None else 2.5)
    assert len(p.position) == dimension
    assert space.from_coordinates(p.coordinates) == p
    value = Ultra(1, 2, 3, 4, 5, 6, 7, 8)
    located = LocatedUltra(value, p)
    field = UltraField.constant(value, space)
    assert field(p) is value
    assert field.at(*p.position, time=p.time) == located
    assert len(field.gradient()) == dimension
    if dimension == 0:
        assert field.laplacian()(p) == Ultra()


@pytest.mark.parametrize(
    "axes,time",
    [
        (("x", "x"), "t"),
        (("t",), "t"),
        (("i",), None),
        (("eps",), "t"),
        (("coefficient",), "t"),
        (("_hidden",), "t"),
        (("for",), "t"),
    ],
)
def test_bad_coordinate_names(axes, time):
    with pytest.raises(ValueError):
        CoordinateSpace(axes, time)


def test_points_validate_and_copy_coordinates():
    space = CoordinateSpace()
    with pytest.raises(ValueError):
        space.point(1, 2)
    with pytest.raises(ValueError):
        SpaceTimePoint(space, (1, 2, 3))
    with pytest.raises(ValueError):
        space.point(1, 2, math.inf)
    with pytest.raises(TypeError):
        space.point(1, True, 3)
    with pytest.raises(TypeError):
        space.point(1, I, 3)
    with pytest.raises(ValueError):
        CoordinateSpace((), None).point(time=1)
    with pytest.raises(ValueError):
        CoordinateSpace.cartesian(True)
    p = space.point(1, 2, 3)
    assert p.time == 0
    coordinates = p.coordinates
    coordinates["x"] = 100
    assert p["x"] == 1
    with pytest.raises(ValueError):
        p.replace(unknown=5)
    with pytest.raises(ValueError):
        space.from_coordinates({"x": 1, "y": 2, "z": 3})


def test_located_arithmetic_is_same_point_and_relocation_explicit():
    p = CoordinateSpace().point(1, 2, 3, time=4)
    a = LocatedUltra(1 + I + EPS, p)
    b = LocatedUltra(2 + J * 0.5, p)
    for result, expected in [
        (a + b, a.value + b.value),
        (a - b, a.value - b.value),
        (a * b, a.value * b.value),
        (a / b, a.value / b.value),
        (I + a, I + a.value),
        (I - a, I - a.value),
        (I * a, I * a.value),
        (I / a, I / a.value),
        (a**3, a.value**3),
        (a.map(Ultra.exp), a.value.exp()),
    ]:
        assert result.point == p
        assert result.value == expected
    moved = b.relocated(p.replace(t=5))
    assert moved.value is b.value
    for operation in [lambda: a + moved, lambda: a - moved, lambda: a * moved, lambda: a / moved]:
        with pytest.raises(ValueError, match="same point"):
            operation()


def test_formula_parameters_snapshot_and_no_coordinates_as_algebra_axes():
    params = {"speed": 2 + EPS}
    field = UltraField.from_formula("exp(i*(x-speed*t))+j*y+eps*i*j*z", parameters=params)
    params["speed"] = 99
    expected = (I * (1 - (2 + EPS) * 4)).exp() + J * 2 + EPS * I * J * 3
    assert field.evaluate(x=1, y=2, z=3, t=4) == expected
    assert field.at(1, 2, 3, time=4).value == expected
    with pytest.raises(ValueError, match="Unbound"):
        UltraField.from_formula("x+missing")
    for params in [{"x": 2}, {"eps": 1}, {"i": 3}]:
        with pytest.raises(ValueError):
            UltraField.from_formula("x", parameters=params)


def test_lazy_pointwise_arithmetic_and_coordinate_contract():
    f = UltraField.from_formula("1+x+i*y+eps*t")
    g = UltraField.from_formula("2+j*z")
    p = f.space.point(1, 2, 0.25, time=0.5)
    for expression, expected in [
        (f + g, f(p) + g(p)),
        (f - g, f(p) - g(p)),
        (f * g, f(p) * g(p)),
        (f / g, f(p) / g(p)),
        (I / f, I / f(p)),
        (I - f, I - f(p)),
        (f**2, f(p) ** 2),
        (f.exp(), f(p).exp()),
    ]:
        assert expression(p) == expected
    other = UltraField.constant(1, CoordinateSpace.cartesian(2))
    with pytest.raises(ValueError):
        _ = f + other
    with pytest.raises(ValueError):
        f(other.space.point(0, 0))
    with pytest.raises(TypeError):
        UltraField(lambda p: True)(p)


def test_partial_retains_each_existing_tangent_coefficient():
    space = CoordinateSpace.cartesian(2)
    multiplier = Ultra(2, -3, 0.5, 0.125, 1e-40, -2e-50, 4e-60, 1e-70)
    f = UltraField(lambda p: multiplier * (p["x"] ** 4 + p["y"] ** 2 + p["t"]), space)
    p = space.point(0.7, -0.4, time=0.2)
    for name, derivative in [("x", 4 * 0.7**3), ("y", -0.8), ("t", 1)]:
        assert_coefficients(f.partial(name)(p), multiplier * derivative, rel=2e-11, abs=0)
    assert_coefficients(f.partial("x", order=2)(p), multiplier * (12 * 0.7**2), rel=2e-9, abs=0)
    assert_coefficients(f.laplacian()(p), multiplier * (12 * 0.7**2 + 2), rel=2e-9, abs=0)


def test_analytic_partial_and_numerical_convergence():
    space = CoordinateSpace.cartesian(1, time_axis=None)
    f = UltraField(lambda p: math.sin(p["x"]) * (1 + EPS), space)
    p = space.point(0.4)
    exact = (1 + EPS) * math.cos(0.4)
    errors = [abs(f.partial("x", step=h)(p).real - exact.real) for h in (0.2, 0.1, 0.05)]
    assert 14 < errors[0] / errors[1] < 17
    assert 14 < errors[1] / errors[2] < 17
    analytic = UltraField(f.rule, space, partials={"x": lambda p: (1 + EPS) * math.cos(p["x"])})
    assert analytic.partial("x")(p) == exact


def test_spatial_and_parameter_derivatives_coexist_in_wave_model():
    # Epsilon is the speed parameter, not a coordinate differentiation seed.
    f = UltraField.from_formula("exp(i*(2*x-(speed+eps)*2*t))", parameters={"speed": 1.5})
    p = f.space.point(0.3, 2, 3, time=0.7)
    assert_coefficients(f.partial("x")(p), 2 * I * f(p), rel=1e-10)
    # The speed sensitivity solves the differentiated, inhomogeneous equation:
    # L(d_c F) = (2/c) F_xx, although L(F_body)=0.
    result = f.wave_operator(speed=1.5)(p)
    assert_coefficients(result.primal, Ultra(), abs=2e-8)
    assert_coefficients(result.tangent, f(p).primal * (-8 / 1.5), abs=3e-8)


@pytest.mark.parametrize("step", [0, -1, math.inf, math.nan, 1e308, 1e-300])
def test_derivative_step_validation(step):
    with pytest.raises(ValueError):
        UltraField.from_formula("x").partial("x", order=2, step=step)


def test_derivative_domains_fail_explicitly():
    f = UltraField.from_formula("x")
    with pytest.raises(ValueError):
        f.partial("x")(f.space.point(1e30, 0, 0))
    with pytest.raises(ValueError):
        f.partial("missing")
    with pytest.raises(ValueError):
        f.partial("x", order=True)
    with pytest.raises(ValueError):
        f.wave_operator(speed=0)
    with pytest.raises(ValueError):
        UltraField.constant(1, CoordinateSpace((), None)).wave_operator()


def test_slices_keep_original_location_and_explicit_reduced_field():
    f = UltraField.from_formula("x+10*y+100*z+1000*t+eps*i*x*y")
    view = f.slice(z=2).slice(t=3)
    assert view.space == CoordinateSpace(("x", "y"), None)
    located = view.at(4, 5)
    assert located.point == f.space.point(4, 5, 2, time=3)
    assert located.value == f(located.point)
    assert view.evaluate(x=4, y=5) == located.value
    assert view.as_field().at(4, 5).point == view.space.point(4, 5)
    assert view.slice(x=4, y=5).at() == located
    with pytest.raises(ValueError):
        view.slice(t=4)
    with pytest.raises(ValueError):
        view.evaluate(x=4, y=5, t=4)


def test_grid_ij_axis_order_full_coefficients_and_zero_dimensional_sample():
    f = UltraField.from_formula("x+10*y+eps*i*j*t")
    view = f.slice(z=9, t=0.5)
    grid = view.sample({"y": [1, 2], "x": [3, 4, 5]})
    assert grid.shape == (2, 3)
    assert grid.at_index(1, 2) == f.at(5, 2, 9, time=0.5)
    assert list(view.iter_samples({"y": [1, 2], "x": [3, 4, 5]})) == [
        grid.at_index(a, b) for a in range(2) for b in range(3)
    ]
    single = view.slice(x=3, y=1).sample({})
    assert single.shape == ()
    assert single.at_index() == f.at(3, 1, 9, time=0.5)
    with pytest.raises(IndexError):
        grid.at_index(-1, 0)
    with pytest.raises(IndexError):
        grid.at_index(0)
    with pytest.raises(ValueError):
        view.sample({"x": [1], "y": []})
    with pytest.raises(ValueError):
        view.sample({"x": [1]})
    with pytest.raises(ValueError):
        view.sample({"x": [1], "y": [1], "z": [1]})
    with pytest.raises(ValueError):
        view.sample({"x": [1, 2], "y": [1, 2]}, max_points=3)
    with pytest.raises(ValueError):
        FieldGrid(f.space, grid.axes, grid.fixed, grid.values[:-1])


def test_optional_array_adapters():
    pytest.importorskip("numpy")
    f = UltraField.from_formula("x+eps*i*y")
    grid = f.slice(z=0, t=2).sample({"x": [0, 2, 4], "y": [1, 3]})
    array = grid.to_numpy()
    assert array.shape == (3, 2, 8)
    assert tuple(array[2, 1]) == f.at(4, 3, 0, time=2).value.coefficients
    array[:] = 99
    assert grid.at_index(0, 0).value == EPS * I
    pytest.importorskip("xarray")
    named = grid.to_xarray()
    assert named.dims == ("x", "y", "coefficient")
    assert list(named.coefficient.values) == list(BASIS)
    assert named.sel(x=4, y=3, coefficient="eps*i").item() == 3
    assert named.coords["z"].item() == 0
    assert named.coords["t"].item() == 2
    scalar = f.slice(x=0, y=1, z=0, t=2).sample({})
    assert scalar.to_numpy().shape == (8,)
    assert scalar.to_xarray().dims == ("coefficient",)


def test_coordinate_pullback_moves_only_coordinates():
    source = CoordinateSpace(("u", "v"))
    target = CoordinateSpace()
    transform = CoordinateMap(
        source, target, lambda p: target.point(2 * p["u"], 3 * p["v"], 7, time=p.time)
    )
    f = UltraField.from_formula("x+i*y+j*z+eps*t", space=target)
    pulled = transform.pullback(f)
    p = source.point(0.25, 0.5, time=2)
    assert pulled(p) == Ultra(0.5, 7, 1.5, 0, 2)
    assert transform.locate(pulled.at(*p.position, time=p.time)) == f.at(0.5, 1.5, 7, time=2)
    assert_coefficients(pulled.partial("u")(p), Ultra(2))
    with pytest.raises(ValueError):
        transform.pullback(pulled)
    bad = CoordinateMap(source, target, lambda p: p)
    with pytest.raises(ValueError):
        bad(p)


def test_real_spacetime_map_preserves_a_scalar_wave_equation():
    # An explicit Lorentz coordinate change with c=1, applied to a scalar field.
    # No internal generator is identified with a space/time direction.
    rest = CoordinateSpace()
    moving = CoordinateSpace(("u", "v", "w"), time_axis="clock")
    speed = 0.4
    gamma = 1 / math.sqrt(1 - speed**2)
    boost = CoordinateMap(
        moving,
        rest,
        lambda p: rest.point(
            gamma * (p["u"] + speed * p["clock"]),
            p["v"],
            p["w"],
            time=gamma * (p["clock"] + speed * p["u"]),
        ),
    )
    f = UltraField.from_formula("exp(i*(x-t))*(1+j/4+eps*i*j)", space=rest)
    pulled = boost.pullback(f)
    p = moving.point(0.7, 0.2, -0.1, time=0.3)
    assert_coefficients(pulled.wave_operator()(p), Ultra(), abs=3e-8)
    q = boost(p)
    assert p["clock"] ** 2 - sum(x * x for x in p.position) == pytest.approx(
        q["t"] ** 2 - sum(x * x for x in q.position)
    )
