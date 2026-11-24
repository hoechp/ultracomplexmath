"""Listen to a two-tap sum/difference filter. The phase input is e^(-i D omega)."""

from fractions import Fraction

from ultracomplexmath import QEPS, QI, QJ, QONE, ExactComplex, ExactUltra
from ultracomplexmath.exact import Rational, rational


def comb_response(phase: ExactComplex, delay_samples: int, gain: Rational = 1) -> ExactUltra:
    """Exact channels (1 ± g*phase)/(1+g), seeded with d/d(angular frequency)."""
    if not isinstance(phase, ExactComplex) or phase.determinant != 1:
        raise ValueError("The delayed phasor must lie on the Gaussian-rational unit circle")
    if type(delay_samples) is not int or delay_samples <= 0:
        raise ValueError("Delay must be a positive integer number of samples")
    g = rational(gain)
    if not 0 <= g <= 1:
        raise ValueError("Echo gain must lie between zero and one")
    echo = phase.to_ultra() * (1 - QEPS * QI * delay_samples)
    return (QONE + QJ * g * echo) / (1 + g)


def group_delays(response: ExactUltra) -> tuple[Fraction | None, Fraction | None]:
    """Minus the phase slope in samples. An exactly silent channel has no phase."""

    def delay(channel: tuple[ExactComplex, ExactComplex]) -> Fraction | None:
        h, dh = channel
        return -(dh / h).imag if h else None

    plus, minus = response.channels()
    return delay(plus), delay(minus)
