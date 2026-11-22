"""Integer and modular foundations; Python int supplies arbitrary precision.

Primality is deterministic below 2**64 and probabilistic above it.
"""

from __future__ import annotations

import math
import secrets
from dataclasses import dataclass


def is_prime(n: int, *, rounds: int = 32) -> bool:
    if rounds < 1:
        raise ValueError("rounds must be positive")
    if n < 2:
        return False
    for p in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if n % p == 0:
            return n == p
    d, s = n - 1, 0
    while d % 2 == 0:
        d //= 2
        s += 1
    bases = (
        (2, 325, 9375, 28178, 450775, 9780504, 1795265022)
        if n < 2**64
        else tuple(secrets.randbelow(n - 3) + 2 for _ in range(rounds))
    )
    for a in bases:
        a %= n
        if a < 2:
            continue
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(s - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False
    return True


def next_prime(n: int) -> int:
    n += 1
    if n <= 2:
        return 2
    n |= 1
    while not is_prime(n):
        n += 2
    return n


def integer_root(n: int, direction: int = 0) -> int | None:
    root = math.isqrt(n)
    if root * root == n or direction < 0:
        return root
    return root + 1 if direction > 0 else None


def root_and_remainder(n: int) -> tuple[int, int]:
    root = math.isqrt(n)
    return root, n - root * root


def extended_gcd(a: int, b: int) -> tuple[int, int, int]:
    old_r, r, old_s, s, old_t, t = a, b, 1, 0, 0, 1
    while r:
        q = old_r // r
        old_r, r = r, old_r - q * r
        old_s, s = s, old_s - q * s
        old_t, t = t, old_t - q * t
    sign = -1 if old_r < 0 else 1
    return sign * old_r, sign * old_s, sign * old_t


def euklid(a: int, b: int) -> tuple[int, int, int, int, int]:
    a, b = max(a, b), min(a, b)
    g, x, y = extended_gcd(a, b)
    return g, x, a, y, b


def modular_inverse(value: int, modulus: int) -> int:
    if modulus <= 1:
        raise ValueError("Modulus must exceed one")
    return pow(value, -1, modulus)


@dataclass(frozen=True)
class FermatFactors:
    steps: int
    lower: int
    upper: int


def fermat_factors(n: int, *, max_steps: int | None = None) -> FermatFactors:
    if n < 1:
        raise ValueError("Expected a positive integer")
    if max_steps is not None and max_steps < 1:
        raise ValueError("max_steps must be positive")
    if n % 2 == 0:
        return FermatFactors(1, min(2, n // 2), max(2, n // 2))
    a = math.isqrt(n)
    if a * a < n:
        a += 1
    step = 0
    while True:
        step += 1
        b = math.isqrt(a * a - n)
        if b * b == a * a - n:
            return FermatFactors(step, a - b, a + b)
        if max_steps is not None and step >= max_steps:
            raise TimeoutError("Fermat step limit reached")
        a += 1


def fermat_output(n: int, *, max_steps: int | None = None) -> str:
    f = fermat_factors(n, max_steps=max_steps)
    return f"{n} = {f.lower} × {f.upper} ({f.steps} steps)"


def congruent_prime(p: int, minimum_bits: int) -> tuple[int, int]:
    if p < 1 or minimum_bits < 2:
        raise ValueError("Invalid bounds")
    i = max(1, ((1 << (minimum_bits - 1)) - 1 + p - 1) // p)
    while not is_prime(i * p + 1):
        i += 1
    return i, i * p + 1


class BigInt(int):
    """Optional familiar constructor; ordinary int operations remain native."""

    next_prime = staticmethod(next_prime)
    root = staticmethod(integer_root)
    root_and_remainder = staticmethod(root_and_remainder)
    is_square = staticmethod(lambda n: n >= 0 and math.isqrt(n) ** 2 == n)
    fermat_factors = staticmethod(fermat_factors)
    euklid = staticmethod(euklid)
