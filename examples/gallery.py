"""Rebuild the visual gallery using the ultracomplex engine.

Run from the repository root after installing .[plot]:
    python examples/gallery.py
    python examples/gallery.py --quick --output /tmp/ultra-gallery

NumPy arranges samples and Matplotlib draws them. Every function evaluation,
Newton step and sensitivity comes from ultracomplexmath, not a second algebra.
"""

from __future__ import annotations

import argparse
import cmath
import io
import json
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation, PillowWriter
from matplotlib.collections import LineCollection
from matplotlib.colors import to_rgb
from mpl_toolkits.mplot3d.art3d import Line3DCollection
from PIL import Image

from ultracomplexmath import EPS, ONE, Binary, Complex, Dual, I, J, Ultra
from ultracomplexmath.geometry import vector_from_angle

BG = "#090e1d"
PANEL = "#10192b"
FG = "#ecf0ff"
MUTED = "#99aac8"
CYAN = "#59e0df"
PURPLE = "#b795ff"
GOLD = "#ffcf7b"
PINK = "#ff7ba8"
COLORS = [CYAN, PURPLE, GOLD, PINK, "#75b3ff", "#b8ed9a", "#ef9bff", "#ff997b"]
LABELS = ["1", "j", "i", "ij", "ε", "εj", "εi", "εij"]
ROOTS = tuple(cmath.exp(2j * math.pi * k / 3) for k in range(3))
BASIN_COLORS = np.array(
    [
        to_rgb(c)
        for c in [
            "#ffd580",
            "#ff816b",
            "#e65baf",
            "#ad95ff",
            "#787dec",
            "#50b5ff",
            "#58e2dc",
            "#94cf83",
            "#e9ecaf",
        ]
    ]
)
OMEGA = 1.8
COUPLING = 0.36


def configure():
    plt.rcParams.update(
        {
            "figure.facecolor": BG,
            "axes.facecolor": PANEL,
            "savefig.facecolor": BG,
            "text.color": FG,
            "axes.labelcolor": MUTED,
            "xtick.color": MUTED,
            "ytick.color": MUTED,
            "axes.edgecolor": "#29354d",
            "grid.color": "#394861",
            "font.family": "DejaVu Sans",
            "font.size": 10,
            "axes.titlesize": 14,
            "axes.titleweight": "bold",
        }
    )


def title(fig, number, heading, subtitle):
    fig.text(
        0.045, 0.949, f"ULTRACOMPLEX MATH   /   {number}", fontsize=9, color=CYAN, weight="bold"
    )
    fig.text(0.045, 0.891, heading, fontsize=25, weight="bold")
    fig.text(0.045, 0.844, subtitle, fontsize=10.5, color=MUTED)


def footer(fig, text):
    fig.text(0.045, 0.035, text, color=MUTED, fontsize=9)
    fig.text(
        0.957, 0.035, "i² = −1   ·   j² = +1   ·   ε² = 0", ha="right", color=MUTED, fontsize=9
    )


def clean(ax):
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(alpha=0.26, linewidth=0.65)


def save(fig, path):
    raw = io.BytesIO()
    fig.savefig(raw, format="png", dpi=135)
    plt.close(fig)
    raw.seek(0)
    encoded = io.BytesIO()
    with Image.open(raw) as im:
        im.convert("RGB").save(encoded, format="PNG", optimize=True)
    path.write_bytes(encoded.getvalue())
    with Image.open(path) as im:
        im.verify()
    print(f"Rendered {path}", flush=True)


def cosine_grid(kind, resolution=320, half_range=math.pi):
    """Return the two real output coefficients, using Ultra.cos at every pixel."""
    coordinates = np.linspace(-half_range, half_range, resolution)
    component = {Complex: 2, Binary: 1, Dual: 4}[kind]
    result = np.empty((resolution, resolution, 2))
    for row, y in enumerate(coordinates):
        for col, x in enumerate(coordinates):
            value = kind(float(x), float(y)).to_ultra().cos()
            result[row, col] = value.real, value.coefficients[component]
    return coordinates, result


def coefficient_colors(values):
    """The migrated Java color map: zero is white, large magnitudes get dark."""
    shape = values.shape[:-1] + (3,)
    return (
        np.array([Complex(float(a), float(b)).color() for a, b in values.reshape(-1, 2)]).reshape(
            shape
        )
        / 255
    )


