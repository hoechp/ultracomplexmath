"""Residue classes and complete addition/multiplication tables."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Residue:
    modulus: int
    value: int

    def __post_init__(self) -> None:
        if self.modulus < 1:
            raise ValueError("Modulus must be positive")
        object.__setattr__(self, "value", self.value % self.modulus)

    def _check(self, other: Residue) -> None:
        if self.modulus != other.modulus:
            raise ValueError("Different rings")

    def __add__(self, other: Residue) -> Residue:
        self._check(other)
        return Residue(self.modulus, self.value + other.value)

    def __mul__(self, other: Residue) -> Residue:
        self._check(other)
        return Residue(self.modulus, self.value * other.value)

    def __pow__(self, exponent: int) -> Residue:
        return Residue(self.modulus, pow(self.value, exponent, self.modulus))

    def inverse(self) -> Residue:
        return self**-1

    @property
    def powers(self) -> frozenset[Residue]:
        current, seen = Residue(self.modulus, 1), set()
        while current not in seen:
            seen.add(current)
            current *= self
        return frozenset(seen)

    @property
    def order(self) -> int:
        """Cardinality of the power orbit including 1, also for nonunits."""
        return len(self.powers)


@dataclass(frozen=True)
class ModularRing:
    modulus: int

    def __post_init__(self) -> None:
        if self.modulus < 1:
            raise ValueError("Modulus must be positive")

    def __call__(self, value: int) -> Residue:
        return Residue(self.modulus, value)

    @property
    def residues(self) -> tuple[Residue, ...]:
        return tuple(self(i) for i in range(self.modulus))

    @property
    def addition_table(self) -> tuple[tuple[int, ...], ...]:
        return tuple(
            tuple((a + b) % self.modulus for b in range(self.modulus)) for a in range(self.modulus)
        )

    @property
    def multiplication_table(self) -> tuple[tuple[int, ...], ...]:
        return tuple(
            tuple((a * b) % self.modulus for b in range(self.modulus)) for a in range(self.modulus)
        )


Restklasse = Residue
ZModuloNZRing = ModularRing
