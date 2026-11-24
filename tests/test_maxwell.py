import itertools
import math
from fractions import Fraction as F

import pytest

from examples.maxwell import SEEDS, crossing_link, fibers, presets, render
from ultracomplexmath import (
    EPS,
    QEPS,
    QI,
    QJ,
    QZERO,
    DomainError,
    MaxwellField,
    MaxwellMode,
    MaxwellState,
    Ultra,
    exact_hopfion,
    hopfion,
    periodic_maxwell_field,
)


def vector_close(a, b, abs_tol=2e-12):
    assert len(a) == len(b)
    assert all(x.isclose(y, abs_tol=abs_tol, rel_tol=2e-12) for x, y in zip(a, b, strict=True))


@pytest.mark.parametrize("t", [0, 0.31, -1.2, math.pi / 2, 2 * math.pi])
def test_standing_and_circular_waves_against_real_solutions(t):
    x, z = 0.7, -0.52
    standing = MaxwellField(presets()["standing"])
    s = standing.at(x, -0.25, z, time=t)
    vector_close(s.electric, [0, math.cos(x) * math.cos(t), 0])
    vector_close(s.magnetic, [0, 0, math.sin(x) * math.sin(t)])
    wave = MaxwellField(presets()["traveling"]).at(x, 0, z, time=t)
    vector_close(wave.electric, [math.cos(z - t), -math.sin(z - t), 0])
    vector_close(wave.magnetic, [math.sin(z - t), math.cos(z - t), 0])
    vector_close(wave.poynting, [0, 0, 1])
    assert wave.energy.isclose(1) and wave.invariant.isclose(0)
    assert standing.component("y").at(x, -0.25, z, time=t).value == s.components[1]


def test_vacuum_evolution_obeys_maxwell_and_local_energy_balance_in_3d():
    modes = presets()["crossing"]
    field = MaxwellField(modes + [MaxwellMode((0, 0, 0), (0, 0, 0), (0, 0, 1))])
    x = (0.314, 0.58, -0.81)
    t = 0.733
    step = 1e-5

    def spatial(axis, sign):
        pos = list(x)
        pos[axis] += step * sign
        return field.at(*pos, time=t)

    sides = [(spatial(axis, 1), spatial(axis, -1)) for axis in range(3)]
    plus, minus = field.at(*x, time=t + step), field.at(*x, time=t - step)

    def derivative(v, w):
        return (v - w) / (2 * step)

    for attr, other, sign in (("electric", "magnetic", 1), ("magnetic", "electric", -1)):
        jac = [
            [derivative(getattr(p, attr)[i], getattr(m, attr)[i]) for i in range(3)]
            for p, m in sides
        ]
        assert abs(sum(jac[i][i].real for i in range(3))) < 2e-9
        curl = [jac[1][2] - jac[2][1], jac[2][0] - jac[0][2], jac[0][1] - jac[1][0]]
        vector_close(
            curl,
            [
                sign * -derivative(a, b)
                for a, b in zip(getattr(plus, other), getattr(minus, other), strict=True)
            ],
            abs_tol=3e-9,
        )
    div_s = sum(derivative(p.poynting[i], m.poynting[i]).real for i, (p, m) in enumerate(sides))
    assert abs(derivative(plus.energy, minus.energy).real + div_s) < 4e-9
    assert MaxwellField([]).at(1, 2, 3).energy == Ultra()


def test_modes_keep_an_independent_parameter_in_every_component():
    k = (2, 2, 1)
    m = MaxwellMode.traveling(
        k,
        [Ultra.complex(1, 2).with_tangent(2 - 1j), Ultra.complex(-1, -2).with_tangent(-2 + 1j), 0],
    )
    x = (0.8, 0.1, -0.5)
    t = 0.4
    phi = sum(a * b for a, b in zip(k, x, strict=True)) - 3 * t
    wave = m.at(x, t)
    assert wave.electric[0].isclose(
        Ultra.dual(math.cos(phi) - 2 * math.sin(phi), 2 * math.cos(phi) + math.sin(phi))
    )
    assert wave.invariant.isclose(0)
    # Magnetic and electric waves propagating together have |S|=u, including the tangent.
    n = [2 / 3, 2 / 3, 1 / 3]
    vector_close(wave.poynting, [wave.energy * a for a in n])