def render_cosine(output, resolution):
    fig, axes = plt.subplots(1, 3, figsize=(14, 6.5))
    fig.subplots_adjust(left=0.065, right=0.975, bottom=0.21, top=0.72, wspace=0.19)
    title(
        fig,
        "01",
        "One cosine. Three different worlds.",
        "The original color map and ±2π input range make growth, periodicity and linearity visible.",
    )
    names = ["COMPLEX  /  i² = −1", "SPLIT-COMPLEX  /  j² = +1", "DUAL  /  ε² = 0"]
    identities = [
        "cos x cosh y − i sin x sinh y",
        "cos x cos y − j sin x sin y",
        "cos x − ε y sin x",
    ]
    for ax, kind, name, identity in zip(
        axes, [Complex, Binary, Dual], names, identities, strict=True
    ):
        _, values = cosine_grid(kind, resolution, half_range=math.tau)
        ax.imshow(
            coefficient_colors(values),
            extent=(-math.tau, math.tau, -math.tau, math.tau),
            origin="lower",
            interpolation="nearest",
        )
        ax.set_title(name, loc="left", fontsize=11, pad=12)
        ax.set_xticks([-math.tau, 0, math.tau], ["−2π", "0", "2π"])
        ax.set_yticks([-math.tau, 0, math.tau], ["−2π", "0", "2π"])
        ax.set_xlabel("real input x", fontsize=9)
        ax.set_ylabel("generator input y", fontsize=9)
        ax.text(0.5, -0.29, identity, transform=ax.transAxes, ha="center", color=FG, fontsize=10)
    footer(
        fig,
        "Original Java colors · white = zero · darker = larger magnitude · no added contour bands",
    )
    save(fig, output / "assets/cosine-atlas.png")


def render_euler(output):
    fig, axes = plt.subplots(1, 3, figsize=(14, 6.5))
    fig.subplots_adjust(left=0.07, right=0.97, bottom=0.18, top=0.71, wspace=0.32)
    title(
        fig,
        "02",
        "Rotation. Stretch. Tangent.",
        "Three Euler exponentials, evaluated by the same eight-dimensional number type.",
    )
    for ax, unit, index, color, name, formula, bounds in zip(
        axes,
        [I, J, EPS],
        [2, 1, 4],
        [CYAN, PURPLE, GOLD],
        ["Circular", "Hyperbolic", "Nilpotent"],
        ["exp(t i) = cos t + i sin t", "exp(t j) = cosh t + j sinh t", "exp(t ε) = 1 + t ε"],
        [(-math.pi, math.pi), (-1.65, 1.65), (-2.3, 2.3)],
        strict=True,
    ):
        values = [(float(t) * unit).exp() for t in np.linspace(*bounds, 601)]
        x = [v.real for v in values]
        y = [v.coefficients[index] for v in values]
        for width, alpha in [(13, 0.04), (7, 0.10), (2.8, 1)]:
            ax.plot(x, y, color=color, lw=width, alpha=alpha)
        for t in [-1.2, 0, 1.2]:
            point = (t * unit).exp()
            ax.scatter(point.real, point.coefficients[index], c=FG, s=20, zorder=3)
        ax.axhline(0, color=MUTED, lw=0.6, alpha=0.4)
        ax.axvline(0, color=MUTED, lw=0.6, alpha=0.4)
        ax.set_title(name, loc="left", color=color, pad=12)
        ax.set_xlabel("real coefficient")
        ax.set_ylabel("generator coefficient")
        ax.set_aspect("equal", adjustable="datalim")
        ax.text(0.5, -0.20, formula, transform=ax.transAxes, ha="center", fontsize=10)
        clean(ax)
    footer(
        fig,
        "The geometry follows from the generator square; there is no special-case plotting algebra.",
    )
    save(fig, output / "assets/euler-triptych.png")


def angle_surface(kind, a_values, b_values):
    return np.array(
        [[vector_from_angle(kind(float(a), float(b))) for a in a_values] for b in b_values]
    )


