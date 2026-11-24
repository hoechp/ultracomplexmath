"""A normalized electromagnetic Hopfion in the ij plane, with optional dual coordinates."""

from .core import I, J, Scalar, Ultra
from .exact import QI, QJ, ExactScalar, ExactUltra
from .maxwell import MaxwellState


def _field[N: (Ultra, ExactUltra)](x: N, y: N, z: N, t: N, unit: N) -> tuple[N, N, N]:
    if any(v != type(unit).dual(v.real, v.eps) for v in (x, y, z, t)):
        raise ValueError("Hopfion coordinates must be real, optionally with a real tangent")
    a, b = x - unit * y, t - unit - z
    denominator = x * x + y * y + z * z - (t - unit) ** 2
    # One common inverse for all three components of the Bateman field.
    scale = (denominator**3).inverse()
    return (b * b - a * a) * scale, -unit * (a * a + b * b) * scale, 2 * a * b * scale


def exact_hopfion(
    x: ExactScalar, y: ExactScalar, z: ExactScalar, *, time: ExactScalar = 0
) -> tuple[ExactUltra, ExactUltra, ExactUltra]:
    """Exact E + ij B on rational spacetime; real dual inputs seed any direction."""
    return _field(
        ExactUltra.coerce(x),
        ExactUltra.coerce(y),
        ExactUltra.coerce(z),
        ExactUltra.coerce(time),
        QI * QJ,
    )


def hopfion(x: Scalar, y: Scalar, z: Scalar, *, time: Scalar = 0) -> MaxwellState:
    """The same finite-energy null solution in numerical normalized units."""
    return MaxwellState(
        _field(Ultra.coerce(x), Ultra.coerce(y), Ultra.coerce(z), Ultra.coerce(time), I * J)
    )
