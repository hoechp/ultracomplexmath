"""Exact Segre coordinates on the tangent bundle of the split projective quadric."""

from __future__ import annotations

from dataclasses import dataclass

from .exact import QJ, QONE, ExactUltra
from .transformations import ProjectivePoint


@dataclass(frozen=True, slots=True)
class SegreQuadricPoint:
    """Homogeneous [su:sv:tu:tv] over the Gaussian-rational dual numbers."""

    su: ExactUltra
    sv: ExactUltra
    tu: ExactUltra
    tv: ExactUltra

    def __post_init__(self) -> None:
        entries = self.su, self.sv, self.tu, self.tv
        if any(not isinstance(q, ExactUltra) or q != q.conjugate("j") for q in entries):
            raise TypeError("Quadric coordinates must be exact complex-dual scalars")
        if not any(q.primal for q in entries):
            raise ValueError("At least one homogeneous body coordinate must be nonzero")
        if self.su * self.tv != self.sv * self.tu:
            raise ValueError("Coordinates violate the quadric or its tangent equation")

    @classmethod
    def from_projective(cls, point: ProjectivePoint[ExactUltra]) -> SegreQuadricPoint:
        if not isinstance(point.x, ExactUltra):
            raise TypeError("The exact Segre map requires an exact projective point")
        # Embed each channel as the same complex-dual scalar in both modes.
        xp, xm = point.x.channels()
        yp, ym = point.y.channels()
        s, t, u, v = (ExactUltra.from_channels(c, c) for c in (xp, yp, xm, ym))
        return cls(s * u, s * v, t * u, t * v)

    def to_projective(self) -> ProjectivePoint[ExactUltra]:
        """A unit pivot selects a column and row, even at mixed infinities."""
        rows = ((self.su, self.sv), (self.tu, self.tv))
        i, j = next((i, j) for i in range(2) for j in range(2) if rows[i][j].primal)
        plus, minus = (QONE + QJ) / 2, (QONE - QJ) / 2
        return ProjectivePoint(
            rows[0][j] * plus + rows[i][0] * minus, rows[1][j] * plus + rows[i][1] * minus
        )