def render_angles(output):
    fig = plt.figure(figsize=(14, 6.5))
    title(
        fig,
        "03",
        "A family of hypercomplex angles.",
        "The hypercomplex angle map turns one coordinate construction into a sphere, cylinder or hyperboloid.",
    )
    for k, kind, color, name, formula, bmax in zip(
        range(3),
        [Binary, Dual, Complex],
        [CYAN, PURPLE, GOLD],
        ["SPHERE  /  binary angle", "CYLINDER  /  dual angle", "HYPERBOLOID  /  complex angle"],
        ["x² + y² + z² = 1", "x² + y² = 1", "x² + y² − z² = 1"],
        [math.pi / 2, 1.45, 1.15],
        strict=True,
    ):
        ax = fig.add_axes(
            (0.015 + k * 0.327, 0.14, 0.323, 0.58), projection="3d", computed_zorder=False
        )
        surface = angle_surface(kind, np.linspace(0, math.tau, 91), np.linspace(-bmax, bmax, 45))
        ax.plot_surface(
            *np.moveaxis(surface, -1, 0),
            color=color,
            alpha=0.11,
            linewidth=0,
            shade=False,
            rcount=45,
            ccount=91,
        )
        ax.plot_wireframe(
            *np.moveaxis(surface, -1, 0),
            rstride=4,
            cstride=6,
            color=color,
            alpha=0.38,
            linewidth=0.6,
        )
        t = np.linspace(0, math.tau, 800)
        path = np.array(
            [vector_from_angle(kind(float(a), float(0.72 * bmax * math.sin(3 * a)))) for a in t]
        )
        ax.plot(*path.T, color=FG, lw=2.1, zorder=5)
        ax.scatter(*path[110], color=GOLD, s=35, depthshade=False, zorder=6)
        ax.view_init(22, -54)
        ax.set_box_aspect((1, 1, 1))
        ax.set_axis_off()
        ax.set_facecolor(BG)
        ax.text2D(
            0.5,
            1.015,
            name,
            transform=ax.transAxes,
            ha="center",
            fontsize=10,
            weight="bold",
            color=color,
        )
        ax.text2D(0.5, -0.04, formula, transform=ax.transAxes, ha="center", fontsize=13)
    footer(
        fig,
        "White curves: a varying hypercomplex angle · wireframes: coordinate lines · independent panel scales",
    )
    save(fig, output / "assets/angle-surfaces.png")


def coupled_state(t, coupling=COUPLING):
    """Z=z1+j*z2+eps*(d_k z1+j*d_k z2), Z(0)=1, with real k.

    d_t Z = i*(omega+j*k)*Z. Seeding k with k+eps differentiates the
    complete exponential exactly in the algebra (up to floating point).
    """
    generator = I * (OMEGA + J * (float(coupling) + EPS))
    return (float(t) * generator).exp()


def coupled_samples(times, coupling=COUPLING):
    return np.array([coupled_state(t, coupling).coefficients for t in times])


def unpack(samples):
    return (
        samples[:, 0] + 1j * samples[:, 2],
        samples[:, 1] + 1j * samples[:, 3],
        samples[:, 4] + 1j * samples[:, 6],
        samples[:, 5] + 1j * samples[:, 7],
    )


def colored_path(ax, x, y, color, width=2):
    ax.plot(x, y, lw=width * 5, color=color, alpha=0.045)
    ax.plot(x, y, lw=width * 2.5, color=color, alpha=0.07)
    points = np.column_stack((x, y)).reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)
    rgba = np.tile((*to_rgb(color), 1), (len(segments), 1))
    rgba[:, 3] = np.linspace(0.12, 1, len(segments))
    ax.add_collection(LineCollection(segments, colors=rgba, linewidths=width))
    ax.autoscale_view()


