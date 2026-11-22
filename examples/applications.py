"""Further applications of the Ultra engine.

From the repository root: python -m examples.applications
Use --quick for a lower-resolution preview, or --only to select one demo.
"""

from __future__ import annotations

import argparse
import cmath
import json
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation, PillowWriter
from matplotlib.colors import LinearSegmentedColormap, LogNorm

from examples.gallery import (
    BG,
    CYAN,
    FG,
    GOLD,
    MUTED,
    PURPLE,
    clean,
    configure,
    footer,
    save,
    title,
)
from ultracomplexmath import EPS, ONE, I, J

P_PLUS = (ONE + J) / 2
P_MINUS = (ONE - J) / 2
LENGTHS = (1.2, 1.0)
PACKET_WIDTH = 0.85
PACKET_K = 5.5
PACKET_OFFSET = 3.0
WAVELENGTH = 0.7
SIGNED = LinearSegmentedColormap.from_list("ultra_signed", [CYAN, BG, GOLD])


def render_trigonometry(output):
    fig, axes = plt.subplots(1, 3, figsize=(14, 6.5))
    fig.subplots_adjust(left=0.075, right=0.97, top=0.71, bottom=0.21, wspace=0.35)
    title(
        fig,
        "07",
        "The same cosine. Three unmistakable curves.",
        "Fix the real input at π/4 and vary only y: plot the two coefficients of cos(π/4 + u y).",
    )
    y = np.linspace(-math.pi, math.pi, 801)
    for ax, unit, index, color, name, formula in zip(
        axes,
        [I, J, EPS],
        [2, 1, 4],
        [CYAN, PURPLE, GOLD],
        ["COMPLEX · HYPERBOLA", "SPLIT-COMPLEX · CIRCLE", "DUAL · STRAIGHT LINE"],
        ["a² − b² = ½", "a² + b² = ½", "a = 1/√2"],
        strict=True,
    ):
        values = [(math.pi / 4 + float(t) * unit).cos() for t in y]
        a, b = [v.real for v in values], [v.coefficients[index] for v in values]
        for width, alpha in [(10, 0.06), (5, 0.14), (2.6, 1)]:
            ax.plot(a, b, color=color, lw=width, alpha=alpha)
        v = (math.pi / 4 + 0.0 * unit).cos()
        ax.scatter(v.real, v.coefficients[index], c=FG, s=30, zorder=5)
        ax.set_aspect("equal", adjustable="datalim")
        ax.axhline(0, lw=0.6, color=MUTED, alpha=0.4)
        ax.axvline(0, lw=0.6, color=MUTED, alpha=0.4)
        ax.set_title(name, color=color, fontsize=11, loc="left", pad=13)
        ax.set_xlabel("real output a")
        ax.set_ylabel("generator output b")
        ax.text(0.5, -0.27, formula, transform=ax.transAxes, ha="center", fontsize=13)
        clean(ax)
    footer(
        fig,
        "Identical y range: −π to π · equal aspect within each panel · independent panel scales · white point: y = 0",
    )
    save(fig, output / "assets/trigonometry-slices.png")


def wave_state(x, t, speed=1.0):
    """Two characteristic waves and their speed derivative in one Ultra value."""
    q = float(x) - J * ((float(speed) + EPS) * float(t) - PACKET_OFFSET)
    return (-(q * q) / PACKET_WIDTH**2 + I * PACKET_K * q).exp()


def wave_reference(x, t, speed=1.0):
    result = []
    for sign in (1, -1):
        q = x - sign * (speed * t - PACKET_OFFSET)
        f = cmath.exp(-((q / PACKET_WIDTH) ** 2) + 1j * PACKET_K * q)
        derivative = -sign * t * (-2 * q / PACKET_WIDTH**2 + 1j * PACKET_K) * f
        result.append((f, derivative))
    return result


def wave_samples(xs, times):
    return np.array([[wave_state(x, t).coefficients for x in xs] for t in times])


