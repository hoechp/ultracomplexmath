"""Reproducible UltraField figures and optional time-slice animation.

Run: python -m examples.fields [--quick] [--animate] [--output DIRECTORY]
All scalar/field evaluations use the library; NumPy and Matplotlib only arrange
and display samples. The wave speed is a chosen model parameter, not relativity.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation, PillowWriter
from matplotlib.colors import Normalize
from PIL import Image, ImageSequence

from ultracomplexmath import Ultra, UltraField, __version__, mobius_strip, torus

from .gallery import BG, FG, MUTED, configure

WAVE_FORMULA = (
    "exp(i*(1.6*x+0.6*y+0.4*z-(speed+eps)*omega1*t)+j*0.35+i*j*0.45)"
    "+0.8*exp(i*(-0.9*x+1.8*y-0.5*z-(speed+eps)*omega2*t)-j*0.2-i*j*0.25)"
)
TORUS_FORMULA = "exp(i*(2*u-3*v-t)+j*0.3*cos(u)+i*j*0.45*sin(v))*(1+eps*0.2*cos(u+v))"
MOBIUS_FORMULA = "exp(i*(2*u-t)+j*0.8*v*cos(u/2))*(1+eps*v*sin(u/2))"


def interference_field(speed=1.0):
    return UltraField.from_formula(
        WAVE_FORMULA,
        parameters={"speed": speed, "omega1": math.sqrt(3.08), "omega2": math.sqrt(4.3)},
        name="two plane waves",
    )


def surface_fields():
    ring, strip = torus(), mobius_strip()
    return (
        (ring, UltraField.from_formula(TORUS_FORMULA, space=ring.space)),
        (strip, UltraField.from_formula(MOBIUS_FORMULA, space=strip.space)),
    )


def wave_samples(size=121, *, time=1.2, z=0.0):
    axis = np.linspace(-5, 5, size)
    grid = interference_field().map(Ultra.abs2).slice(z=z, t=time).sample({"x": axis, "y": axis})
    a = grid.to_numpy()
    # Each measurement is named explicitly; no coefficient is a space axis.
    return axis, (
        a[..., 0] + a[..., 1],
        a[..., 0] - a[..., 1],
        a[..., 4] + a[..., 5],
        a[..., 4] - a[..., 5],
    )


def save_figure(fig, path):
    fig.savefig(path, dpi=155, facecolor=BG)
    plt.close(fig)
    print(f"Wrote {path}", flush=True)


def plot_waves(output, size):
    _, images = wave_samples(size)
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    fig.subplots_adjust(left=0.07, right=0.93, top=0.84, bottom=0.09, wspace=0.34, hspace=0.34)
    fig.text(0.07, 0.965, "ONE FIELD · TWO MODES · PARAMETER SENSITIVITY", color=MUTED, size=10)
    fig.text(0.07, 0.913, "A two-dimensional view into a (3+1) field", color=FG, size=23)
    fig.text(
        0.07,
        0.871,
        "Spatial slice z = 0 · time t = 1.2 · epsilon carries sensitivity to wave speed c",
        color=MUTED,
        size=11,
    )
    titles = [
        "+ mode intensity",
        "− mode intensity",
        "Change of + intensity with c",
        "Change of − intensity with c",
    ]
    intensity_limit = max(float(a.max()) for a in images[:2])
    sensitivity_limit = max(float(np.abs(a).max()) for a in images[2:])
    for n, (ax, a, title) in enumerate(zip(axes.flat, images, titles, strict=True)):
        limits = (0, intensity_limit) if n < 2 else (-sensitivity_limit, sensitivity_limit)
        im = ax.imshow(
            a.T,
            origin="lower",
            extent=(-5, 5, -5, 5),
            vmin=limits[0],
            vmax=limits[1],
            cmap="magma" if n < 2 else "RdBu_r",
            interpolation="nearest",
        )
        ax.set(title=title, xlabel="x", ylabel="y")
        fig.colorbar(im, ax=ax, shrink=0.9, pad=0.03)
    fig.text(
        0.07,
        0.025,
        "Rule-defined everywhere. This grid is only a view; all eight value coefficients remain available.",
        color=MUTED,
        size=10,
    )
    save_figure(fig, output / "ultrafield-slices.png")


def plot_surfaces(output, shape):
    fig = plt.figure(figsize=(13, 7.2))
    fig.subplots_adjust(left=0.01, right=0.99, top=0.77, bottom=0.14, wspace=0.02)
    fig.text(
        0.055, 0.94, "THE SAME VALUE ALGEBRA · DIFFERENT SPATIAL GEOMETRY", color=MUTED, size=10
    )
    fig.text(0.055, 0.874, "Fields on a torus and a Möbius strip", color=FG, size=25)
    norm = Normalize(-2, 2)
    for index, (surface, field) in enumerate(surface_fields()):
        axes = {
            name: np.linspace(*bounds, n)
            for name, bounds, n in zip(
                surface.space.spatial_axes, surface.bounds, shape, strict=True
            )
        }
        grid = field.slice(t=0).sample(axes)
        positions = np.array(
            [
                surface.locate(sample).point.position
                for sample in field.slice(t=0).iter_samples(axes)
            ]
        ).reshape(*grid.shape, 3)
        color = np.array([v.channels()[0][0].real for v in grid.values]).reshape(grid.shape)
        ax = fig.add_subplot(1, 2, index + 1, projection="3d")
        ax.plot_surface(
            positions[..., 0],
            positions[..., 1],
            positions[..., 2],
            facecolors=plt.colormaps["coolwarm"](norm(color)),
            rstride=1,
            cstride=1,
            linewidth=0,
            antialiased=True,
            shade=False,
        )
        ax.set_axis_off()
        ax.set_box_aspect((1, 1, 0.42))
        ax.view_init(elev=35 if index == 0 else 27, azim=-58)
        ax.set_title(
            "TORUS\nTwo periodic coordinates"
            if index == 0
            else "MÖBIUS STRIP\n(u + 2π, v) ≡ (u, −v)",
            color=FG,
            pad=0,
        )
    cax = fig.add_axes((0.33, 0.14, 0.34, 0.022))
    fig.colorbar(
        plt.cm.ScalarMappable(norm=norm, cmap="coolwarm"),
        cax=cax,
        orientation="horizontal",
        label="Real part of the + mode (one selected observable)",
    )
    fig.text(
        0.055,
        0.035,
        "Embedding, metric and seam transitions act on the domain. No algebra generator becomes a spatial direction.",
        color=MUTED,
        size=10,
    )
    save_figure(fig, output / "ultrafield-surfaces.png")


def animate_waves(output, size, frames):
    # Only time is sampled for the animation; the underlying formula is continuous.
    times = np.linspace(0, 5, frames)
    intensity = interference_field().map(Ultra.abs2)
    axis = np.linspace(-5, 5, size)
    arrays = []
    for t in times:
        a = intensity.slice(z=0, t=float(t)).sample({"x": axis, "y": axis}).to_numpy()
        arrays.append((a[..., 0] + a[..., 1]).T)
    fig, ax = plt.subplots(figsize=(6.5, 6.2))
    fig.subplots_adjust(left=0.1, right=0.88, top=0.88, bottom=0.13)
    im = ax.imshow(
        arrays[0],
        extent=(-5, 5, -5, 5),
        origin="lower",
        vmin=0,
        vmax=max(float(a.max()) for a in arrays),
        cmap="magma",
        interpolation="nearest",
    )
    ax.set(xlabel="x", ylabel="y")
    title = ax.set_title("")
    fig.colorbar(im, ax=ax, label="+ mode intensity", shrink=0.85)
    fig.text(0.1, 0.04, "UltraField · z = 0 · a time-dependent spatial slice", color=MUTED, size=10)

    def update(index):
        im.set_data(arrays[index])
        title.set_text(f"Interference · t = {times[index]:.2f}")
        return im, title

    animation = FuncAnimation(fig, update, frames=len(times), interval=90)
    path = output / "ultrafield-time.gif"
    animation.save(path, writer=PillowWriter(fps=8), dpi=95)
    # Keep the portable preview compact. Nearest-neighbour resizing preserves
    # the sampled cells; palette reduction affects display colors, not values.
    with Image.open(path) as rendered:
        size = (480, round(480 * rendered.height / rendered.width))
        previews = [
            frame.convert("RGB")
            .resize(size, Image.Resampling.NEAREST)
            .quantize(colors=32, dither=Image.Dither.NONE)
            for frame in ImageSequence.Iterator(rendered)
        ]
    previews[0].save(
        path, save_all=True, append_images=previews[1:], duration=125, loop=0, optimize=True
    )
    plt.close(fig)
    print(f"Wrote {path}", flush=True)


def report(size, surface_shape, frames):
    root = Path(__file__).resolve().parents[1]
    sources = (
        "src/ultracomplexmath/core.py",
        "src/ultracomplexmath/fields.py",
        "src/ultracomplexmath/surfaces.py",
        "examples/fields.py",
    )
    seams = {}
    for surface, field in surface_fields():
        check = surface.check_seams(field, samples=17, times=(0, 0.7))
        assert check.within(atol=1e-8)
        seams[surface.name] = {
            "comparisons": check.comparisons,
            "max_value_coefficient_error": max(check.value_errors),
            "max_partial_coefficient_error": max(map(max, check.derivative_errors)),
        }
    ring = torus()
    area = ring.integrate(UltraField.constant(1, ring.space), shape=(32, 32)).real
    return {
        "environment": {
            "python": platform.python_version(),
            "ultracomplexmath": __version__,
            "numpy": np.__version__,
            "matplotlib": matplotlib.__version__,
        },
        "source_sha256": {
            name: hashlib.sha256((root / name).read_bytes()).hexdigest() for name in sources
        },
        "wave_formula": WAVE_FORMULA,
        "wave_parameters": {"speed": 1, "omega1": math.sqrt(3.08), "omega2": math.sqrt(4.3)},
        "wave_grid": [size, size],
        "wave_bounds": [-5, 5],
        "wave_slice": {"z": 0, "t": 1.2},
        "surface_grid": list(surface_shape),
        "surface_time": 0,
        "surface_formulas": {"torus": TORUS_FORMULA, "mobius": MOBIUS_FORMULA},
        "seam_checks": seams,
        "torus_area_absolute_error": abs(area - 4 * math.pi**2 * 2 * 0.65),
        "animation_frames": frames,
        "animation_preview": {"width": 480, "palette_colors": 32, "fps": 8},
        "animation_time_interval": [0, 5],
        "note": "Numerical diagnostics on stated samples; no claim of a new physical theory.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("docs/gallery/assets"))
    parser.add_argument("--quick", action="store_true")
    parser.add_argument("--animate", action="store_true")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    configure()
    size = 61 if args.quick else 141
    surface_shape = (57, 29) if args.quick else (113, 57)
    frames = (8 if args.quick else 16) if args.animate else 0
    plot_waves(args.output, size)
    plot_surfaces(args.output, surface_shape)
    if args.animate:
        animate_waves(args.output, 41 if args.quick else 65, frames)
    (args.output / "ultrafield-report.json").write_text(
        json.dumps(report(size, surface_shape, frames), indent=2) + "\n"
    )


if __name__ == "__main__":
    main()