def render_coupling(output):
    times = np.linspace(0, 18, 901)
    samples = coupled_samples(times)
    z1, z2, d1, d2 = unpack(samples)
    fig = plt.figure(figsize=(14, 8.7))
    title(
        fig,
        "04",
        "Eight coefficients. A useful calculation.",
        "Two coupled complex modes + their exact first-order sensitivity to coupling κ, in one exponential.",
    )
    axes = [fig.add_axes((0.065, 0.44, 0.255, 0.34)), fig.add_axes((0.385, 0.44, 0.255, 0.34))]
    for ax, z, derivative, color, name in zip(
        axes, [z1, z2], [d1, d2], [CYAN, PURPLE], ["MODE 1", "MODE 2"], strict=True
    ):
        colored_path(ax, z.real, z.imag, color)
        chosen = np.arange(70, 850, 100)
        ax.quiver(
            z.real[chosen],
            z.imag[chosen],
            0.04 * derivative.real[chosen],
            0.04 * derivative.imag[chosen],
            color=GOLD,
            angles="xy",
            scale_units="xy",
            scale=1,
            width=0.006,
            headwidth=4,
        )
        ax.set(xlim=(-1.28, 1.28), ylim=(-1.28, 1.28), xlabel="real", ylabel="imaginary")
        ax.set_aspect("equal")
        ax.set_title(name, color=color, loc="left", fontsize=11)
        clean(ax)
    fig.text(0.708, 0.747, "ONE ULTRACOMPLEX EXPONENTIAL", color=GOLD, fontsize=10, weight="bold")
    fig.text(0.708, 0.687, "Z(t) = exp[i (ω + j (κ + ε)) t]", fontsize=15)
    fig.text(
        0.708,
        0.633,
        "1, i     →  complex mode z₁\nj, ij    →  complex mode z₂\nε, εi    →  ∂z₁ / ∂κ\nεj, εij  →  ∂z₂ / ∂κ",
        fontsize=12,
        linespacing=1.9,
        color=MUTED,
        va="top",
    )
    fig.text(
        0.708,
        0.467,
        "Gold arrows: 0.04 × sensitivity\nω = 1.8    κ = 0.36\nNo finite-difference step is used.",
        fontsize=10,
        linespacing=1.6,
        color=MUTED,
        va="top",
    )
    ax = fig.add_axes((0.07, 0.15, 0.39, 0.20))
    ax.fill_between(times, abs(z1) ** 2, color=CYAN, alpha=0.12)
    ax.plot(times, abs(z1) ** 2, c=CYAN, lw=2, label="|z₁|²")
    ax.plot(times, abs(z2) ** 2, c=PURPLE, lw=2, label="|z₂|²")
    ax.set(xlim=(0, 18), ylim=(-0.04, 1.04), xlabel="time t", ylabel="modal intensity")
    ax.set_title("Lossless exchange: |z₁|² + |z₂|² = 1", loc="left", fontsize=11)
    ax.legend(frameon=False, loc="upper right", ncols=2, labelcolor=FG)
    clean(ax)
    ax = fig.add_axes((0.565, 0.15, 0.39, 0.20))
    delta = 0.015
    actual = unpack(coupled_samples(times, COUPLING + delta))[0]
    ax.plot(times, abs(actual - z1), c=PURPLE, lw=2, label="actual change")
    ax.plot(times, abs(actual - (z1 + delta * d1)), c=GOLD, lw=2, label="linear prediction error")
    ax.set(xlim=(0, 18), xlabel="time t", ylabel="complex error magnitude")
    ax.set_title("Predicting a change Δκ = 0.015", loc="left", fontsize=11)
    ax.legend(frameon=False, fontsize=9, labelcolor=FG)
    clean(ax)
    footer(
        fig,
        "A finite parameter change is approximated to first order; the derivative itself is algebraic.",
    )
    save(fig, output / "assets/coupled-sensitivity.png")
    return times, samples