def render_waves(output, quick=False):
    xs = np.linspace(-6, 6, 180 if quick else 400)
    times = np.linspace(0, 6, 49 if quick else 145)
    values = wave_samples(xs, times)
    pressure, tangent = values[:, :, 0], values[:, :, 4]
    fig = plt.figure(figsize=(14, 8.5))
    title(
        fig,
        "08",
        "Two travelling waves. One algebraic field.",
        "j separates left and right propagation; i carries phase; ε differentiates the field with respect to speed.",
    )
    for col, data, label in [
        (0, pressure, "FIELD  u(x,t)"),
        (1, tangent, "SPEED SENSITIVITY  ∂u/∂c"),
    ]:
        ax = fig.add_axes((0.065 + 0.48 * col, 0.43, 0.385, 0.34))
        limit = float(np.max(abs(data)))
        image = ax.imshow(
            data,
            extent=(-6, 6, 6, 0),
            aspect="auto",
            cmap=SIGNED,
            vmin=-limit,
            vmax=limit,
            interpolation="bilinear",
        )
        ax.plot([-3, 3], [0, 6], ":", c=FG, alpha=0.3, lw=0.9)
        ax.plot([3, -3], [0, 6], ":", c=FG, alpha=0.3, lw=0.9)
        ax.set(xlabel="position x", ylabel="time t")
        ax.set_title(label, fontsize=11, loc="left")
        bar = fig.colorbar(image, ax=ax, fraction=0.028, pad=0.025)
        bar.ax.tick_params(labelsize=8)
    ax = fig.add_axes((0.065, 0.13, 0.385, 0.20))
    index = int(np.argmin(abs(times - 2.55)))
    a, b = values[index, :, 0], values[index, :, 1]
    ax.plot(xs, (a + b) / 2, c=CYAN, lw=1.5, label="right-moving contribution")
    ax.plot(xs, (a - b) / 2, c=PURPLE, lw=1.5, label="left-moving contribution")
    ax.plot(xs, a, c=FG, lw=1.8, label="sum")
    ax.set(xlim=(-6, 6), xlabel="position x", ylabel="displacement")
    ax.set_title(f"Superposition at t = {times[index]:.2f}", fontsize=11, loc="left")
    ax.legend(frameon=False, fontsize=8, labelcolor=FG, loc="upper left")
    clean(ax)
    ax = fig.add_axes((0.545, 0.13, 0.385, 0.20))
    index = int(np.argmin(abs(times - 4.4)))
    delta = 0.025
    changed = np.array([wave_state(x, times[index], 1 + delta).real for x in xs])
    predicted = pressure[index] + delta * tangent[index]
    ax.plot(xs, changed, c=CYAN, lw=2, label="actual, c = 1.025")
    ax.plot(xs, predicted, c=GOLD, lw=1.5, ls="--", label="first-order prediction")
    ax.set(xlim=(-6, 6), xlabel="position x", ylabel="displacement")
    ax.set_title(f"A changed propagation speed at t = {times[index]:.2f}", fontsize=11, loc="left")
    ax.legend(frameon=False, fontsize=8, labelcolor=FG, loc="upper left")
    clean(ax)
    footer(
        fig,
        "Exact travelling-wave solution of u_tt = c² u_xx · arbitrary consistent units · independent color scales",
    )
    save(fig, output / "assets/wave-propagation.png")
    render_wave_animation(output, xs, times, values, quick)
    return {"samples": [len(times), len(xs)], "speed": 1.0}


def render_wave_animation(output, xs, times, values, quick):
    fig = plt.figure(figsize=(9.6, 5.8))
    fig.text(0.07, 0.91, "PASS THROUGH. INTERFERE. CONTINUE.", fontsize=16, weight="bold")
    fig.text(
        0.07,
        0.85,
        "One Ultra field carries both travelling waves and their speed sensitivity.",
        color=MUTED,
        fontsize=10,
    )
    ax = fig.add_axes((0.085, 0.44, 0.84, 0.34))
    ax.set(xlim=(-6, 6), ylim=(-1.12, 1.12), ylabel="displacement")
    lines = [
        ax.plot([], [], color=c, lw=lw, label=label)[0]
        for c, lw, label in [
            (CYAN, 1.7, "right-moving"),
            (PURPLE, 1.7, "left-moving"),
            (FG, 2.1, "sum"),
        ]
    ]
    ax.legend(loc="upper right", ncols=3, fontsize=8, frameon=False, labelcolor=FG)
    clean(ax)
    space = fig.add_axes((0.085, 0.15, 0.84, 0.21))
    space.imshow(values[:, :, 0], extent=(-6, 6, 6, 0), aspect="auto", cmap=SIGNED, vmin=-1, vmax=1)
    space.set(xlabel="position x", ylabel="time t")
    cursor = space.axhline(0, c=FG, lw=1.1)
    label = fig.text(0.5, 0.045, "", ha="center", color=MUTED, fontsize=10)
    frames = 24 if quick else 96

    def update(frame):
        index = int(frame * (len(times) - 1) / (frames - 1))
        a, b = values[index, :, 0], values[index, :, 1]
        for line, y in zip(lines, [(a + b) / 2, (a - b) / 2, a], strict=True):
            line.set_data(xs, y)
        cursor.set_ydata([times[index], times[index]])
        label.set_text(f"t = {times[index]:.2f}   ·   c = 1   ·   linear superposition")
        return [*lines, cursor, label]

    animation = FuncAnimation(fig, update, frames=frames, interval=60)
    animation.save(output / "assets/travelling-waves.gif", writer=PillowWriter(fps=18), dpi=92)
    plt.close(fig)


