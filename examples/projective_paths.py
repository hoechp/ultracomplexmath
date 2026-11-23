"""Build an offline two-channel projective continuation lab from the public API."""

from __future__ import annotations

import json
from pathlib import Path

from examples.impact_models import MINUS, PLUS
from ultracomplexmath import EPS, ONE, J, ProjectivePoint, Ultra, projective_path

ROOT = Path(__file__).resolve().parents[1]


def pole_point(t: float) -> ProjectivePoint[Ultra]:
    return ProjectivePoint(ONE, t + J + EPS)


def glass_point(slope: float) -> ProjectivePoint[Ultra]:
    """[0.1 : reflected tangential E], air to bare glass, n=1.5.

    The independent variable is tan(incidence angle). Both Fresnel amplitudes
    and their derivatives use this variable. The rationalized p numerator
    makes the Brewster zero explicit at the represented input slope 1.5.
    """
    u = slope + EPS
    n2 = 1.5**2
    a = (n2 + (n2 - 1) * u**2).sqrt()
    rs = (1 - a) / (1 + a)
    rp = (n2 - 1) * (u - 1.5) * (u + 1.5) / (a + n2) ** 2
    return ProjectivePoint(Ultra(0.1), PLUS * rs + MINUS * rp)


def sample_path(point_at, parameters):
    points = [point_at(t) for t in parameters]

    def trace(sequence):
        return [
            [
                [coord.chart, round(coord.value.real, 12), round(coord.tangent.real, 12)]
                for coord in step
            ]
            for step in projective_path(sequence)
        ]

    return {
        "parameters": parameters,
        "forward": trace(points),
        "reverse": trace(reversed(points))[::-1],
    }


def main():
    samples = {
        "pole": sample_path(pole_point, [k / 20 for k in range(-60, 61)]),
        "glass": sample_path(glass_point, [k / 40 for k in range(141)]),
    }
    source = Path(__file__).with_suffix(".html").read_text()
    page = source.replace("__PATHS__", json.dumps(samples, allow_nan=False, separators=(",", ":")))
    (ROOT / "docs/gallery/projective-paths.html").write_text(page)


if __name__ == "__main__":
    main()