def render_flow(output, times, samples):
    fig = plt.figure(figsize=(14, 8))
    title(
        fig,
        "05",
        "A trace through eight dimensions.",
        "The same coupled-mode solution: a three-coordinate projection above, every real coefficient below.",
    )
    ax = fig.add_axes((0.02, 0.31, 0.57, 0.48), projection="3d")
    # Show an explicitly labelled three-coordinate projection of the eight coefficients.
    points = np.column_stack((samples[:, 0], samples[:, 2], samples[:, 1]))
    segments = np.stack([points[:-1], points[1:]], axis=1)
    collection = Line3DCollection(segments, cmap="cool", linewidth=2.1)
    collection.set_array(times[:-1])
    ax.add_collection3d(collection)
    ax.set(xlim=(-1.1, 1.1), ylim=(-1.1, 1.1), zlim=(-1.1, 1.1))
    ax.set_xlabel("coefficient of 1", labelpad=5, fontsize=9)
    ax.set_ylabel("coefficient of i", labelpad=5, fontsize=9)
    ax.set_zlabel("coefficient of j", labelpad=5, fontsize=9)
    ax.view_init(24, -51)
    ax.set_facecolor(BG)
    for axis in [ax.xaxis, ax.yaxis, ax.zaxis]:
        axis.set_pane_color((*to_rgb(BG), 0))
        axis._axinfo["grid"]["color"] = (*to_rgb(MUTED), 0.16)
    ax.tick_params(labelsize=8)
    fig.text(0.63, 0.73, "FOUR STATE COEFFICIENTS", fontsize=11, color=CYAN, weight="bold")
    fig.text(
        0.63,
        0.70,
        "Two complex amplitudes exchange intensity.\nTheir real coefficients stay bounded.",
        fontsize=11,
        color=MUTED,
        linespacing=1.6,
        va="top",
    )
    fig.text(0.63, 0.565, "FOUR DERIVATIVE COEFFICIENTS", fontsize=11, color=GOLD, weight="bold")
    fig.text(
        0.63,
        0.54,
        "The ε coefficients measure sensitivity.\nThey can grow while the motion stays stable:\nphase uncertainty accumulates over time.",
        fontsize=11,
        color=MUTED,
        linespacing=1.6,
        va="top",
    )
    for k in range(8):
        col, row = k % 4, k // 4
        axis = fig.add_axes((0.068 + col * 0.237, 0.195 - row * 0.113, 0.199, 0.085))
        axis.plot(times, samples[:, k], lw=1.35, c=COLORS[k])
        axis.axhline(0, color=MUTED, alpha=0.2, lw=0.5)
        axis.set(xlim=(0, 18))
        axis.text(
            0.025,
            0.84,
            LABELS[k],
            color=COLORS[k],
            transform=axis.transAxes,
            fontsize=12,
            weight="bold",
        )
        axis.tick_params(labelsize=7, length=2)
        if row == 0:
            axis.set_xticklabels([])
        clean(axis)
    footer(
        fig, "Projection uses coefficients (1, i, j) · each small plot has its own vertical scale"
    )
    save(fig, output / "assets/eight-dimensional-flow.png")


def newton_point(value, iterations=45, tolerance=1e-9):
    """Full Ultra Newton iteration; reject singular or unresolved points explicitly."""
    for iteration in range(iterations + 1):
        try:
            square = value * value
            residual = square * value - ONE
            if abs(residual) < tolerance:
                plus, minus = value.channels()
                a = min(range(3), key=lambda k: abs(plus[0] - ROOTS[k]))
                b = min(range(3), key=lambda k: abs(minus[0] - ROOTS[k]))
                return 3 * a + b, iteration, value
            if iteration == iterations:
                break
            value = value - residual / (3 * square)
        except (ArithmeticError, ValueError):
            break
    return -1, iterations, None


def newton_grid(resolution=320, progress=False):
    coordinates = np.linspace(-1.8, 1.8, resolution)
    labels = np.empty((resolution, resolution), dtype=int)
    steps = np.empty_like(labels)
    for row, y in enumerate(coordinates):
        for col, x in enumerate(coordinates):
            seed = Ultra(real=float(x), j=0.27, i=float(y), ij=0.20, eps=1)
            label, count, _ = newton_point(seed)
            labels[row, col], steps[row, col] = label, count
        if progress and row % 40 == 0:
            print(f"Newton basins: {row + 1}/{resolution} rows", flush=True)
    return coordinates, labels, steps