def arm_state(theta):
    """Differentiate theta1 in the + channel, theta2 in the - channel."""
    a = float(theta[0]) + EPS * P_PLUS
    b = float(theta[1]) + EPS * P_MINUS
    return LENGTHS[0] * (I * a).exp() + LENGTHS[1] * (I * (a + b)).exp()


def arm_position_jacobian(theta):
    plus, minus = arm_state(theta).channels()
    position = np.array([plus[0].real, plus[0].imag])
    jacobian = np.array([[plus[1].real, minus[1].real], [plus[1].imag, minus[1].imag]])
    return position, jacobian


def arm_reference(theta):
    a, b = theta
    elbow = LENGTHS[0] * cmath.exp(1j * a)
    distal = LENGTHS[1] * cmath.exp(1j * (a + b))
    p = elbow + distal
    da, db = 1j * p, 1j * distal
    return np.array([p.real, p.imag]), np.array([[da.real, db.real], [da.imag, db.imag]])


def solve_arm(target, initial, tolerance=1e-10, max_iterations=60):
    """Damped least-squares IK using the two AD Jacobian columns."""
    theta = np.array(initial, dtype=float)
    for iteration in range(max_iterations):
        point, jacobian = arm_position_jacobian(theta)
        error = np.asarray(target) - point
        if np.linalg.norm(error) < tolerance:
            return theta, iteration
        step = np.linalg.solve(jacobian.T @ jacobian + 1e-8 * np.eye(2), jacobian.T @ error)
        step *= min(1.0, 0.3 / max(float(np.linalg.norm(step)), 1e-15))
        theta += step
    raise RuntimeError("Planar arm target did not converge")


def arm_path(count=361):
    t = np.linspace(0, math.tau, count)
    radius = 0.40 + 0.115 * np.cos(5 * t)
    targets = np.column_stack((1.13 + radius * np.cos(t), 0.28 + radius * np.sin(t)))
    angles, errors, iterations = [], [], []
    guess = [-0.65, 1.45]
    for target in targets:
        guess, count = solve_arm(target, guess)
        actual, _ = arm_position_jacobian(guess)
        angles.append(guess.copy())
        errors.append(float(np.linalg.norm(actual - target)))
        iterations.append(count)
    return targets, np.array(angles), np.array(errors), iterations


def arm_joints(theta):
    # Link endpoints are also evaluated through the ultracomplex exponential.
    elbow = LENGTHS[0] * (I * float(theta[0])).exp()
    tip, _ = arm_position_jacobian(theta)
    return np.array([[0, 0], [elbow.real, elbow.i], tip])


