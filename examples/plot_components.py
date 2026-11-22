"""Plot all eight coefficients of an ultracomplex expression."""

import argparse

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from ultracomplexmath import BASIS, Formula


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="components.png")
    parser.add_argument("--expression", default="exp(t*(i+0.3*j+0.4*eps))")
    args = parser.parse_args()
    expression = Formula(args.expression)
    t = [-4 + k * 8 / 400 for k in range(401)]
    values = [expression({"t": x}).coefficients for x in t]
    fig, axes = plt.subplots(4, 2, figsize=(10, 10), sharex=True, layout="constrained")
    for k, axis in enumerate(axes.flat):
        axis.plot(t, [value[k] for value in values], color="#7342b4", linewidth=2)
        axis.set_title(BASIS[k], loc="left", weight="bold")
        axis.axhline(0, color="#b6b6bf", linewidth=0.7)
        axis.grid(alpha=0.15)
        axis.spines[["top", "right"]].set_visible(False)
    for axis in axes[-1]:
        axis.set_xlabel("t")
    fig.suptitle(args.expression, fontsize=16)
    fig.savefig(args.output, dpi=140)
    plt.close(fig)


if __name__ == "__main__":
    main()
