"""Optional desktop explorers; run ``ultracomplex-gui --help``.

Matplotlib supplies windows, keyboard/mouse events, widgets and image export.
The math package stays importable without the optional plotting dependency.
"""

from __future__ import annotations

import argparse
import math
from typing import Any

from .core import BASIS
from .geometry import ZERO3
from .mechanisms import Actor, Freedom, Joint, Machine, Mechanism
from .visuals import ALGEBRAS, domain_color_grid, sample_curve


def _plotting() -> tuple[Any, Any]:
    try:
        import matplotlib.pyplot as plt
        import matplotlib.widgets as widgets
    except ImportError as error:
        raise RuntimeError("Install the desktop extra: pip install '.[plot]'") from error
    return plt, widgets


class FormulaExplorer:
    """Editable formulas, eight traces, parametric paths, domain colors and vectors."""

    def __init__(self, source: str = "exp((x+t)*i)", mode: str = "components") -> None:
        plt, widgets = _plotting()
        self.figure, self.axes = plt.subplots(figsize=(11, 7))
        self.figure.subplots_adjust(left=0.10, bottom=0.38, top=0.89)
        self.formula = widgets.TextBox(
            self.figure.add_axes((0.13, 0.94, 0.78, 0.04)), "Formula ", initial=source
        )
        self.range = widgets.TextBox(
            self.figure.add_axes((0.13, 0.27, 0.29, 0.04)), "Range ", initial="-3.14, 3.14, 401"
        )
        self.limits = widgets.TextBox(
            self.figure.add_axes((0.57, 0.27, 0.34, 0.04)), "View bounds ", initial="auto"
        )
        modes = ("components", "paths", "domain", "vectors")
        self.mode = widgets.RadioButtons(
            self.figure.add_axes((0.10, 0.04, 0.20, 0.19)), modes, active=modes.index(mode)
        )
        self.algebra = widgets.RadioButtons(
            self.figure.add_axes((0.34, 0.04, 0.17, 0.19)), tuple(ALGEBRAS)
        )
        self.phase = widgets.Slider(
            self.figure.add_axes((0.60, 0.13, 0.30, 0.04)), "t", -math.pi, math.pi, valinit=0
        )
        self.play = widgets.Button(self.figure.add_axes((0.60, 0.05, 0.13, 0.05)), "Play / pause")
        self.legacy = widgets.CheckButtons(
            self.figure.add_axes((0.76, 0.03, 0.20, 0.08)), ("Legacy colors",), (False,)
        )
        self.status = self.figure.text(0.10, 0.33, "", fontsize=9)
        self.marker: complex = 0j
        self.timer = self.figure.canvas.new_timer(interval=150)
        self.timer.add_callback(self.tick)
        self.running = False
        self.play.on_clicked(self.toggle_animation)
        for control in (self.formula, self.range, self.limits):
            control.on_submit(self.redraw)
        self.mode.on_clicked(self.redraw)
        self.algebra.on_clicked(self.redraw)
        self.phase.on_changed(self.redraw)
        self.legacy.on_clicked(self.redraw)
        self.figure.canvas.mpl_connect("key_press_event", self.on_key)
        self.figure.canvas.mpl_connect("button_press_event", self.on_click)
        self.figure.canvas.mpl_connect("close_event", lambda event: self.timer.stop())
        self.redraw()

    def tick(self) -> None:
        value = (float(self.phase.val) + 0.1 + math.pi) % math.tau - math.pi
        self.phase.set_val(value)

    def toggle_animation(self, event: Any = None) -> None:
        self.running = not self.running
        if self.running:
            self.timer.start()
        else:
            self.timer.stop()

    def on_key(self, event: Any) -> None:
        if event.inaxes is not self.axes:
            return
        shifts = {
            "left": -0.1,
            "a": -0.1,
            "right": 0.1,
            "d": 0.1,
            "up": 0.1j,
            "w": 0.1j,
            "down": -0.1j,
            "s": -0.1j,
        }
        if event.key in shifts:
            self.marker += shifts[event.key]
            self.redraw()
        elif event.key == " ":
            self.toggle_animation()

    def on_click(self, event: Any) -> None:
        if event.inaxes is self.axes and event.xdata is not None and event.ydata is not None:
            self.marker = complex(event.xdata, event.ydata)
            if self.mode.value_selected in ("domain", "vectors", "domain-clusters"):
                self.redraw()

    def redraw(self, event: Any = None) -> None:
        try:
            parts = [p.strip() for p in self.range.text.split(",")]
            start, stop, count = float(parts[0]), float(parts[1]), int(parts[2])
            if len(parts) != 3:
                raise ValueError("Range: start, stop, samples")
            mode, kind = self.mode.value_selected, ALGEBRAS[self.algebra.value_selected]
            parameters = {"t": float(self.phase.val)}
            axes = self.axes
            axes.clear()
            if mode in ("components", "paths"):
                curve = sample_curve(self.formula.text, start, stop, count, parameters=parameters)
                for index, label in enumerate(BASIS):
                    if mode == "components" or index:
                        axes.plot(
                            curve.parameters if mode == "components" else curve.component(0),
                            curve.component(index),
                            label=label,
                            linewidth=1.5,
                        )
                axes.set_xlabel("x" if mode == "components" else "real component")
                axes.set_ylabel("coefficient")
                axes.legend(ncol=4, fontsize=8)
                message = f"{curve.undefined_count} undefined samples; gaps are left in the curves"
            else:
                resolution = min(count, 19) if mode == "vectors" else min(count, 129)
                grid = domain_color_grid(
                    self.formula.text,
                    kind=kind,
                    bounds=(start, stop, start, stop),
                    resolution=resolution,
                    parameters=parameters,
                    legacy_colors=self.legacy.get_status()[0],
                )
                if mode == "domain":
                    axes.imshow(
                        grid.colors,
                        origin="lower",
                        extent=(start, stop, start, stop),
                        interpolation="nearest",
                        aspect="equal",
                    )
                else:
                    points = [
                        (x, y, v)
                        for y, row in zip(grid.ys, grid.values, strict=True)
                        for x, v in zip(grid.xs, row, strict=True)
                        if v is not None
                    ]
                    axes.quiver(
                        [x for x, y, v in points],
                        [y for x, y, v in points],
                        [v.real for x, y, v in points],
                        [v.imag for x, y, v in points],
                        angles="xy",
                        scale_units="xy",
                        scale=6,
                    )
                    axes.set(xlim=(start, stop), ylim=(start, stop), aspect="equal")
                axes.plot(
                    self.marker.real,
                    self.marker.imag,
                    "+",
                    color="white" if mode == "domain" else "red",
                    markersize=12,
                )
                from .expressions import FormulaSystem

                result = FormulaSystem(self.formula.text).result(
                    {**parameters, "x": kind(self.marker.real, self.marker.imag).to_ultra()}
                )
                message = f"x={self.marker:.3g} → {result}; click / arrows / WASD move the probe"
                axes.set(xlabel="real", ylabel=kind.symbol)
            if self.limits.text.strip() != "auto":
                xmin, xmax, ymin, ymax = map(float, self.limits.text.split(","))
                if (
                    not all(map(math.isfinite, (xmin, xmax, ymin, ymax)))
                    or xmin >= xmax
                    or ymin >= ymax
                ):
                    raise ValueError("View bounds must be increasing and finite")
                axes.set(xlim=(xmin, xmax), ylim=(ymin, ymax))
            axes.set_title(f"Ultracomplex Math · {mode}")
            if mode != "domain":
                axes.grid(alpha=0.2)
            self.status.set_text(message)
            self.status.set_color("#444444")
        except (ValueError, ArithmeticError, IndexError) as error:
            self.status.set_text(str(error))
            self.status.set_color("#ad2323")
        self.figure.canvas.draw_idle()