def render_robot(output, quick=False):
    targets, angles, errors, iterations = arm_path(121 if quick else 361)
    fig = plt.figure(figsize=(14, 8.5))
    title(
        fig,
        "09",
        "Draw a path. Let derivatives steer the arm.",
        "Planar inverse kinematics: one Ultra expression returns the endpoint and both Jacobian columns.",
    )
    ax = fig.add_axes((0.055, 0.16, 0.52, 0.61))
    ax.plot(targets[:, 0], targets[:, 1], color=FG, lw=2, label="requested path")
    selected = [int(f * (len(angles) - 1)) for f in [0.07, 0.27, 0.47, 0.67, 0.87]]
    for index in selected:
        joints = arm_joints(angles[index])
        ax.plot(*joints.T, c=CYAN, alpha=0.17, lw=2)
    index = selected[1]
    joints = arm_joints(angles[index])
    for k, color in [(0, CYAN), (1, PURPLE)]:
        ax.plot(*joints[k : k + 2].T, c=color, lw=5, solid_capstyle="round")
    ax.scatter(*joints.T, c=[FG, PURPLE, GOLD], s=[70, 60, 90], zorder=6)
    ax.scatter(*joints[-1], s=420, c=GOLD, alpha=0.12, zorder=5)
    point, jacobian = arm_position_jacobian(angles[index])
    for col, color in [(0, CYAN), (1, GOLD)]:
        ax.quiver(
            *point,
            *(jacobian[:, col] * 0.17),
            angles="xy",
            scale_units="xy",
            scale=1,
            color=color,
            width=0.007,
        )
    ax.set(xlim=(-0.2, 2.05), ylim=(-1.25, 1.1), xlabel="x", ylabel="y", aspect="equal")
    ax.set_title("Two links follow a five-lobed path", loc="left", fontsize=12)
    ax.legend(frameon=False, labelcolor=FG, loc="upper left")
    clean(ax)
    ax = fig.add_axes((0.68, 0.45, 0.25, 0.30))
    phases = np.linspace(0, math.tau, 361)
    circle = np.array([np.cos(phases), np.sin(phases)]) * 0.05
    for theta, color, label in [
        ([0.5, 1.2], CYAN, "bent elbow"),
        ([0.5, 0.04], GOLD, "almost straight"),
    ]:
        _, jacobian = arm_position_jacobian(theta)
        ellipse = jacobian @ circle
        ax.plot(*ellipse, c=color, lw=2, label=label)
    ax.set(xlabel="linearized Δx", ylabel="linearized Δy", aspect="equal")
    ax.set_title("What small joint changes can do", loc="left", fontsize=11)
    ax.legend(frameon=False, labelcolor=FG, fontsize=8, loc="lower left")
    clean(ax)
    fig.text(
        0.65,
        0.36,
        "A straight elbow loses one direction of motion.\nThe Jacobian exposes that singularity directly.",
        color=MUTED,
        fontsize=11,
        linespacing=1.6,
        va="top",
    )
    fig.text(
        0.65,
        0.235,
        f"{len(angles)} solved targets\nMaximum endpoint error: {max(errors):.2e}\nTypical updates per target: {np.median(iterations):.0f}",
        fontsize=12,
        linespacing=1.8,
        color=FG,
        va="top",
    )
    footer(
        fig,
        "Ideal 2-link planar arm · link lengths 1.2 and 1.0 · ellipse: joint step norm 0.05 rad",
    )
    save(fig, output / "assets/robot-inverse-kinematics.png")
    render_robot_animation(output, targets, angles, errors, quick)
    return {
        "targets": len(angles),
        "max_endpoint_error": float(max(errors)),
        "median_updates": float(np.median(iterations)),
    }


def render_robot_animation(output, targets, angles, errors, quick):
    fig = plt.figure(figsize=(8.8, 6.4))
    fig.text(
        0.075, 0.925, "TWO JOINTS. TWO DERIVATIVES. ONE EVALUATION.", fontsize=13, weight="bold"
    )
    fig.text(
        0.075,
        0.87,
        "The + and − channels differentiate different joint angles simultaneously.",
        fontsize=9.5,
        color=MUTED,
    )
    ax = fig.add_axes((0.08, 0.17, 0.66, 0.64))
    ax.plot(*targets.T, c=FG, alpha=0.2, lw=1.3)
    (trace,) = ax.plot([], [], color=GOLD, lw=2.3)
    (first,) = ax.plot([], [], color=CYAN, lw=5, solid_capstyle="round")
    (second,) = ax.plot([], [], color=PURPLE, lw=5, solid_capstyle="round")
    dots = ax.scatter([0, 0, 0], [0, 0, 0], c=[FG, PURPLE, GOLD], s=[55, 45, 70], zorder=6)
    ax.set(xlim=(-0.15, 1.95), ylim=(-1.25, 1.05), xlabel="x", ylabel="y", aspect="equal")
    clean(ax)
    fig.text(
        0.77,
        0.61,
        "CYAN\nfirst link\n\nPURPLE\nsecond link\n\nGOLD\ntraced path",
        color=MUTED,
        fontsize=10,
        linespacing=1.5,
        va="top",
    )
    label = fig.text(0.5, 0.065, "", ha="center", color=MUTED, fontsize=10)
    frames = 24 if quick else 100

    def update(frame):
        index = int(frame * (len(angles) - 1) / (frames - 1))
        joints = arm_joints(angles[index])
        first.set_data(*joints[:2].T)
        second.set_data(*joints[1:].T)
        dots.set_offsets(joints)
        trace.set_data(*targets[: index + 1].T)
        label.set_text(
            f"θ₁ = {angles[index, 0]:+.3f}   θ₂ = {angles[index, 1]:+.3f} rad   ·   error = {errors[index]:.1e}"
        )
        return first, second, dots, trace, label

    animation = FuncAnimation(fig, update, frames=frames, interval=60)
    animation.save(output / "assets/robot-path.gif", writer=PillowWriter(fps=18), dpi=94)
    plt.close(fig)


