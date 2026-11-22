import math
from types import SimpleNamespace

import pytest

from ultracomplexmath import EPS, ONE, ExpressionError, I, J, Ultra
from ultracomplexmath.numbers import Binary, Dual
from ultracomplexmath.visuals import domain_color_grid, sample_curve


def test_curve_samples_and_domain_failures():
    curve = sample_curve("f=exp(x*i); y=2", 0, math.tau, 5)
    assert curve.component(0) == pytest.approx((1, 0, -1, 0, 1), abs=1e-12)
    assert curve.component(2) == pytest.approx((0, 1, 0, -1, 0), abs=1e-12)
    assert sample_curve("1/x", -1, 1, 3).values == (Ultra(-1), None, Ultra(1))
    with pytest.raises(ExpressionError):
        sample_curve("sin(missing)")
    for source in ("f=y;y=f", "f=x+missing"):
        with pytest.raises(ExpressionError):
            sample_curve(source)


@pytest.mark.parametrize("kind", [Binary, Dual])
def test_domain_sampling(kind):
    grid = domain_color_grid("x*x", kind=kind, resolution=5)
    for y, row in zip(grid.ys, grid.values, strict=True):
        for x, value in zip(grid.xs, row, strict=True):
            assert value.isclose(kind(x, y) ** 2)
    assert all(0 <= c <= 1 for row in grid.colors for pixel in row for c in pixel)


def test_graphical_controls(tmp_path):
    mpl = pytest.importorskip("matplotlib")
    mpl.use("Agg")
    import matplotlib.pyplot as plt

    from ultracomplexmath.gui import FormulaExplorer, MechanismExplorer

    formula = FormulaExplorer()
    formula.range.set_val("-1, 1, 9")
    formula.phase.set_val(0.5)
    for i in range(4):
        formula.mode.set_active(i)
        assert formula.status.get_color() != "#ad2323"
    marker = formula.marker
    formula.on_key(SimpleNamespace(key="right", inaxes=formula.axes))
    assert formula.marker == marker + 0.1
    formula.on_click(SimpleNamespace(inaxes=formula.axes, xdata=0.2, ydata=0.1))
    assert formula.marker == 0.2 + 0.1j
    formula.formula.set_val("missing(x)")
    assert formula.status.get_color() == "#ad2323"
    formula.formula.set_val("exp((x+t)*i)")
    formula.mode.set_active(0)
    formula.figure.savefig(tmp_path / "formula.png")
    mechanism = MechanismExplorer()
    mechanism.sliders[0].set_val(0.75)
    end = mechanism.machine.mechanisms["elbow"].adjusted_joint.endpoint
    assert end == pytest.approx((0, 3.5, 0), abs=1e-12)
    mechanism.figure.savefig(tmp_path / "mechanism.png")
    for name in ("formula", "mechanism"):
        assert (tmp_path / f"{name}.png").stat().st_size > 1000
    plt.close("all")


def test_domain_projection_and_contours():
    grid = domain_color_grid(
        "x*x", resolution=5, input_basis=(I + J, EPS), components=(0, 6), contours=(8, 1, 0)
    )
    assert len(grid.values) == 5
    assert grid.values[0][0].imag == pytest.approx(8)
    assert grid.colors[2][2] == (0, 0, 0)
    projected_norm = domain_color_grid(
        "x", resolution=3, input_basis=(ONE, EPS), components=(None, 4)
    )
    assert projected_norm.values[0][0].real == pytest.approx(math.sqrt(8))
