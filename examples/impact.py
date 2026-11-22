"""Three engineering use cases, a formula audit, and an offline interactive lab.

python -m examples.impact
python -m examples.impact --quick --output /tmp/ultra-impact
python -m examples.impact --only formulas
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
from dataclasses import asdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from examples.gallery import (
    CYAN,
    FG,
    GOLD,
    MUTED,
    PINK,
    PURPLE,
    clean,
    configure,
    footer,
    save,
    title,
)
from examples.impact_models import (
    LAYERS,
    Circuit,
    coating_reference,
    coating_response,
    exact_circuit_audit,
    exact_damping_audit,
    fit_impedance,
    impedance,
    impedance_reference,
    information,
    oscillator_path,
    oscillator_reference,
    synthetic_spectrum,
)
from ultracomplexmath import ONE

ROOT = Path(__file__).resolve().parents[1]


def frame(number, heading, subtitle):
    fig, axes = plt.subplots(2, 2, figsize=(14, 9.5))
    fig.subplots_adjust(left=0.075, right=0.963, bottom=0.11, top=0.74, hspace=0.58, wspace=0.3)
    title(fig, number, heading, subtitle)
    for ax in axes.flat:
        clean(ax)
    return fig, axes


def optical_data(quick=False):
    wavelengths = np.linspace(400, 1000, 21 if quick else 41)
    scales = np.linspace(0.6, 1.6, 11 if quick else 21)
    angles = np.array([0, 15, 30, 45, 60, 75])
    values = np.empty((len(scales), len(angles), len(wavelengths), 4))
    reflection_error = energy_error = 0.0
    for k, scale in enumerate(scales):
        for a, angle in enumerate(angles):
            for n, wavelength in enumerate(wavelengths):
                response = coating_response(wavelength, angle, scale)
                (s, ds), (p, dp) = response.reflectance.channels()
                values[k, a, n] = s.real, p.real, ds.real, dp.real
                ref = coating_reference(wavelength, angle, scale)
                reflection_error = max(
                    reflection_error,
                    *(
                        abs(z - r)
                        for (z, _), r in zip(response.reflection.channels(), ref, strict=True)
                    ),
                )
                energy_error = max(
                    energy_error,
                    *(abs(x) for x in (response.reflectance + response.transmittance - ONE)),
                )
    # A stated, uniformly weighted design score, not an irradiance/PV-yield model.
    objective = values[:, (0, 2, 4), :, :2].mean(axis=(1, 2, 3))
    chosen = int(np.argmin(objective))
    nominal = int(np.argmin(abs(scales - 1)))
    bare = np.mean(
        [
            coating_response(w, a, layers=()).reflectance.real
            for w in wavelengths
            for a in (0, 30, 60)
        ]
    )
    shifted, predicted = [], []
    for w in wavelengths:
        r = coating_response(w, 45, scales[chosen]).reflectance
        shifted.append(coating_response(w, 45, scales[chosen] * 1.05).reflectance.real - r.real)
        predicted.append(0.05 * scales[chosen] * r.eps)
    return {
        "wavelengths": wavelengths,
        "scales": scales,
        "angles": angles,
        "values": values,
        "objective": objective,
        "chosen": chosen,
        "nominal": nominal,
        "shifted": np.array(shifted),
        "predicted": np.array(predicted),
        "report": {
            "layers_index_thickness_nm": LAYERS,
            "substrate_index": 1.52,
            "score": "arithmetic mean R over sampled 400–1000 nm, angles 0/30/60 degrees, s/p equally weighted",
            "wavelength_samples": len(wavelengths),
            "scale_samples": len(scales),
            "bare_mean_R": float(bare),
            "nominal_mean_R": float(objective[nominal]),
            "selected_mean_R": float(objective[chosen]),
            "selected_first_layer_scale": float(scales[chosen]),
            "max_complex_reflection_error_vs_fresnel": reflection_error,
            "max_energy_body_and_tangent_residual": energy_error,
            "plus_5_percent_max_prediction_error_in_R": float(
                max(abs(np.array(shifted) - predicted))
            ),
        },
    }


def render_optics(output, data):
    fig, axes = frame(
        "14 / OPTICAL DESIGN",
        "Less reflection. Visible tolerances.",
        "Two polarizations × complex interference × thickness sensitivity, in ordered projective layers.",
    )
    w, values = data["wavelengths"], data["values"]
    chosen, nominal = data["chosen"], data["nominal"]
    ax = axes[0, 0]
    for column, color, label in ((0, CYAN, "s"), (1, PURPLE, "p")):
        ax.plot(w, values[chosen, 3, :, column] * 100, color=color, label=f"selected / {label}")
        ax.plot(
            w,
            values[nominal, 3, :, column] * 100,
            color=color,
            ls=":",
            alpha=0.65,
            label=f"nominal / {label}",
        )
    ax.set(
        title="01   Two polarizations at 45°",
        xlabel="Wavelength / nm",
        ylabel="Reflected power / %",
    )
    ax.legend(ncol=2, fontsize=8, frameon=False)
    ax = axes[0, 1]
    ax.plot(data["scales"], data["objective"] * 100, color=CYAN, lw=2)
    ax.scatter(
        [1, data["scales"][chosen]],
        data["objective"][[nominal, chosen]] * 100,
        c=[GOLD, CYAN],
        s=65,
        zorder=3,
    )
    ax.axhline(data["report"]["bare_mean_R"] * 100, color=MUTED, ls="--", label="bare glass")
    ax.set(
        title="02   Choose a thickness",
        xlabel="First-layer thickness / nominal thickness",
        ylabel="Uniform design score / %",
    )
    ax.legend(frameon=False)
    ax.text(
        0.03,
        0.84,
        "400–1000 nm · 0°, 30°, 60° · equal s/p weights",
        transform=ax.transAxes,
        fontsize=8,
        color=MUTED,
    )
    ax = axes[1, 0]
    for col, color, label in ((0, CYAN, "s polarization"), (1, PURPLE, "p polarization")):
        ax.plot(
            data["angles"],
            values[chosen, :, :, col].mean(axis=1) * 100,
            "o-",
            color=color,
            label=label,
        )
    ax.set(
        title="03   Inspect angular tradeoffs",
        xlabel="Incidence angle / degrees",
        ylabel="Mean spectral reflection / %",
    )
    ax.legend(frameon=False, fontsize=9)
    ax = axes[1, 1]
    ax.plot(w, data["shifted"] * 100, color=GOLD, lw=2.5, label="recomputed at +5% thickness")
    ax.plot(w, data["predicted"] * 100, color=PINK, ls="--", label="tangent prediction")
    ax.axhline(0, color=MUTED, lw=0.6)
    ax.set(
        title="04   Predict manufacturing drift",
        xlabel="Wavelength / nm",
        ylabel="Change in unpolarized R / percentage points",
    )
    ax.legend(frameon=False, fontsize=9)
    footer(
        fig,
        "Lossless, nondispersive illustrative stack · sampled one-parameter search · no solar-yield forecast",
    )
    save(fig, output / "assets/impact-optics.png")


def circuit_data():
    fs = np.geomspace(0.01, 1e6, 65)
    observations, sigmas = synthetic_spectrum(fs)
    fit = fit_impedance(fs, observations, sigmas)
    model = fit["circuit"]
    responses = [impedance(f, model).channels() for f in fs]
    z = np.array([a[0] for a, _ in responses])
    derivatives = np.array([[a[1], b[1]] for a, b in responses])
    errors = np.array(
        [
            [
                abs(a[0] - impedance_reference(f, model)[0]),
                abs(a[1] - impedance_reference(f, model)[1]),
                abs(b[1] - impedance_reference(f, model)[2]),
            ]
            for f, (a, b) in zip(fs, responses, strict=True)
        ]
    )
    relative_errors = errors / np.array(
        [[abs(x) for x in impedance_reference(f, model)] for f in fs]
    )
    high = information(fs[-17:], model, sigmas[-17:])
    audit = exact_circuit_audit()
    return {
        "frequencies": fs,
        "observations": np.array(observations),
        "sigmas": np.array(sigmas),
        "fit": fit,
        "z": z,
        "derivatives": derivatives,
        "high": high,
        "report": {
            "truth": asdict(Circuit()),
            "fit": asdict(model),
            "synthetic_seed": 2317,
            "noise": "independent real/imag Gaussian sigma = 0.006 * abs(Z_truth)",
            "frequency_range_hz": [0.01, 1e6],
            "frequency_count": len(fs),
            "fit_converged": fit["converged"],
            "weighted_costs": fit["costs"],
            "reduced_chi_squared": fit["reduced_chi_squared"],
            "full_band_information": fit["information"],
            "high_band_information": high,
            "high_band_range_hz": [float(fs[-17]), float(fs[-1])],
            "max_relative_errors_Z_dlogRp_dlogRct": relative_errors.max(axis=0).tolist(),
            "max_absolute_errors_Z_dlogRp_dlogRct": errors.max(axis=0).tolist(),
            "exact_fixture_impedance_coefficients": [str(x) for x in audit["impedance"]],
            "exact_fixture_residual_zero_in_all_24_coefficients": all(
                not any(x) for x in audit["residual"]
            ),
        },
    }


def render_impedance(output, data):
    fig, axes = frame(
        "15 / COATING DIAGNOSTICS",
        "One spectrum. Two hidden pathways.",
        "Complex impedance + two resistance derivatives + inverse fitting + frequency-band identifiability.",
    )
    z, observed, f = data["z"], data["observations"], data["frequencies"]
    ax = axes[0, 0]
    ax.plot(z.real / 1000, -z.imag / 1000, color=CYAN, label="fitted Kirchhoff model")
    ax.scatter(
        observed.real / 1000, -observed.imag / 1000, c=GOLD, s=11, label="synthetic observations"
    )
    ax.set(
        title="01   Recover a protective-coating model", xlabel="Re(Z) / kΩ", ylabel="−Im(Z) / kΩ"
    )
    ax.set_aspect("equal", adjustable="datalim")
    ax.legend(frameon=False, fontsize=8)
    ax = axes[0, 1]
    for col, color, label in (
        (0, CYAN, "pore resistance Rp"),
        (1, PURPLE, "charge-transfer resistance Rct"),
    ):
        ax.loglog(f, abs(data["derivatives"][:, col]) / abs(z), color=color, label=label)
    ax.axvspan(1e4, 1e6, color=GOLD, alpha=0.1)
    ax.set(
        title="02   Which frequencies see each parameter?",
        xlabel="Frequency / Hz",
        ylabel="|∂Z/∂log R| / |Z|",
    )
    ax.legend(frameon=False, fontsize=8)
    ax = axes[1, 0]
    x = np.arange(2)
    full = data["fit"]["information"]["log_sigma"]
    restricted = data["high"]["log_sigma"]
    ax.bar(x - 0.17, full, width=0.3, color=CYAN, label="0.01 Hz–1 MHz")
    ax.bar(x + 0.17, restricted, width=0.3, color=GOLD, label="10 kHz–1 MHz")
    ax.set_yscale("log")
    ax.set_xticks(x, ["log Rp", "log Rct"])
    ax.set(
        title="03   A fit needs informative measurements",
        ylabel="Local standard deviation / log units",
    )
    ax.legend(frameon=False, fontsize=8)
    ax = axes[1, 1]
    ax.axis("off")
    model = data["fit"]["circuit"]
    ax.text(0, 1, "04   A reproducible recovery", fontsize=14, fontweight="bold", va="top")
    lines = [
        ("PARAMETER", "GENERATED", "RECOVERED"),
        ("Rp / Ω", "2,400", f"{model.rp:,.1f}"),
        ("Rct / Ω", "9,000", f"{model.rct:,.1f}"),
    ]
    for y, row in zip((0.72, 0.52, 0.32), lines, strict=True):
        for xx, label in zip((0, 0.41, 0.77), row, strict=True):
            ax.text(
                xx, y, label, color=MUTED if y > 0.7 else FG, fontsize=10, transform=ax.transAxes
            )
    ax.text(
        0, 0.06, "Rs, Cf and Cdl held fixed · 0.6% known component noise", color=MUTED, fontsize=9
    )
    footer(
        fig,
        "Synthetic equivalent-circuit experiment · local uncertainty assumes this model and known noise · no corrosion-rate claim",
    )
    save(fig, output / "assets/impact-impedance.png")


def damping_data(quick=False):
    dampings = np.linspace(0.2, 1.8, 17)
    tau = np.arange(241) * 0.05
    values = np.array([oscillator_path(float(z), 0.05, 240) for z in dampings])
    errors, energy_errors = [], []
    for damping, rows in zip(dampings, values, strict=True):
        reference = np.array([oscillator_reference(t, damping) for t in tau])
        errors.append(float(np.max(abs(rows[:, :2] - reference))))
        q, v = rows[:, 0], rows[:, 1]
        energy_errors.append(
            float(
                np.max(
                    abs(
                        np.diff((q * q + v * v) / 2)
                        + 2 * damping * 0.05 * ((v[:-1] + v[1:]) / 2) ** 2
                    )
                )
            )
        )
    audit = exact_damping_audit()
    critical = int(np.argmin(abs(dampings - 1)))
    continuous_derivative = np.exp(-tau) * tau**3 / 3
    convergence = []
    for h in (0.2, 0.1, 0.05, 0.025):
        t = np.arange(round(12 / h) + 1) * h
        path = np.array(oscillator_path(1, h, len(t) - 1))
        ref = np.array([oscillator_reference(x, 1) for x in t])
        convergence.append([h, float(np.max(abs(path[:, :2] - ref)))])
    return {
        "dampings": dampings,
        "tau": tau,
        "values": values,
        "critical": critical,
        "continuous_derivative": continuous_derivative,
        "convergence": np.array(convergence),
        "stride": 4 if quick else 2,
        "report": {
            "dimensionless_step": 0.05,
            "steps": 240,
            "initial_state": [1, 0],
            "damping_range": [0.2, 1.8],
            "damping_count": len(dampings),
            "max_position_velocity_error_vs_continuous": max(errors),
            "max_discrete_energy_balance_residual": max(energy_errors),
            "max_critical_position_sensitivity_error_vs_continuous": float(
                max(abs(values[critical, :, 2] - continuous_derivative))
            ),
            "critical_convergence_step_max_error": convergence,
            "exact_dual_energy_residual_zero": not any(audit["energy_residual"]),
            "jordan_square_zero": audit["jordan_square_zero"],
            "epsilon_times_jordan_nonzero": audit["epsilon_times_jordan_nonzero"],
        },
    }


def render_damping(output, data):
    fig, axes = frame(
        "16 / VIBRATION CONTROL",
        "Cross critical damping. Keep the derivative.",
        "One rational operator handles ringing, critical decay and overdamping, with an exact discrete energy law.",
    )
    tau, values = data["tau"], data["values"]
    selected = [
        (2, CYAN, "ζ = 0.4 / ringing"),
        (8, GOLD, "ζ = 1.0 / critical"),
        (14, PURPLE, "ζ = 1.6 / overdamped"),
    ]
    ax = axes[0, 0]
    for index, color, label in selected:
        ax.plot(tau, values[index, :, 0], color=color, label=label)
    ax.axhspan(-0.02, 0.02, color=FG, alpha=0.08)
    ax.set(
        title="01   Residual motion after a displacement",
        xlabel="Normalized time τ = ω₀t",
        ylabel="Position / initial displacement",
    )
    ax.legend(frameon=False, fontsize=8)
    ax = axes[0, 1]
    for index, color, label in selected:
        q, v = values[index, :, 0], values[index, :, 1]
        ax.semilogy(tau, q * q + v * v, color=color, label=label)
    ax.set(
        title="02   Dissipation, not numerical energy gain",
        xlabel="Normalized time τ",
        ylabel="Energy / initial energy",
    )
    ax.text(
        0.04, 0.92, "ΔE = −2ζh [(vₙ₊₁ + vₙ)/2]²", transform=ax.transAxes, color=GOLD, fontsize=11
    )
    ax = axes[1, 0]
    ax.plot(
        tau, values[data["critical"], :, 2], color=GOLD, lw=3, label="Ultra / discrete derivative"
    )
    ax.plot(
        tau,
        data["continuous_derivative"],
        color=PINK,
        ls="--",
        label="continuous reference exp(−τ) τ³/3",
    )
    ax.set(
        title="03   Sensitivity remains finite at ζ = 1",
        xlabel="Normalized time τ",
        ylabel="∂q / ∂ζ",
    )
    ax.legend(frameon=False, fontsize=8)
    ax = axes[1, 1]
    conv = data["convergence"]
    ax.loglog(conv[:, 0], conv[:, 1], "o-", color=CYAN, label="max q/v error over 0 ≤ τ ≤ 12")
    ax.loglog(
        conv[:, 0],
        conv[-1, 1] * (conv[:, 0] / conv[-1, 0]) ** 2,
        "--",
        color=MUTED,
        label="second-order slope",
    )
    ax.set(
        title="04   Time accuracy is checked separately",
        xlabel="Midpoint step h",
        ylabel="Error against continuous solution",
    )
    ax.legend(frameon=False, fontsize=8)
    footer(
        fig,
        "Single passive linear mode · q(0)=1, v(0)=0 · exact discrete derivatives do not imply an exact continuous trajectory",
    )
    save(fig, output / "assets/impact-damping.png")


def formula_data():
    circuit, frequency = Circuit(), 8.0
    (_, u), (_, v) = impedance(frequency, circuit).channels()
    refs = impedance_reference(frequency, circuit)[1:]
    steps = np.logspace(-12, -1, 45)
    fd = []
    for h in steps:
        row = []
        for name, reference in zip(("rp", "rct"), refs, strict=True):
            parameters = asdict(circuit)
            parameters[name] *= math.exp(h)
            a = impedance_reference(frequency, Circuit(**parameters))[0]
            parameters = asdict(circuit)
            parameters[name] *= math.exp(-h)
            b = impedance_reference(frequency, Circuit(**parameters))[0]
            row.append(abs((a - b) / (2 * h) - reference) / abs(reference))
        fd.append(row)
    errors = [abs(x - r) / abs(r) for x, r in zip((u, v), refs, strict=True)]
    return {
        "steps": steps,
        "fd": np.array(fd),
        "ultra_errors": errors,
        "report": {
            "frequency_hz": frequency,
            "relative_Ultra_derivative_errors": errors,
            "current_internal_complex_solves": 4,
            "ordinary_equations_with_shared_body": 3,
            "claim": "fewer handwritten derivative equations; no speedup claim",
        },
    }


def render_formulas(output, data):
    fig, axes = frame(
        "17 / FORMULA AUDIT",
        "Three equations. One algebraic expression.",
        "A complex solution and two independent first variations share one Ultra solve — the arithmetic still has a cost.",
    )
    for ax in axes[0]:
        ax.axis("off")
    ax = axes[0, 0]
    ax.text(0, 1, "ORDINARY COMPLEX FORM", fontsize=12, color=MUTED, va="top")
    for y, equation in [
        (0.71, r"$A_0 x_0=b_0$"),
        (0.43, r"$A_0 u=b_1-A_1 x_0$"),
        (0.15, r"$A_0 v=b_2-A_2 x_0$"),
    ]:
        ax.text(0.02, y, equation, fontsize=19)
    ax = axes[0, 1]
    ax.text(0, 1, "PACKED ULTRACOMPLEX FORM", fontsize=12, color=CYAN, va="top")
    ax.text(0, 0.72, r"$A_\star=A_0+\varepsilon(p_+A_1+p_-A_2)$", fontsize=17)
    ax.text(0, 0.48, r"$b_\star=b_0+\varepsilon(p_+b_1+p_-b_2)$", fontsize=17)
    ax.text(0, 0.18, r"$x_\star=\mathrm{solve}(A_\star,b_\star)$", fontsize=23, color=CYAN)
    ax = axes[1, 0]
    for col, color, name in ((0, CYAN, "∂Z/∂log Rp"), (1, PURPLE, "∂Z/∂log Rct")):
        ax.loglog(
            data["steps"], data["fd"][:, col], color=color, label=f"central difference / {name}"
        )
        ax.axhline(
            max(data["ultra_errors"][col], 1e-17), color=color, ls=":", label=f"Ultra / {name}"
        )
    ax.set(
        title="Derivative error at 8 Hz",
        xlabel="Finite-difference log-parameter step",
        ylabel="Relative error vs explicit derivative",
    )
    ax.legend(frameon=False, fontsize=7.5, ncol=1)
    ax = axes[1, 1]
    ax.axis("off")
    ax.text(0, 1, "WHAT ACTUALLY BECOMES SIMPLER", fontsize=12, color=CYAN, va="top")
    ax.text(
        0,
        0.71,
        "One model expression propagates both derivatives.\nNo perturbation step to tune; no hand-derived Jacobian.",
        fontsize=11,
        linespacing=1.7,
    )
    ax.text(
        0,
        0.4,
        "Exact fixture: all 24 residual coefficients are zero.\nFloat fixture: roundoff remains and is measured.",
        fontsize=11,
        linespacing=1.7,
    )
    ax.text(
        0,
        0.07,
        "Current solve: four internal complex solves.\nA reused ordinary factorization can be faster.",
        fontsize=11,
        color=GOLD,
        linespacing=1.7,
    )
    footer(
        fig,
        "p± = (1±j)/2 · shared complex body · two first derivatives, no Hessian · exact rational audit is a separate fixture",
    )
    save(fig, output / "assets/impact-formulas.png")


def serializable(value, rounded=False):
    if isinstance(value, np.ndarray):
        return serializable(value.tolist(), rounded)
    if isinstance(value, dict):
        return {key: serializable(v, rounded) for key, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [serializable(v, rounded) for v in value]
    if isinstance(value, (float, np.floating)):
        return float(f"{value:.7g}") if rounded else float(value)
    if isinstance(value, complex):
        return serializable([value.real, value.imag], rounded)
    return value


def render_lab(output, optics, circuit, damping, formulas):
    stride = damping["stride"]
    payload = {
        "optics": {
            key: optics[key]
            for key in (
                "wavelengths",
                "scales",
                "angles",
                "values",
                "objective",
                "chosen",
                "nominal",
            )
        },
        "circuit": {
            key: circuit[key]
            for key in ("frequencies", "observations", "z", "derivatives", "report")
        },
        "damping": {
            "dampings": damping["dampings"],
            "tau": damping["tau"][::stride],
            "values": damping["values"][:, ::stride],
            "critical": damping["critical"],
        },
        "formulas": {key: formulas[key] for key in ("steps", "fd", "ultra_errors")},
    }
    template = (ROOT / "examples/impact_lab.html").read_text()
    html = template.replace(
        "__IMPACT_DATA__",
        json.dumps(serializable(payload, rounded=True), separators=(",", ":"), allow_nan=False),
    )
    (output / "impact-lab.html").write_text(html)
    print(f"Rendered {output / 'impact-lab.html'}", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--quick", action="store_true")
    parser.add_argument("--output", type=Path, default=ROOT / "docs/gallery")
    parser.add_argument("--only", choices=("optics", "impedance", "damping", "formulas"))
    args = parser.parse_args()
    (args.output / "assets").mkdir(parents=True, exist_ok=True)
    configure()
    loaders = {
        "optics": lambda: optical_data(args.quick),
        "impedance": circuit_data,
        "damping": lambda: damping_data(args.quick),
        "formulas": formula_data,
    }
    renderers = {
        "optics": render_optics,
        "impedance": render_impedance,
        "damping": render_damping,
        "formulas": render_formulas,
    }
    data = {}
    for name in [args.only] if args.only else loaders:
        data[name] = loaders[name]()
        renderers[name](args.output, data[name])
    sources = [
        "examples/impact.py",
        "examples/impact_models.py",
        "examples/impact_lab.html",
        "examples/gallery.py",
        "src/ultracomplexmath/core.py",
        "src/ultracomplexmath/exact.py",
        "src/ultracomplexmath/linalg.py",
        "src/ultracomplexmath/exact_linalg.py",
        "src/ultracomplexmath/transformations.py",
    ]
    report = {
        "scope": "bounded example checks, not a certification or general error bound",
        "quick": args.quick,
        "python": platform.python_version(),
        "numpy": np.__version__,
        "matplotlib": matplotlib.__version__,
        "source_sha256": {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in sources},
        "demos": {key: value["report"] for key, value in data.items()},
    }
    if not args.only:
        render_lab(
            args.output, data["optics"], data["impedance"], data["damping"], data["formulas"]
        )
    name = f"impact-{args.only}-report.json" if args.only else "impact-report.json"
    (args.output / "assets" / name).write_text(
        json.dumps(serializable(report), indent=2, allow_nan=False) + "\n"
    )
    print(f"Report: {args.output / 'assets' / name}", flush=True)


if __name__ == "__main__":
    main()