def test_transversality_and_reality_domains():
    for e, b in [((1, 0, 0), (0, 1, 0)), ((EPS * 1e-90, 1, 0), (0, 0, 0)), ((0, 1, 0), (1j, 0, 0))]:
        with pytest.raises(ValueError, match="transverse"):
            MaxwellMode((1, 0, 0), e, b)
    with pytest.raises(ValueError):
        MaxwellMode((0, 0, 0), (0, 1j, 0), (0, 0, 0))
    with pytest.raises(ValueError):
        MaxwellMode.traveling((0, 0, 0), (0, 1, 0))
    with pytest.raises(ValueError):
        MaxwellState.from_fields((1j, 0, 0), (0, 0, 0))
    with pytest.raises(ValueError):
        MaxwellField([]).at(0, 0, 0, time=float("nan"))


def test_observers_keep_invariants_and_can_stop_only_nonnull_energy_flux():
    s = MaxwellState.from_fields((1 + EPS, 2, -0.5), (-0.1, 1, 3 - EPS / 2))
    n = (2, 1, -4)
    r = 0.72
    s1 = s.boosted(n, r)
    assert s1.invariant.isclose(s.invariant)
    vector_close(s1.boosted(n, -r).components, s.components)
    inv = s.invariant
    # Complex norm uses ij as its imaginary unit, and retains epsilon.
    w4 = Ultra.dual(inv.real, inv.eps) ** 2 + Ultra.dual(inv.ij, inv.eps_ij) ** 2
    assert (4 * (s.energy**2 - sum((q**2 for q in s.poynting), Ultra()))).isclose(w4)
    direction, rapidity = s.energy_rest_boost()
    rest = s.boosted(direction, rapidity)
    assert all(abs(v.real) < 1e-12 for v in rest.poynting)
    assert rest.energy.real == pytest.approx(math.hypot(inv.real, inv.ij) / 2)
    for scale in [1e-200, 1e200]:
        large = MaxwellState.from_fields(
            [scale * x.real for x in s.electric], [scale * x.real for x in s.magnetic]
        )
        assert large.energy_rest_boost()[1] == pytest.approx(rapidity)
    plane = MaxwellState.from_fields((1, 0, 0), (0, 1, 0))
    with pytest.raises(DomainError):
        plane.energy_rest_boost()
    assert plane.boosted((0, 0, 1), r).energy.real == pytest.approx(math.exp(-2 * r))
    assert MaxwellState.from_fields((0, 0, 0), (0, 0, 0)).energy_rest_boost()[1] == 0
    with pytest.raises(ValueError):
        s.boosted((0, 0, 0), r)


@pytest.mark.parametrize(
    "coordinates", [(0, 0, 0, 0), (1, 3, -2, 1), (F(3, 7), F(-1, 4), F(2, 5), F(-7, 3))]
)
def test_hopfion_exactly_solves_the_full_spacetime_equation(coordinates):
    def at(values):
        x, y, z, t = values
        return exact_hopfion(x, y, z, time=t)

    f = at(coordinates)
    assert sum((v * v for v in f), QZERO) == QZERO
    deriv = []
    for axis in range(4):
        point = list(coordinates)
        point[axis] += QEPS
        seeded = at(point)
        assert all(v.primal == u for v, u in zip(seeded, f, strict=True))
        deriv.append([v.tangent for v in seeded])
    dx, dy, dz, dt = deriv
    assert dx[0] + dy[1] + dz[2] == QZERO
    curl = (dy[2] - dz[1], dz[0] - dx[2], dx[1] - dy[0])
    assert tuple(dt) == tuple(-QI * QJ * w for w in curl)
    s = hopfion(*map(float, coordinates[:3]), time=float(coordinates[3]))
    vector_close(s.components, [v.approximate() for v in f])
    assert math.hypot(*(v.real for v in s.poynting)) == pytest.approx(s.energy.real)
    with pytest.raises(ValueError):
        exact_hopfion(QI, 0, 0)


