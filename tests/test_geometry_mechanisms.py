import math
import random

import pytest

from ultracomplexmath import DomainError
from ultracomplexmath import geometry as g
from ultracomplexmath.matrix import M2R, Matrix
from ultracomplexmath.mechanisms import Actor, Freedom, Joint, Machine, Mechanism
from ultracomplexmath.numbers import Binary, Complex, Dual


@pytest.mark.parametrize("kind", [Complex, Binary, Dual])
def test_angle_vector_roundtrip(kind):
    rng = random.Random(701)
    for _ in range(40):
        a = kind(rng.uniform(-math.pi, math.pi), rng.uniform(-1, 1))
        value = g.scale(g.vector_from_angle(a), 2.7)
        angle, scale = g.angle_from_vector(value, kind)
        assert angle.isclose(a)
        assert scale == pytest.approx(2.7)
        assert g.isclose(g.scale(g.vector_from_angle(angle), scale), value)


def test_frames_projection_rotation():
    basis = g.frame((1, 2, 3), (1, -1, 0))
    for i in range(3):
        for j in range(3):
            assert g.dot(basis[i], basis[j]) == pytest.approx(int(i == j), abs=1e-12)
    value = (1, 2, 3)
    assert g.isclose(g.from_base(g.to_base(value, basis), basis), value)
    assert g.rotate((1, 0, 0), (0, 0, 7), math.pi / 2) == pytest.approx((0, 1, 0))
    assert g.dot(g.reject(value, (1, 0, 0)), (1, 0, 0)) == 0
    assert g.azimuth((0, 1, 0)) == pytest.approx(math.pi / 2)


def test_oriented_lines():
    a = g.Line((0, 0, 0), (1, 0, 0))
    b = g.Line((0, 0, 2), (0, 1, 0))
    first, second = a.closest_points(b)
    assert g.sub(second, first) == (0, 0, 2)
    assert a.dual_angle(b).isclose(Dual(math.pi / 2, 2))
    advanced = a.transcend((0, 0, 2), a.dual_angle(b))
    assert g.isclose(advanced.point, b.point)
    assert g.isclose(advanced.direction, b.direction)
    assert a.intersection(g.Line((1, 1, 0), (0, -1, 0))) == (1, 0, 0)
    parallel = g.Line((2, 3, 0), (1, 0, 0))
    assert a.connecting_normal(parallel) == (0, 3, 0)
    for other in (b, parallel, a):
        with pytest.raises(DomainError):
            a.intersection(other)


def test_matrix_and_m2r():
    rotation = Matrix.rotation(2, math.pi / 2)
    point = Matrix(((1, 0, 0),)) @ rotation
    assert point.rows[0] == pytest.approx((0, 1, 0))
    assert (Matrix(((1, 2), (3, 4))) + Matrix(((10, 20),))).rows == ((11, 22), (13, 24))
    assert Matrix(((1, 2), (3, 4))).transpose.rows == ((1, 3), (2, 4))
    for raw, expected in [
        (((2, -3), (3, 2)), Complex(2, 3)),
        (((2, 3), (3, 2)), Binary(2, 3)),
        (((2, 3), (0, 2)), Dual(2, 3)),
    ]:
        assert M2R(raw).value == expected
        assert M2R(expected).matrix.rows == raw
    assert (M2R(Complex(1, 2)) * M2R(Binary(2, 1))).value.real == pytest.approx(2)


def test_mechanism_chain_and_axis_mode():
    root = Mechanism(Joint(angle=Binary(math.pi / 2)))
    child = Mechanism(Joint(), root)
    assert child.adjusted_joint.endpoint == pytest.approx((0, 2, 0))
    root.joint.angle = Binary(math.pi)
    root.update()
    assert child.adjusted_joint.endpoint == pytest.approx((-2, 0, 0), abs=1e-12)
    with pytest.raises(ValueError, match="cycles"):
        root.reparent(child)
    root.joint.axis = True
    root.joint.angle = Binary(math.pi / 2, 0.5)
    root.update()
    assert g.sub(child.adjusted_joint.endpoint, child.adjusted_joint.position) == pytest.approx(
        (0, 1, 0)
    )
    child.reparent(None)
    assert not root.attachments
    assert child.adjusted_joint.endpoint == (1, 0, 0)


def test_actor_repeatability_and_freedoms():
    joint = Joint()
    actor = Actor(joint, {"roll": Freedom(factor=math.pi), "stretch": Freedom(factor=4)})
    actor.act()
    first = joint.endpoint
    actor.act()
    assert joint.endpoint == first
    actor.reset()
    assert joint.endpoint == (1, 0, 0)
    f = Freedom(periodic=True, percentage=1.25, factor=8, minimum=2)
    assert f.value == 4
    f.invert()
    assert f.value == -4
    f.add_percentage(0.1)
    assert f.value == pytest.approx(-4.8)
    f.negate()
    f.add_percentage(0.1)
    assert f.value == pytest.approx(-4)
    machine = Machine(root=Mechanism(Joint(length=0)))
    m = machine.connect("arm", Joint())
    machine.actors["arm"].freedoms["real"] = Freedom(factor=math.pi)
    machine.update()
    assert m.adjusted_joint.endpoint == pytest.approx((0, 1, 0))
