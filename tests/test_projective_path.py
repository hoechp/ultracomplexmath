from fractions import Fraction as F
from itertools import islice
from math import atan, degrees

import pytest

from examples.impact_models import coating_reference
from examples.projective_paths import glass_point, pole_point
from ultracomplexmath import (
    EPS,
    ONE,
    QEPS,
    QI,
    QJ,
    QONE,
    QZERO,
    ExactComplex,
    ExactUltra,
    J,
    NonFiniteError,
    ProjectivePoint,
    Ultra,
    projective_path,
)


def test_both_affine_poles_in_both_directions():
    ts = [-3, -2, -1, 0, 1, 2, 3]
    for parameters in (ts, ts[::-1]):
        for t, coords in zip(
            parameters, projective_path(pole_point(v) for v in parameters), strict=True
        ):
            for a, coord in zip([t + 1, t - 1], coords, strict=True):
                if not a:
                    assert coord.chart == "x"
                expected = (a, 1) if coord.chart == "x" else (1 / a, -1 / a**2)
                assert (coord.value, coord.tangent) == pytest.approx(expected)
            if t == 1:
                assert coords[1].value == 0 and coords[1].tangent == 1
                assert coords[0].chart == "y" and coords[0].value == 0.5


def test_exact_one_channel_pole_and_chart_overlap():
    points = [ProjectivePoint(QONE, ExactUltra(t) + QJ + QEPS) for t in (3, 2, 1)]
    plus, minus = list(projective_path(points))[-1]
    assert (plus.chart, plus.value, plus.tangent) == (
        "y",
        ExactComplex(F(1, 2)),
        ExactComplex(F(-1, 4)),
    )
    assert (minus.chart, minus.value, minus.tangent) == ("x", ExactComplex(0), ExactComplex(1))
    z = QONE + QI + QEPS * (QONE - QI)
    a = ProjectivePoint(QONE, z)
    b = list(projective_path([ProjectivePoint(QONE, QZERO), a]))[-1]
    c = next(projective_path([a]))
    assert b[0].chart == "x" and c[0].chart == "y"
    assert b[0].value * c[0].value == ExactComplex(1)
    assert b[0].tangent == -c[0].tangent / (c[0].value ** 2)


def test_hysteresis_and_invariance_under_unit_rescaling():
    scale = 3 + QI + QEPS - QJ
    ys = [ExactUltra(t) for t in (1, F(3, 4), F(1, 2), F(1, 3), 2, 3)]
    points = [ProjectivePoint(QONE, y + QEPS) for y in ys]
    trace = list(projective_path(points))
    assert [p.chart for p, _ in trace] == ["y", "y", "x", "x", "y", "y"]
    assert trace == list(
        projective_path(ProjectivePoint(pt.x * scale, pt.y * scale) for pt in points)
    )


def test_streaming_domains_and_scale_extremes():
    assert list(projective_path([])) == []

    def stream():
        yield pole_point(0)
        raise AssertionError("consumed past requested sample")

    assert len(list(islice(projective_path(stream()), 1))) == 1
    with pytest.raises(TypeError, match="domain"):
        list(projective_path([pole_point(1), ProjectivePoint(QONE, QZERO)]))
    # Plus body exceeds float range in homogeneous coordinates; normalized ratios fit.
    big = Ultra(1.5e308, j=1e308)
    assert all(
        c.value == 1 and c.tangent == 0 for c in next(projective_path([ProjectivePoint(big, big)]))
    )
    with pytest.raises(NonFiniteError):
        next(projective_path([ProjectivePoint(EPS * 1e308, Ultra(1e-310))]))
    with pytest.raises(ValueError):
        ProjectivePoint(ONE + J, EPS + ONE + J)


@pytest.mark.parametrize("slope", [0, 0.75, 1.5, 2.5, 3.5])
def test_bare_glass_coordinates_and_tangents_against_fresnel(slope):
    def reference(u):
        return coating_reference(550, degrees(atan(u)), layers=(), substrate_index=1.5)

    channels = glass_point(slope).y.channels()
    for j, (val, tangent) in enumerate(channels):
        assert val == pytest.approx(reference(slope)[j], abs=2e-15)
        if slope > 0:
            h = 1e-5
            derivative = (reference(slope + h)[j] - reference(slope - h)[j]) / (2 * h)
            assert tangent == pytest.approx(derivative, abs=2e-10)
    if slope == 1.5:
        plus, minus = next(projective_path([glass_point(slope)]))
        assert plus.chart == "y" and minus.chart == "x"
        assert minus.value == 0 and minus.tangent.real > 0