def test_hopfion_lines_are_closed_linked_and_tangent_to_the_electric_field():
    curves = fibers(8)
    for seed, curve in zip(SEEDS, curves, strict=True):
        assert tuple(seed) == curve[0] == curve[-1]
        for x, y, z in curve[:-1:5]:
            r2 = x * x + y * y + z * z
            # Stereographic derivative of the great-circle generator, times two.
            tangent = (r2 - 1 - 2 * x * x, 2 * (z - x * y), -2 * (y + x * z))
            e = exact_hopfion(x, y, z)
            assert tuple(v.real * (1 + r2) ** 3 for v in e) == tangent
    for a, b in itertools.combinations(curves, 2):
        assert crossing_link(a, b) == 1
        assert crossing_link(a, list(reversed(b))) == -1


def test_periodic_fft_recovers_oblique_standing_and_dc_fields_off_grid():
    np = pytest.importorskip("numpy")
    shape = (7, 8, 5)
    axes = [np.arange(n) * math.tau / n for n in shape]
    x, y, z = np.meshgrid(*axes, indexing="ij")
    phase = x + 2 * y - z
    direction = np.array([2.0, -1.0, 0.0])
    e = np.cos(phase)[..., None] * direction
    b = np.zeros_like(e)
    b[..., 2] = 0.25
    f = periodic_maxwell_field(e, b, (math.tau,) * 3, electric_tangent=3 * e)
    assert len(f.modes) == 2
    analytic = MaxwellField(
        [
            MaxwellMode((1, 2, -1), [v * (1 + 3 * EPS) for v in direction], (0, 0, 0)),
            MaxwellMode((0, 0, 0), (0, 0, 0), (0, 0, 0.25)),
        ]
    )
    for position, t in [((0.4, -0.713, 0.62), -0.71), ((2, 1, 3), 0)]:
        vector_close(f.at(*position, time=t).components, analytic.at(*position, time=t).components)
    zeros = e * 0
    with pytest.raises(ValueError, match="divergence"):
        periodic_maxwell_field(e[..., ::-1], zeros, (1, 1, 1))
    ny = ((-1.0) ** np.arange(8))[None, :, None] * np.ones(shape)
    zeros[..., 0] = ny
    with pytest.raises(ValueError, match="Nyquist"):
        periodic_maxwell_field(zeros, b, (1, 1, 1))
    with pytest.raises(ValueError):
        periodic_maxwell_field(e[..., 0], b, (1, 1, 1))
    with pytest.raises(ValueError):
        periodic_maxwell_field(e, b * 1j, (1, 1, 1))


def test_shipped_maxwell_lab(tmp_path):
    from pathlib import Path

    page = tmp_path / "maxwell.html"
    render(page)
    assert (
        page.read_bytes()
        == (Path(__file__).resolve().parents[1] / "docs/gallery/maxwell.html").read_bytes()
    )


def test_rapid_observer_retains_a_redshifted_null_wave():
    s = MaxwellState.from_fields((1, 0, 0), (0, 1, 0))
    for rapidity in (25, 710):
        shifted = s.boosted((0, 0, 1), rapidity)
        assert shifted.electric[0].real == math.exp(-rapidity)
    tiny = MaxwellState.from_fields((0, 1, 0), (0, 0, 0)).boosted((1, 0, 0), 1e-80)
    assert tiny.magnetic[2].real == -1e-80


def test_hopfion_energy_profile_and_local_continuity_exact():
    pos = (F(-2, 5), F(3, 7), F(1, 9))
    expected = 1 / (1 + sum(x * x for x in pos)) ** 4

    def energy_flux(coords, t):
        f = exact_hopfion(*coords, time=t)
        e = [v.real_part() for v in f]
        b = [-QI * QJ * (v - u) for v, u in zip(f, e, strict=True)]
        return sum((a * a + c * c for a, c in zip(e, b, strict=True)), QZERO) / 2, (
            e[1] * b[2] - e[2] * b[1],
            e[2] * b[0] - e[0] * b[2],
            e[0] * b[1] - e[1] * b[0],
        )

    assert energy_flux(pos, 0)[0].real == expected
    t = F(1, 3)
    u, _ = energy_flux(pos, t + QEPS)
    residual = u.eps
    for axis in range(3):
        point = list(pos)
        point[axis] += QEPS
        residual += energy_flux(point, t)[1][axis].eps
    assert residual == 0
