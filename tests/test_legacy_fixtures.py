"""Compare preserved arithmetic against actual captured Java executions."""

import json
from pathlib import Path

import pytest

from ultracomplexmath import Ultra

CAPTURE = json.loads(
    (Path(__file__).resolve().parents[1] / "tests/fixtures/legacy-results.json").read_text()
)
BASELINE = "954c19190ea862ee93e5e1a18295cc15f69649dd"


@pytest.mark.parametrize("a", range(8))
@pytest.mark.parametrize("b", range(8))
def test_basis_agrees_with_captured_java(a, b):
    assert CAPTURE["source_commit"] == BASELINE
    expected = Ultra(*CAPTURE["cases"][f"basis_{a}_{b}"])
    assert Ultra.unit(a) * Ultra.unit(b) == expected


def test_full_addition_and_multiplication_agree_with_java():
    a, b = Ultra(2, 3, 5, 7, 11, 13, 17, 19), Ultra(3, 5, 7, 11, 13, 17, 19, 2)
    assert a + b == Ultra(*CAPTURE["cases"]["addition"])
    assert a * b == Ultra(*CAPTURE["cases"]["multiplication"])
