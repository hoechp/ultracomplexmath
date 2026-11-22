"""Plot the three Euler curves without Java applets or a GUI event loop."""

import argparse
import math

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from ultracomplexmath import EPS, I, J


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="euler.png")
    args = parser.parse_args()
    t = [-1.25 + k * 2.5 / 500 for k in range(501)]
    colors = ["#7342b4", "#167e87", "#cf7952"]
    fig, axes = plt.subplots(1, 3, figsize=(12, 4.5), layout="constrained")
    for axis, unit, coefficient, title, color in zip(
        axes,
        [I, J, EPS],
        [2, 1, 4],
        ["Complex · i² = −1", "Split-complex · j² = +1", "Dual · ε² = 0"],
        colors,
        strict=True,
    ):
        values = [(math.pi * x * unit).exp() for x in t]
        axis.plot(
            [x.real for x in values],
            [x.coefficients[coefficient] for x in values],
            color=color,
            linewidth=2.5,
        )
        axis.axhline(0, color="#c9c9d0", linewidth=0.8)
        axis.axvline(0, color="#c9c9d0", linewidth=0.8)
        axis.set(title=title, xlabel="Real coefficient", ylabel="Generator coefficient")
        axis.grid(alpha=0.15)
        if coefficient == 2:
            axis.set_aspect("equal", adjustable="box")
        axis.spines[["top", "right"]].set_visible(False)
    fig.suptitle("One exponential, three geometries", fontsize=18, weight="bold")
    fig.text(0.5, -0.025, "exp(π t u),  −1.25 ≤ t ≤ 1.25", ha="center", fontsize=11)
    fig.savefig(args.output, dpi=160, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    main()
