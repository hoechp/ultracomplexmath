import pytest

from examples.moment_ranks import moment_band_rank, third_power_band_rank
from examples.novelty_models import interval_band_rank, second_power_band_rank
from tools.novelty_probe import higher_power_probe


def test_independent_higher_power_references():
    counts = higher_power_probe()
    assert all(counts["jordan_blocks_by_power"].values())
    assert (
        counts["deliberately_deficient_windows"] > 0
        and counts["independent_full_tensor_powers"] > 0
    )


def test_specializations_and_degree_zero():
    for d in range(4):
        for r in range(1, 7):
            for q in range(1, 7):
                for p, special in [
                    (1, interval_band_rank),
                    (2, second_power_band_rank),
                    (3, third_power_band_rank),
                ]:
                    for c in range(p * d + 1):
                        if 0 <= q + c - r <= p * d:
                            assert moment_band_rank(r, q, d, p, c) == special(r, q, d, c)
    assert moment_band_rank(9, 9, 0, 13, 0) == 9


def test_cubic_collinearity_and_large_parameters():
    # Three pairs collinear, and three pairs not collinear.
    assert third_power_band_rank(4, 4, 3, 2) == 3
    assert third_power_band_rank(1, 1, 2, 0) == 1
    assert third_power_band_rank(4, 4, 4, 1) == 3
    size = 10**30
    assert moment_band_rank(size, size, 10**20, 5, 0) == size
    # A massive square samples a single polynomial piece of degree six.
    assert moment_band_rank(size, size, 2 * size, 7, size) == 7


@pytest.mark.parametrize(
    "args,exc",
    [
        ((1, 1, 1, 0, 0), ValueError),
        ((1, 1, -1, 2, 0), ValueError),
        ((False, 1, 1, 1, 1), TypeError),
        ((1, 1, 1, True, 0), TypeError),
        ((1, 4, 1, 1, 1), ValueError),
    ],
)
def test_window_domain(args, exc):
    with pytest.raises(exc):
        moment_band_rank(*args)
