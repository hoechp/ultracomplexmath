import itertools
import math

import pytest

from ultracomplexmath.modular import ModularRing
from ultracomplexmath.number_theory import (
    congruent_prime,
    euklid,
    extended_gcd,
    fermat_factors,
    integer_root,
    is_prime,
    modular_inverse,
    next_prime,
    root_and_remainder,
)


def test_primes_roots_bezout_and_original_large_factors():
    for n in range(500):
        expected = n >= 2 and all(n % k for k in range(2, math.isqrt(n) + 1))
        assert is_prime(n) == expected
        root, rem = root_and_remainder(n)
        assert root * root + rem == n and 0 <= rem < 2 * root + 1
        assert integer_root(n, -1) == root
        assert integer_root(n, 1) == root + bool(rem)
        assert integer_root(n) == (None if rem else root)
    assert not is_prime(341550071728321)
    assert next_prime(100) == 101
    assert euklid(40, 7) == (1, 3, 40, -17, 7)
    for a, b in itertools.product(range(-8, 9), repeat=2):
        g, x, y = extended_gcd(a, b)
        assert g == math.gcd(a, b) == a * x + b * y
    n = 1606938044258990275551518141370982378356229797292067198570519
    result = fermat_factors(n, max_steps=2)
    assert (result.steps, result.lower, result.upper) == (
        1,
        1267650600228229401499935529979,
        1267650600228229401501009274261,
    )
    assert result.lower * result.upper == n
    with pytest.raises(TimeoutError):
        fermat_factors(101, max_steps=2)
    i, prime = congruent_prime(10, 8)
    assert prime >= 128 and prime == 10 * i + 1 and is_prime(prime)
    assert modular_inverse(3, 11) == 4


def test_residue_orbits():
    ring = ModularRing(11)
    assert [ring(i).order for i in range(1, 11)] == [1, 10, 5, 5, 5, 10, 10, 10, 5, 2]
    assert (ring(-1) + ring(2)).value == 1
    assert (ring(3) * ring(3).inverse()).value == 1
    assert ModularRing(8)(2).powers == frozenset(ModularRing(8)(i) for i in (1, 2, 4, 0))
    assert ring.addition_table[7][9] == 5
    assert ring.multiplication_table[7][9] == 8