def interference_field(x, z, separation):
    """Two coherent scalar 3D point sources, sampled in the x-z plane (z>0)."""
    if z <= 0 or separation <= 0:
        raise ValueError("Positive detector distance and source separation required")
    offset = float(x) - J * (float(separation) + EPS) / 2
    radius = (offset * offset + float(z) ** 2).sqrt()
    return (I * (math.tau / WAVELENGTH) * radius).exp() / radius


def interference_intensity(x, z, separation):
    value = interference_field(x, z, separation)
    amplitude = 2 * complex(value.real, value.i)
    derivative = 2 * complex(value.eps, value.eps_i)
    # Fixed distance compensation makes screen intensities approximately order one.
    return abs(amplitude) ** 2 * z * z / 4, 2 * (
        amplitude.conjugate() * derivative
    ).real * z * z / 4


def interference_reference(x, z, separation):
    """Independent scalar propagators and their analytic distance derivatives."""
    field, derivative = 0j, 0j
    for sign in (1, -1):
        dx = x - sign * separation / 2
        r = math.hypot(dx, z)
        a = cmath.exp(1j * math.tau * r / WAVELENGTH) / r
        dr = -sign * dx / (2 * r)
        field += a
        derivative += a * (1j * math.tau / WAVELENGTH - 1 / r) * dr
    return abs(field) ** 2 * z * z / 4, 2 * (field.conjugate() * derivative).real * z * z / 4


def interference_observations():
    xs = np.linspace(-6, 6, 81)
    truth, distance = 2.4, 8.0
    exact = np.array([interference_reference(x, distance, truth)[0] for x in xs])
    observed = exact + np.random.default_rng(20261002).normal(0, 0.008, len(xs))
    return xs, observed, truth, distance


def fit_separation(xs, observed, distance, initial=2.0):
    separation = float(initial)
    history = []
    for _ in range(20):
        values = np.array([interference_intensity(x, distance, separation) for x in xs])
        residual, gradient = values[:, 0] - observed, values[:, 1]
        cost = float(np.dot(residual, residual))
        history.append((separation, cost))
        step = -float(np.dot(gradient, residual) / np.dot(gradient, gradient))
        if abs(step) < 1e-11:
            break
        for scale in (1, 0.5, 0.25, 0.125, 0.0625, 0.03125):
            candidate = separation + scale * step
            if not 0.2 < candidate < 5.0:
                continue
            changed = np.array([interference_intensity(x, distance, candidate)[0] for x in xs])
            if np.dot(changed - observed, changed - observed) < cost:
                separation = candidate
                break
        else:
            break
    return separation, np.array(history)


