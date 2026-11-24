"""Gaussian-rational Jones optics and real Stokes observables with first variations."""

from __future__ import annotations

from dataclasses import dataclass

from .exact import QI, ExactScalar, ExactUltra
from .exact_linalg import ExactMatrix
from .transformations import ModeOperator


@dataclass(frozen=True, init=False, slots=True)
class ExactStokes:
    """H_12=(S2+i*S3)/2. Physical Stokes bodies and two-sided first variations."""

    s0: ExactUltra
    s1: ExactUltra
    s2: ExactUltra
    s3: ExactUltra

    def __init__(self, s0: ExactScalar, s1: ExactScalar, s2: ExactScalar, s3: ExactScalar) -> None:
        for name, value in zip(("s0", "s1", "s2", "s3"), (s0, s1, s2, s3), strict=True):
            v = ExactUltra.coerce(value)
            if v != ExactUltra.dual(v.real, v.eps):
                raise ValueError("Stokes observables must be real dual scalars")
            object.__setattr__(self, name, v)
        norm = self.interval
        if self.s0.real < 0 or norm.real < 0:
            raise ValueError("Stokes body lies outside the future intensity cone")
        if not norm.real and norm.eps:
            raise ValueError("At the polarization boundary a two-sided variation must be tangent")
        if not self.s0.real and any(v.eps for v in (self.s0, self.s1, self.s2, self.s3)):
            raise ValueError("At zero intensity every two-sided first variation vanishes")

    @property
    def interval(self) -> ExactUltra:
        """Four times the coherency determinant, including its derivative."""
        return self.s0**2 - self.s1**2 - self.s2**2 - self.s3**2

    @classmethod
    def from_jones(cls, state: ExactUltra) -> ExactStokes:
        """The two split channels are the two coherent field amplitudes."""
        if not isinstance(state, ExactUltra):
            raise TypeError("Jones amplitudes require an ExactUltra")
        u, v = (ExactUltra.from_channels(c, c) for c in state.channels())
        cross = u * v.conjugate("i")
        return cls(
            u.abs2() + v.abs2(), u.abs2() - v.abs2(), 2 * cross.real_part(), 2 * cross.imag_part()
        )

    def coherency(self) -> ExactMatrix:
        cross = (self.s2 + QI * self.s3) / 2
        return ExactMatrix(
            [[(self.s0 + self.s1) / 2, cross], [cross.conjugate("i"), (self.s0 - self.s1) / 2]]
        )

    @classmethod
    def from_coherency(cls, matrix: ExactMatrix) -> ExactStokes:
        if matrix.shape != (2, 2):
            raise ValueError("Coherency requires a 2 by 2 matrix")
        (a, b), (c, d) = matrix.rows
        if c != b.conjugate("i"):
            raise ValueError("Coherency requires a Hermitian matrix")
        return cls(a + d, a - d, b + c, (b - c) / QI)

    def through(self, element: ModeOperator[ExactUltra]) -> ExactStokes:
        """Jones congruence G H G†, including singular polarizers and varying G."""
        if not isinstance(element.alpha, ExactUltra):
            raise TypeError("The Jones operator must have exact coefficients")
        g = ExactMatrix(element.matrix())
        adjoint = ExactMatrix([[v.conjugate("i") for v in row] for row in g.transpose.rows])
        return self.from_coherency(g @ self.coherency() @ adjoint)
