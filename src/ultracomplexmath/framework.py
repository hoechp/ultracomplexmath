"""Exact first- and second-order kinematics of pinned planar bar frameworks."""

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from fractions import Fraction

from .exact_geometry import PointInput, RationalPoint2, rational_point2
from .exact_linalg import rational_solution
from .linalg import InconsistentSystemError, SingularSystemError

type Motion2D = tuple[RationalPoint2, ...]


def _pairs(values: tuple[Fraction, ...]) -> Motion2D:
    return tuple(zip(values[::2], values[1::2], strict=True))


@dataclass(frozen=True, slots=True, init=False)
class BarFramework2D:
    """Rigid bars join indexed rational points. Pins fix both coordinates."""

    points: Motion2D
    bars: tuple[tuple[int, int], ...]
    pins: tuple[int, ...]

    def __init__(
        self,
        points: Sequence[PointInput],
        bars: Sequence[tuple[int, int]],
        *,
        pins: Sequence[int] = (),
    ) -> None:
        joints = tuple(map(rational_point2, points))
        edges = tuple((i, j) for i, j in bars)
        anchors = tuple(pins)
        if not edges:
            raise ValueError("A bar framework needs at least one bar")
        for index in (*anchors, *(k for edge in edges for k in edge)):
            if type(index) is not int or not 0 <= index < len(joints):
                raise ValueError("Joint index out of range")
        if any(joints[i] == joints[j] for i, j in edges):
            raise ValueError("Bars must have positive length")
        object.__setattr__(self, "points", joints)
        object.__setattr__(self, "bars", edges)
        object.__setattr__(self, "pins", anchors)

    def _coordinate_rows(self, indices: Sequence[int]) -> list[tuple[Fraction, ...]]:
        rows = []
        for i in indices:
            if type(i) is not int or not 0 <= i < len(self.points):
                raise ValueError("Joint index out of range")
            for axis in range(2):
                row = [Fraction(0)] * (2 * len(self.points))
                row[2 * i + axis] = Fraction(1)
                rows.append(tuple(row))
        return rows

    def position_residuals(self, points: Sequence[PointInput]) -> tuple[Fraction, ...]:
        """Half the squared-length changes, then the x/y displacements of pins."""
        if len(points) != len(self.points):
            raise ValueError("One planar position is required per joint")
        candidate = tuple(map(rational_point2, points))

        def length2(configuration: Motion2D, i: int, j: int) -> Fraction:
            x, y = configuration[i]
            u, v = configuration[j]
            return (x - u) ** 2 + (y - v) ** 2

        bars = [(length2(candidate, i, j) - length2(self.points, i, j)) / 2 for i, j in self.bars]
        pins = [candidate[i][k] - self.points[i][k] for i in self.pins for k in (0, 1)]
        return tuple(bars + pins)

    @property
    def rigidity_matrix(self) -> tuple[tuple[Fraction, ...], ...]:
        """Jacobian of half squared bar lengths, followed by pin coordinates."""
        rows = []
        for i, j in self.bars:
            row = [Fraction(0)] * (2 * len(self.points))
            for axis in range(2):
                delta = self.points[i][axis] - self.points[j][axis]
                row[2 * i + axis], row[2 * j + axis] = delta, -delta
            rows.append(tuple(row))
        return (*rows, *self._coordinate_rows(self.pins))

    def velocity_basis(self) -> tuple[Motion2D, ...]:
        """Rational basis of all instantaneous motions, in joint order."""
        matrix = self.rigidity_matrix
        _, basis = rational_solution(matrix, [0] * len(matrix))
        return tuple(_pairs(vector) for vector in basis)

    def solve_velocity(self, prescribed: Mapping[int, PointInput]) -> Motion2D:
        """Unique instantaneous response to the given joint velocities."""
        rows = list(self.rigidity_matrix)
        rhs = [Fraction(0)] * len(rows)
        rows.extend(self._coordinate_rows(tuple(prescribed)))
        rhs.extend(c for point in prescribed.values() for c in rational_point2(point))
        velocity, free = rational_solution(rows, rhs)
        if free:
            raise SingularSystemError("Prescribed velocities leave free instantaneous motions")
        return _pairs(velocity)

    def first_order_residuals(self, velocity: Sequence[PointInput]) -> tuple[Fraction, ...]:
        """Half squared-length rates followed by x/y rates of the pinned joints."""
        if len(velocity) != len(self.points):
            raise ValueError("One planar velocity is required per joint")
        flat = tuple(c for pair in map(rational_point2, velocity) for c in pair)
        return tuple(
            sum((a * b for a, b in zip(row, flat, strict=True)), Fraction(0))
            for row in self.rigidity_matrix
        )

    def acceleration_for(self, velocity: Sequence[PointInput]) -> Motion2D:
        """One compatible acceleration, or InconsistentSystemError at either order.

        Passing the second-order test is necessary for a twice differentiable
        finite motion. In general it is insufficient to prove one exists.
        """
        speeds = tuple(map(rational_point2, velocity))
        if any(self.first_order_residuals(speeds)):
            raise InconsistentSystemError("Velocity violates first-order bar or pin constraints")
        rhs = [
            -((speeds[i][0] - speeds[j][0]) ** 2 + (speeds[i][1] - speeds[j][1]) ** 2)
            for i, j in self.bars
        ]
        rhs.extend([Fraction(0)] * (2 * len(self.pins)))
        try:
            particular, _ = rational_solution(self.rigidity_matrix, rhs)
        except InconsistentSystemError as exc:
            raise InconsistentSystemError("Velocity has no second-order extension") from exc
        return _pairs(particular)