def render_interference(output, quick=False):
    xs, observed, truth, distance = interference_observations()
    fitted, history = fit_separation(xs, observed, distance)
    grid_x = np.linspace(-6, 6, 100 if quick else 260)
    grid_z = np.linspace(0.25, 10, 100 if quick else 260)
    intensity = np.array(
        [[interference_intensity(x, z, truth)[0] * 4 / (z * z) for x in grid_x] for z in grid_z]
    )
    fig = plt.figure(figsize=(14, 9))
    title(
        fig,
        "10",
        "Read geometry from an interference pattern.",
        "Recover the separation of two coherent sources using intensity measurements and an Ultra-derived gradient.",
    )
    ax = fig.add_axes((0.065, 0.15, 0.43, 0.62))
    im = ax.imshow(
        intensity,
        extent=(-6, 6, 0.25, 10),
        origin="lower",
        aspect="auto",
        cmap="magma",
        norm=LogNorm(vmin=0.0001, vmax=10),
    )
    ax.axhline(distance, color=CYAN, ls="--", lw=1.3)
    ax.text(5.7, distance + 0.15, "detector screen", color=CYAN, ha="right", fontsize=9)
    ax.scatter([-truth / 2, truth / 2], [0.25, 0.25], c=FG, s=45, marker="^")
    ax.set(xlabel="horizontal position x", ylabel="distance z")
    ax.set_title("Coherent point-source intensity |A|²", loc="left", fontsize=12)
    fig.colorbar(im, ax=ax, fraction=0.03, pad=0.025).set_label(
        "logarithmic color scale", fontsize=9
    )
    ax = fig.add_axes((0.60, 0.46, 0.355, 0.29))
    smooth = np.linspace(-6, 6, 601)
    for separation, color, label, style in [
        (2.0, PURPLE, "initial guess: d = 2.000", "--"),
        (fitted, CYAN, f"fitted: d = {fitted:.4f}", "-"),
    ]:
        curve = [interference_intensity(x, distance, separation)[0] for x in smooth]
        ax.plot(smooth, curve, c=color, label=label, lw=1.8, ls=style)
    ax.scatter(xs, observed, c=FG, s=12, alpha=0.85, label="synthetic noisy observations")
    ax.set(xlim=(-6, 6), xlabel="screen coordinate x", ylabel="scaled screen intensity")
    ax.set_title("The fringe spacing reveals the separation", loc="left", fontsize=11)
    ax.legend(frameon=False, labelcolor=FG, fontsize=8, loc="upper right")
    clean(ax)
    fig.text(
        0.60,
        0.36,
        f"TRUE SEPARATION      {truth:.4f}\nRECOVERED                   {fitted:.4f}\nABSOLUTE ERROR        {abs(fitted - truth):.4f}",
        fontsize=14,
        linespacing=1.8,
        color=GOLD,
        va="top",
    )
    fig.text(
        0.60,
        0.15,
        "Two complex channels store the two source fields.\nTheir ε parts supply the derivative used by the fit.",
        color=MUTED,
        fontsize=11,
        linespacing=1.6,
        va="top",
    )
    footer(
        fig,
        "Scalar point-source model · λ = 0.7 · synthetic Gaussian noise σ = 0.008 · local Gauss–Newton fit",
    )
    save(fig, output / "assets/interference-inverse-design.png")
    return {
        "true_separation": truth,
        "initial_separation": 2.0,
        "fitted_separation": fitted,
        "absolute_error": abs(fitted - truth),
        "history": history.tolist(),
        "noise_standard_deviation": 0.008,
        "noise_seed": 20261002,
    }


def verify_applications():
    wave_error, robot_error, optics_error = 0.0, 0.0, 0.0
    for x, t in [(-1.2, 2.1), (0.1, 3.0), (2.7, 4.8)]:
        actual, expected = wave_state(x, t).channels(), wave_reference(x, t)
        wave_error = max(
            wave_error,
            *(
                abs(a - b)
                for pair, ref in zip(actual, expected, strict=True)
                for a, b in zip(pair, ref, strict=True)
            ),
        )
    for theta in [[0.2, 0.7], [-0.4, 1.2], [1.4, 0.01]]:
        actual, expected = arm_position_jacobian(theta), arm_reference(theta)
        robot_error = max(
            robot_error, *(float(np.max(abs(a - b))) for a, b in zip(actual, expected, strict=True))
        )
    for x, z, d in [(1.3, 8.0, 2.4), (-0.7, 1.2, 1.8), (0.1, 3.4, 2.6)]:
        actual, expected = interference_intensity(x, z, d), interference_reference(x, z, d)
        optics_error = max(
            optics_error, *(abs(a - b) for a, b in zip(actual, expected, strict=True))
        )
    assert max(wave_error, robot_error, optics_error) < 1e-10
    return {
        "wave_channel_and_derivative_max_error": wave_error,
        "robot_position_and_jacobian_max_error": robot_error,
        "interference_intensity_and_gradient_max_error": optics_error,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("docs/gallery"))
    parser.add_argument("--quick", action="store_true")
    parser.add_argument(
        "--only", choices=["trigonometry", "waves", "robot", "interference", "all"], default="all"
    )
    args = parser.parse_args()
    (args.output / "assets").mkdir(parents=True, exist_ok=True)
    configure()
    report = verify_applications()
    for name, function in {
        "trigonometry": lambda: render_trigonometry(args.output),
        "waves": lambda: render_waves(args.output, args.quick),
        "robot": lambda: render_robot(args.output, args.quick),
        "interference": lambda: render_interference(args.output, args.quick),
    }.items():
        if args.only in (name, "all"):
            report[name] = function()
    if args.only == "all":
        (args.output / "applications-verification.json").write_text(
            json.dumps(report, indent=2) + "\n"
        )
    print(json.dumps(report, indent=2), flush=True)


if __name__ == "__main__":
    main()
