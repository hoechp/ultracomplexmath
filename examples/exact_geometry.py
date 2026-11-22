"""Exact circular/hyperbolic/parabolic geometry and their coupled extension.

python -m examples.exact_geometry
python -m examples.exact_geometry --plot

All constructions and invariant checks use Fraction. Matplotlib is optional;
conversion to float occurs only at the plotting boundary.
"""

from __future__ import annotations

import argparse
import json
from fractions import Fraction as F
from pathlib import Path

from ultracomplexmath import (
    CIRCULAR,
    HYPERBOLIC,
    PARABOLIC,
    QEPS,
    QI,
    QJ,
    QONE,
    QZERO,
    ExactUltra,
    Mobius,
    ModeOperator,
    PlaneIsometry,
    ProjectivePoint,
    cross_ratio,
    evaluate_exact,
    line_intersection2d,
    orientation2d,
)


def demonstrate():
    factors = [plane.cayley(F(1, 2)) for plane in (CIRCULAR, HYPERBOLIC, PARABOLIC)]
    assert all(factor.determinant == 1 for factor in factors)
    transformations = [PlaneIsometry(factor, type(factor)(F(1, 3), F(2, 7))) for factor in factors]
    for transform in transformations:
        point = type(transform.factor)(2, 3)
        assert transform.inverse()(transform(point)) == point

    # The full product retains circular, split and infinitesimal mixed directions.
    deformation = (QONE + QI + QJ + QI * QJ) / 7
    combined = factors[0].to_ultra() * factors[1].to_ultra() * (QONE + QEPS * deformation)
    assert combined * combined.inverse() == QONE
    assert all(combined.coefficients)

    # A rational motion law stays regular while kappa crosses zero.
    generator = ModeOperator.from_matrix(QZERO, QONE, QEPS, QZERO)
    critical_map = generator.cayley(ExactUltra(F(1, 3)))
    assert critical_map.matrix()[0][0] == QONE + F(2, 9) * QEPS
    assert critical_map.matrix()[0][1] == F(2, 3) * QONE + F(2, 27) * QEPS

    projectivity = Mobius(2 * QONE, QONE + QEPS, QONE, 3 * QONE)
    points = [ExactUltra(n) + QI / 3 + QJ / 7 for n in (0, 1, 2, 3)]
    assert cross_ratio(*(projectivity(p) for p in points)) == cross_ratio(*points)
    plus, minus = (QONE + QJ) / 2, (QONE - QJ) / 2
    boundary = ProjectivePoint(plus, minus)
    assert boundary.charts == ("x", "y")

    origin = 10**100
    signed_area = orientation2d(
        (origin, origin), (origin + 1, origin + 1), (origin + 2, origin + 2 + F(1, 10**100))
    )
    assert signed_area > 0
    assert evaluate_exact("0.1 + 0.2 - 0.3") == QZERO
    return {
        "coefficient_domain": "Fraction; no floating intermediates",
        "circular_factor": str(factors[0]),
        "hyperbolic_factor": str(factors[1]),
        "parabolic_factor": str(factors[2]),
        "combined_eight_components": [str(x) for x in combined],
        "critical_map_00": str(critical_map.matrix()[0][0]),
        "critical_map_01": str(critical_map.matrix()[0][1]),
        "projective_boundary_charts": boundary.charts,
        "line_intersection": [str(x) for x in line_intersection2d((0, 0), (3, 2), (1, 0), (0, 1))],
        "tiny_signed_area_after_huge_translation": str(signed_area),
        "all_exact_checks_passed": True,
    }


def plot(output: Path):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    colors = ("#2166ac", "#d97421", "#22865a")
    fig, axes = plt.subplots(2, 2, figsize=(11, 8.3), layout="constrained")
    fig.suptitle("One rational construction, three geometries", fontsize=20, fontweight="bold")
    for ax in axes.flat:
        ax.set_facecolor("#f7f9fc")
        ax.axhline(0, color="#bec6d0", linewidth=0.7)
        ax.axvline(0, color="#bec6d0", linewidth=0.7)
        ax.grid(alpha=0.2)
        ax.set_xlabel("x")
        ax.set_ylabel("y")

    for ax, plane, color, title in zip(
        axes.flat,
        (CIRCULAR, HYPERBOLIC, PARABOLIC),
        colors,
        ("Circular: x² + y² = 1", "Hyperbolic: x² − y² = 1", "Parabolic: x² = 1"),
        strict=False,
    ):
        ts = (
            [F(n, 12) for n in range(-48, 49)]
            if plane is CIRCULAR
            else [F(n, 48) for n in range(-36, 37)]
            if plane is HYPERBOLIC
            else [F(n, 12) for n in range(-18, 19)]
        )
        points = [plane.cayley(t) for t in ts]
        if plane is CIRCULAR:
            # The other rational chart fills the arc near the missing -1.
            points += [plane.cayley(t) for t in (F(8), F(16), F(32))]
            points += [plane.exact(-1)]
            points += [plane.cayley(t) for t in (F(-32), F(-16), F(-8))]
            points.append(points[0])
        assert all(p.determinant == 1 for p in points)
        ax.plot(
            [float(p.real) for p in points],
            [float(p.imag) for p in points],
            ".-",
            color=color,
            markersize=3,
            linewidth=1.5,
        )
        if plane is not CIRCULAR:
            ax.plot(
                [-float(p.real) for p in points],
                [-float(p.imag) for p in points],
                ".-",
                color=color,
                markersize=3,
                linewidth=1.5,
            )
        ax.set_title(title, fontsize=13)
        ax.set_aspect("equal", adjustable="box")

    ax = axes[1, 1]
    m = (QONE - QJ) / 2
    for kappa, color in zip((-1, 0, 1), (colors[0], colors[2], colors[1]), strict=True):
        generator = ModeOperator.from_matrix(QZERO, QONE, ExactUltra(kappa), QZERO)
        update = generator.cayley(ExactUltra(F(1, 40)))
        state, path = m, []  # x=0, y=1 in the explicit 2x2 representation.
        for _ in range(31):
            x, y = state.real + state.j, state.real - state.j
            assert y * y - kappa * x * x == 1
            path.append((x, y))
            state = update(state)
        ax.plot(
            [float(x) for x, _ in path],
            [float(y) for _, y in path],
            ".-",
            color=color,
            linewidth=1.5,
            markersize=3,
            label=f"κ = {kappa:+d}",
        )
    ax.set_title("Same rational motion law across κ = 0", fontsize=13)
    ax.legend(frameon=False)
    fig.supxlabel(
        "Exact Fraction constructions; float conversion only for display. Motion uses discrete Cayley steps.",
        fontsize=10,
        color="#475569",
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=160, facecolor="white")
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plot", action="store_true")
    parser.add_argument(
        "--output", type=Path, default=Path("docs/gallery/assets/rational-geometry.png")
    )
    args = parser.parse_args()
    print(json.dumps(demonstrate(), indent=2))
    if args.plot:
        plot(args.output)


if __name__ == "__main__":
    main()