def render_newton(output, resolution):
    _, labels, steps = newton_grid(resolution, progress=True)
    brightness = 0.36 + 0.64 * np.exp(-0.065 * np.maximum(steps - 5, 0))
    rgb = BASIN_COLORS[np.maximum(labels, 0)] * brightness[..., None]
    rgb[labels < 0] = to_rgb(BG)
    fig = plt.figure(figsize=(14, 9))
    title(
        fig,
        "06",
        "A cubic with nine roots.",
        "Newton's method in the full algebra. Each pixel starts at x + 0.27 j + y i + 0.20 ij + ε.",
    )
    ax = fig.add_axes((0.055, 0.13, 0.57, 0.65))
    ax.imshow(rgb, extent=(-1.8, 1.8, -1.8, 1.8), origin="lower", interpolation="nearest")
    ax.set(xlabel="real starting coefficient x", ylabel="imaginary starting coefficient y")
    ax.tick_params(labelsize=9)
    fig.text(0.67, 0.73, "X³ = 1", fontsize=34, color=GOLD)
    fig.text(
        0.67,
        0.665,
        "Three roots per complex channel.\nIndependent choices give 3 × 3 = 9.",
        fontsize=11,
        color=MUTED,
        linespacing=1.7,
    )
    key = fig.add_axes((0.693, 0.40, 0.17, 0.17))
    key.imshow(BASIN_COLORS.reshape(3, 3, 3), origin="upper")
    key.set_xticks([0, 1, 2], ["0", "1", "2"])
    key.set_yticks([0, 1, 2], ["0", "1", "2"])
    key.set_xlabel("root in − channel", fontsize=9)
    key.set_ylabel("root in + channel", fontsize=9)
    for a in range(3):
        for b in range(3):
            key.text(
                b, a, f"{a},{b}", ha="center", va="center", color=BG, fontsize=10, weight="bold"
            )
    found = len(set(labels.ravel()) - {-1})
    unresolved = int(np.count_nonzero(labels < 0))
    fig.text(
        0.67,
        0.31,
        "Brightness encodes convergence speed.\nDark pixels: unresolved after 45 steps.\nThe nilpotent coefficients converge to zero.",
        fontsize=10,
        linespacing=1.8,
        color=MUTED,
        va="top",
    )
    fig.text(
        0.67,
        0.175,
        f"{resolution:,} × {resolution:,} full Ultra calculations\n{found} basins found · {unresolved} unresolved pixels",
        fontsize=10,
        linespacing=1.7,
        color=FG,
    )
    footer(fig, "A 2D slice of an 8D iteration · the two complex channels explain the pattern")
    save(fig, output / "assets/newton-nine-roots.png")
    return {"resolution": resolution, "basins_found": found, "unresolved": unresolved}


def render_animation(output, frames=90):
    times = np.linspace(0, math.tau / COUPLING, 721)
    z1, z2, _, _ = unpack(coupled_samples(times))
    fig = plt.figure(figsize=(9.6, 5.6))
    fig.text(
        0.065,
        0.91,
        "TWO MODES · ONE ULTRACOMPLEX EXPONENTIAL",
        fontsize=14,
        weight="bold",
        color=FG,
    )
    fig.text(
        0.065,
        0.85,
        "Z(t) = exp[i (ω + j (κ + ε)) t]     ·     ε stores the coupling sensitivity",
        fontsize=10,
        color=MUTED,
    )
    axes = [fig.add_axes((0.07, 0.32, 0.34, 0.47)), fig.add_axes((0.57, 0.32, 0.34, 0.47))]
    moving = []
    for ax, z, color, name in zip(
        axes, [z1, z2], [CYAN, PURPLE], ["MODE 1", "MODE 2"], strict=True
    ):
        ax.plot(z.real, z.imag, color=color, alpha=0.17, lw=1)
        (line,) = ax.plot([], [], color=color, lw=2.5)
        (dot,) = ax.plot([], [], "o", color=FG, markersize=6)
        ax.set(xlim=(-1.15, 1.15), ylim=(-1.15, 1.15))
        ax.set_aspect("equal")
        ax.set_title(name, color=color, fontsize=10)
        ax.set_xticks([-1, 0, 1])
        ax.set_yticks([-1, 0, 1])
        clean(ax)
        moving.append((line, dot, z))
    ax = fig.add_axes((0.10, 0.13, 0.8, 0.055))
    ax.set(xlim=(0, 1), ylim=(0, 1))
    ax.set_axis_off()
    first = ax.barh(0.5, 1, height=0.7, color=CYAN)[0]
    second = ax.barh(0.5, 0, left=1, height=0.7, color=PURPLE)[0]
    label = fig.text(0.5, 0.065, "", ha="center", fontsize=10, color=MUTED)

    def update(frame):
        index = int(frame * (len(times) - 1) / frames)
        for line, dot, z in moving:
            start = max(0, index - 95)
            line.set_data(z.real[start : index + 1], z.imag[start : index + 1])
            dot.set_data([z.real[index]], [z.imag[index]])
        energy = abs(z1[index]) ** 2
        first.set_width(energy)
        second.set_x(energy)
        second.set_width(1 - energy)
        label.set_text(
            f"t = {times[index]:05.2f}     |z₁|² = {energy:.3f}     |z₂|² = {1 - energy:.3f}     total = 1"
        )
        return [label, first, second, *(item for pair in moving for item in pair[:2])]

    animation = FuncAnimation(fig, update, frames=frames, interval=1000 / 18, blit=False)
    animation.save(output / "assets/coupled-modes.gif", writer=PillowWriter(fps=18), dpi=95)
    plt.close(fig)
    print("Rendered coupled-modes.gif", flush=True)