class MechanismExplorer:
    def __init__(self) -> None:
        plt, widgets = _plotting()
        self.figure = plt.figure(figsize=(9, 7))
        self.axes = self.figure.add_subplot(111, projection="3d")
        self.figure.subplots_adjust(bottom=0.30)
        self.machine = Machine(root=Mechanism(Joint(length=0)))
        first = self.machine.connect("shoulder", Joint(length=2))
        second = self.machine.connect("elbow", Joint(length=1.5), "shoulder")
        self.machine.actors = {
            "shoulder": Actor(
                first.joint,
                {
                    "real": Freedom(factor=math.tau, minimum=-math.pi),
                    "imag": Freedom(factor=math.pi, minimum=-math.pi / 2),
                },
            ),
            "elbow": Actor(second.joint, {"real": Freedom(factor=math.tau, minimum=-math.pi)}),
        }
        self.sliders = []
        for index, (label, actor, freedom) in enumerate(
            (
                ("Shoulder", "shoulder", "real"),
                ("Elevation", "shoulder", "imag"),
                ("Elbow", "elbow", "real"),
            )
        ):
            slider = widgets.Slider(
                self.figure.add_axes((0.20, 0.05 + index * 0.07, 0.65, 0.03)),
                label,
                0,
                1,
                valinit=0.5,
            )
            slider.on_changed(lambda value, a=actor, f=freedom: self.change(a, f, value))
            self.sliders.append(slider)
        self.redraw()

    def change(self, actor: str, freedom: str, percentage: float) -> None:
        self.machine.actors[actor].freedoms[freedom].set_percentage(percentage)
        self.redraw()

    def redraw(self) -> None:
        self.machine.update()
        self.axes.clear()
        points = [ZERO3] + [m.adjusted_joint.endpoint for m in self.machine.mechanisms.values()]
        xs, ys, zs = zip(*points, strict=True)
        self.axes.plot(xs, ys, zs, "o-", linewidth=4, color="#7346a6")
        self.axes.set(
            xlim=(-4, 4),
            ylim=(-4, 4),
            zlim=(-4, 4),
            xlabel="x",
            ylabel="y",
            zlabel="z",
            title="Articulated mechanism",
        )
        self.axes.set_box_aspect((1, 1, 1))
        self.figure.canvas.draw_idle()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--view",
        choices=(
            "components",
            "paths",
            "domain",
            "vectors",
            "mechanism",
        ),
        default="components",
    )
    parser.add_argument("--formula", default="exp((x+t)*i)")
    parser.add_argument("--output", help="Render without a display to PNG, SVG or PDF")
    args = parser.parse_args()
    if args.output:
        import matplotlib

        matplotlib.use("Agg")
    app: FormulaExplorer | MechanismExplorer
    app = (
        MechanismExplorer()
        if args.view == "mechanism"
        else FormulaExplorer(args.formula, args.view)
    )
    if args.output:
        app.figure.savefig(args.output, dpi=150)
    else:
        plt, _ = _plotting()
        plt.show()


if __name__ == "__main__":
    main()
