"""Fixtures produced by compiling the unchanged Java baseline (no JUnit needed)."""

import json
from pathlib import Path

import pytest

from ultracomplexmath import geometry as g
from ultracomplexmath.matrix import M2R
from ultracomplexmath.mechanisms import Joint, Mechanism
from ultracomplexmath.numbers import Binary, Complex, Dual
from ultracomplexmath.polynomial import guess

FIXTURE = json.loads(
    (Path(__file__).parents[1] / "tests/fixtures/legacy-extended.json").read_text()
)["cases"]


@pytest.mark.parametrize("name,kind", [("complex", Complex), ("split", Binary), ("dual", Dual)])
@pytest.mark.parametrize(
    "operation", ["square", "inverse", "exp", "sin", "cos", "log", "angle_vector"]
)
def test_java_number_fixture(name, kind, operation):
    value = kind(0.4, 0.2)
    if operation == "angle_vector":
        result = g.vector_from_angle(value)
    else:
        result_value = value * value if operation == "square" else getattr(value, operation)()
        result = result_value.real, result_value.imag
    assert result == pytest.approx(FIXTURE[f"{name}_{operation}"], abs=1e-12)


def test_java_geometry_and_mechanism_fixtures():
    assert g.to_frame((1, 0, 0), (1, 2, 3), (2, -1, 0)) == pytest.approx(FIXTURE["frame_x"])
    assert g.rotate((1, 2, 3), (0, 0, 1), 0.7) == pytest.approx(FIXTURE["rotation"])
    first, second = g.Line((0, 0, 0), (1, 0, 0)), g.Line((0, 0, 2), (0, 1, 0))
    assert first.connecting_normal(second) == pytest.approx(FIXTURE["normal"])
    angle = first.dual_angle(second)
    assert (angle.real, angle.imag) == pytest.approx(FIXTURE["dual_angle"])
    value = M2R(((1, 2), (-3, 4))).value
    assert (value.real, value.imag) == pytest.approx(FIXTURE["m2r"])
    root = Mechanism(Joint(length=2, angle=Binary(0.5, 0.3)))
    child = Mechanism(Joint(position=(0.2, -0.1, 0.3), angle=Dual(0.2, 0.1)), root)
    assert root.adjusted_joint.endpoint == pytest.approx(FIXTURE["joint_end"])
    assert child.adjusted_joint.endpoint == pytest.approx(FIXTURE["child_end"])
    root.joint.axis = True
    root.update()
    assert child.adjusted_joint.endpoint == pytest.approx(FIXTURE["axis_child_end"])
    assert guess([2.53, 3.04, 3.70, 4.45, 5.31, 6.12, 6.90], 3).real == pytest.approx(
        FIXTURE["guess"][0]
    )
