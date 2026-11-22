import pytest

from ultracomplexmath import EPS, ONE, I, J, SingularSystemError, Ultra, solve


def test_real_system_with_pivoting():
    assert solve([[0, 2], [1, 3]], [4, 7]) == (ONE, Ultra(2))


def test_full_algebra_system_and_residual():
    a = [[2 + I + EPS, 0.2 * J], [I * EPS, 3 - I + J + 2 * EPS]]
    expected = [Ultra(2, 3, 5, 7, 11, 13, 17, 19), Ultra(1, -2, -3, 2, -1, 4, 5, 2)]
    b = [sum(x * y for x, y in zip(row, expected, strict=True)) for row in a]
    x = solve(a, b)
    for actual, wanted in zip(x, expected, strict=True):
        assert actual.isclose(wanted)
    for row, value in zip(a, b, strict=True):
        assert sum((c * v for c, v in zip(row, x, strict=True)), Ultra()).isclose(value)


def test_every_entry_can_be_a_zero_divisor():
    p, m = (ONE + J) / 2, (ONE - J) / 2
    assert not p.is_invertible and not m.is_invertible
    assert solve([[p, m], [m, p]], [2 * p + 3 * m, 2 * m + 3 * p]) == (Ultra(2), Ultra(3))


def test_dual_linear_system_differentiates_solution():
    assert solve([[2 + EPS]], [4 + 3 * EPS]) == (2 + 0.5 * EPS,)


def test_small_scaled_rows_remain_solvable():
    assert solve([[1e-100, 0], [0, 1e100]], [2e-100, 3e100]) == (Ultra(2), Ultra(3))


@pytest.mark.parametrize(
    "a,b", [([[0]], [1]), ([[EPS]], [1]), ([[ONE + J]], [1]), ([[1, 2], [2, 4]], [1, 2])]
)
def test_singular_system(a, b):
    with pytest.raises(SingularSystemError):
        solve(a, b)


@pytest.mark.parametrize("a,b", [([], []), ([[1, 2]], [1]), ([[1]], [1, 2])])
def test_invalid_dimensions(a, b):
    with pytest.raises(ValueError):
        solve(a, b)