def render_lab(output):
    times = np.linspace(0, 18, 241)
    couplings = np.linspace(0.10, 0.90, 21)
    data = {
        "times": np.round(times, 8).tolist(),
        "couplings": np.round(couplings, 8).tolist(),
        "omega": OMEGA,
        "samples": [np.round(coupled_samples(times, float(k)), 8).tolist() for k in couplings],
    }
    template = Path(__file__).with_name("gallery_lab.html").read_text()
    html = template.replace("/*__ULTRA_DATA__*/", json.dumps(data, separators=(",", ":")))
    (output / "lab.html").write_text(html)
    print("Rendered standalone lab.html", flush=True)


def verify_math():
    """Independent closed formulas, invariants and a finite-change convergence check."""
    times = np.linspace(0, 18, 51)
    z1, z2, d1, d2 = unpack(coupled_samples(times))
    carrier = np.exp(1j * OMEGA * times)
    references = [
        carrier * np.cos(COUPLING * times),
        1j * carrier * np.sin(COUPLING * times),
        -times * carrier * np.sin(COUPLING * times),
        1j * times * carrier * np.cos(COUPLING * times),
    ]
    error = max(
        float(np.max(abs(actual - expected)))
        for actual, expected in zip([z1, z2, d1, d2], references, strict=True)
    )
    conservation_error = float(np.max(abs(abs(z1) ** 2 + abs(z2) ** 2 - 1)))
    residuals = [abs(Ultra.from_channels((a, 0), (b, 0)) ** 3 - ONE) for a in ROOTS for b in ROOTS]
    errors = []
    for delta in [0.004, 0.002]:
        perturbed = unpack(coupled_samples(times, COUPLING + delta))[0]
        errors.append(float(np.max(abs(perturbed - z1 - delta * d1))))
    assert error < 1e-11
    assert conservation_error < 1e-12
    assert max(residuals) < 1e-12
    assert 3.8 < errors[0] / errors[1] < 4.2
    return {
        "closed_form_max_error": error,
        "intensity_conservation_max_error": conservation_error,
        "nine_roots_max_residual": max(residuals),
        "linearization_error_ratio_when_delta_halves": errors[0] / errors[1],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("docs/gallery"))
    parser.add_argument(
        "--quick", action="store_true", help="smaller grids and a shorter animation"
    )
    parser.add_argument(
        "--only",
        choices=["cosine", "euler", "angles", "coupling", "newton", "animation", "lab", "all"],
        default="all",
    )
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "assets").mkdir(exist_ok=True)
    configure()
    report = verify_math()
    functions = {
        "cosine": lambda: render_cosine(args.output, 96 if args.quick else 360),
        "euler": lambda: render_euler(args.output),
        "angles": lambda: render_angles(args.output),
        "newton": lambda: report.update(
            newton=render_newton(args.output, 64 if args.quick else 360)
        ),
        "animation": lambda: render_animation(args.output, 24 if args.quick else 90),
        "lab": lambda: render_lab(args.output),
    }
    if args.only in ("all", "coupling"):
        times, samples = render_coupling(args.output)
        render_flow(args.output, times, samples)
    for name, function in functions.items():
        if args.only in ("all", name):
            function()
    if args.only == "all":
        (args.output / "verification.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2), flush=True)


if __name__ == "__main__":
    main()
