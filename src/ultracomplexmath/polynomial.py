"""Newton interpolation and the original next-value polynomial guesser."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from .core import Scalar, Ultra


@dataclass(frozen=True)
class Polynomial:
    nodes: tuple[float, ...]
    coefficients: tuple[Ultra, ...]

    @classmethod
    def interpolate(cls, nodes: Sequence[float], values: Sequence[Scalar]) -> Polynomial:
        if not nodes or len(nodes) != len(values) or len(set(nodes)) != len(nodes):
            raise ValueError("Distinct nodes and matching nonempty values are required")
        differences = [Ultra.coerce(value) for value in values]
        for order in range(1, len(nodes)):
            for i in range(len(nodes) - 1, order - 1, -1):
                differences[i] = (differences[i] - differences[i - 1]) / (
                    nodes[i] - nodes[i - order]
                )
        return cls(tuple(nodes), tuple(differences))

    def __call__(self, x: Scalar) -> Ultra:
        value = self.coefficients[-1]
        for index in range(len(self.coefficients) - 2, -1, -1):
            value = value * (Ultra.coerce(x) - self.nodes[index]) + self.coefficients[index]
        return value


def guess(values: Sequence[Scalar], max_variables: int | None = None) -> Ultra:
    count = len(values) if max_variables is None else min(len(values), max_variables)
    if count < 1:
        raise ValueError("At least one sample is required")
    return Polynomial.interpolate(list(map(float, range(count))), values[-count:])(count)
