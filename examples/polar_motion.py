"""Build the standalone winding and damping lab from the public numerical APIs."""

import cmath
import json
import math
from pathlib import Path

from ultracomplexmath import EPS, ONE, ZERO, ModeOperator, Ultra

ROOT = Path(__file__).resolve().parents[1]
STEPS = 96
DAMPING_STEPS = 40


def winding(plus_turns: int, minus_turns: int) -> list[list[float]]:
    previous = None
    frames = []
    for k in range(2 * STEPS + 1):
        angle = math.tau * k / STEPS
        value = Ultra.from_channels(
            (cmath.exp(1j * plus_turns * angle), 0j), (cmath.exp(1j * minus_turns * angle), 0j)
        )
        previous = value.polar(previous=previous)
        root = previous.root()
        if not (root * root).isclose(value, abs_tol=3e-14):
            raise ArithmeticError("Square root left its path")
        frames.append([round(x, 9) for x in (*previous.phases, root.real, root.j, root.i, root.ij)])
    return frames


def response(damping: float) -> dict[str, object]:
    # With natural frequency 1, the two split channels store position and velocity.
    generator = ModeOperator.from_matrix(ZERO, ONE, -ONE, -2 * (damping + EPS))
    step = generator.flow(1 / 12)
    state = Ultra.from_channels((1, 0), (0, 0))
    values = []
    for _ in range(97):
        (x, dx), _ = state.channels()
        values.append([round(x.real, 8), round(dx.real, 8)])
        state = step(state)
    gap = cmath.sqrt(damping**2 - 1)
    return {"values": values, "modes": [[z.real, z.imag] for z in (-damping + gap, -damping - gap)]}


def main() -> None:
    samples = {
        "paths": [winding(p, m) for p, m in [(1, 0), (0, 1), (1, 1), (1, -1)]],
        "responses": [response(k / 20) for k in range(DAMPING_STEPS + 1)],
    }
    template = Path(__file__).with_name("polar_motion.html").read_text()
    (ROOT / "docs/gallery/polar-motion.html").write_text(
        template.replace(
            "__LAB_DATA__", json.dumps(samples, separators=(",", ":"), allow_nan=False)
        )
    )


if __name__ == "__main__":
    main()
