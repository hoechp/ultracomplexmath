"""Check displayed field observables against ordinary complex wave formulas."""

import cmath
import math

import pytest

pytest.importorskip("matplotlib")
pytest.importorskip("numpy")

from examples.fields import interference_field, surface_fields, wave_samples


@pytest.mark.parametrize("coordinates", [(0.3, 0.7, -0.2, 1.2), (-1, 2, 3, 0)])
def test_two_wave_observables_against_complex_oracle(coordinates):
    x, y, z, t = coordinates
    f = interference_field()
    value = f.at(x, y, z, time=t).value
    for sign, channel in zip((1, -1), value.channels(), strict=True):
        a = math.exp(sign * 0.35) * cmath.exp(
            1j * (1.6 * x + 0.6 * y + 0.4 * z - math.sqrt(3.08) * t + sign * 0.45)
        )
        b = (
            0.8
            * math.exp(-sign * 0.2)
            * cmath.exp(1j * (-0.9 * x + 1.8 * y - 0.5 * z - math.sqrt(4.3) * t - sign * 0.25))
        )
        body, tangent = a + b, -1j * t * (math.sqrt(3.08) * a + math.sqrt(4.3) * b)
        assert channel[0] == pytest.approx(body, abs=2e-14)
        assert channel[1] == pytest.approx(tangent, abs=2e-14)
        measured = value.abs2().channels()[0 if sign == 1 else 1]
        assert measured[0].real == pytest.approx(abs(body) ** 2, abs=2e-14)
        assert measured[1].real == pytest.approx(2 * (body.conjugate() * tangent).real, abs=2e-14)


def test_plotted_samples_and_surface_formulas_use_shipped_contracts():
    axis, images = wave_samples(5)
    value = interference_field().at(float(axis[1]), float(axis[3]), 0, time=1.2).value.abs2()
    assert images[0][1, 3] == value.real + value.j
    assert images[3][1, 3] == value.eps - value.eps_j
    for surface, field in surface_fields():
        assert surface.check_seams(field, samples=5, times=(0, 0.7)).within(atol=1e-8)
