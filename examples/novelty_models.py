"""Scoped research prototypes, not public core APIs.

See docs/research/novelty.md for proofs, prior art, domains and counterexamples.
The rank formula addresses only the first power in Noferini's Problem 4.19.
The critical-flow identity is a Cayley–Hamilton consequence; the reciprocal
uses an established conjugate identity with a deliberately restricted domain.
"""

from __future__ import annotations

from fractions import Fraction

from ultracomplexmath import (
    QONE,
    QZERO,
    DomainError,
    ExactUltra,
    ModeOperator,
    NonInvertibleError,
    Ultra,
)

QIDENTITY = ModeOperator(QONE, QZERO)
QNULL = ModeOperator(QZERO, QZERO)


def _integer(name: str, value: int, minimum: int = 0) -> None:
    if type(value) is not int:
        raise TypeError(f"{name} must be an integer, not bool or float")
    if value < minimum:
        raise ValueError(f"{name} must be at least {minimum}")


def _band_domain(rows: int, columns: int, degree: int, offset: int) -> None:
    _integer("rows", rows, 1)
    _integer("columns", columns, 1)
    _integer("degree", degree)
    _integer("offset", offset)
    if not 0 <= offset <= degree or not 0 <= columns - rows + offset <= degree:
        raise ValueError("The top-left and bottom-right band entries must both be 1")


def interval_band(rows: int, columns: int, degree: int, offset: int) -> list[list[int]]:
    """R[i,j] = 1 iff 0 <= j-i+offset <= degree, with both corner entries 1."""
    _band_domain(rows, columns, degree, offset)
    return [[int(0 <= j - i + offset <= degree) for j in range(columns)] for i in range(rows)]


def interval_band_rank(rows: int, columns: int, degree: int, offset: int) -> int:
    """Exact rank over any field, using a fixed number of integer operations.

    No matrix is allocated. Integer bit costs still grow with parameter size.
    The proof turns interval columns into edges and counts boundary-to-boundary
    paths. This is NOT a formula for arbitrary weighted Toeplitz bands.
    """
    _band_domain(rows, columns, degree, offset)
    if rows < columns:
        rows, columns, offset = columns, rows, degree - offset
    period = degree + 1

    def count(end: int) -> int:
        cycles, tail = divmod(end, period)
        return cycles * (period - offset) + max(0, tail - offset)

    paths = count(columns + offset) - count(rows - 1)
    return columns - max(0, paths - 1)


def _jordan_domain(m: int, n: int, degree: int) -> None:
    _integer("m", m, 1)
    _integer("n", n, 1)
    _integer("degree", degree, 1)
    if m > n:
        raise ValueError("Use m <= n (interchanging the two Jordan factors is allowed)")


def toeplitz_shape(m: int, n: int, degree: int, power: int, k: int) -> tuple[int, int, int]:
    """Rows, columns, offset in Noferini, Definition 4.10 (arXiv v5)."""
    _jordan_domain(m, n, degree)
    _integer("power", power, 1)
    _integer("k", k, 1)
    total = power * degree
    if not total + 1 <= k <= m + n - 1:
        raise ValueError("k must index an existing block: power*degree+1 <= k <= m+n-1")

    def width(index: int) -> int:
        return min(index, m, n, m + n - index)

    return width(k - total), width(k), min(total, max(0, k - n))


def toeplitz_block(m: int, n: int, degree: int, power: int, k: int) -> list[list[int]]:
    """Explicit small block; coefficients of (1+z+...+z**degree)**power.

    This reference construction allocates the requested block. Use the closed
    first-power functions for large parameters, not this small-experiment helper.
    """
    rows, columns, offset = toeplitz_shape(m, n, degree, power, k)
    coefficients = [1]
    for _ in range(power):
        following = [0] * (len(coefficients) + degree)
        for i, value in enumerate(coefficients):
            for j in range(degree + 1):
                following[i + j] += value
        coefficients = following
    return [
        [
            coefficients[index] if 0 <= (index := j - i + offset) < len(coefficients) else 0
            for j in range(columns)
        ]
        for i in range(rows)
    ]


def first_power_defect(m: int, n: int, degree: int) -> int:
    """Sum of rank losses relative to each block's maximum possible rank.

    Complete first-power formula; no claim about powers >= 2. Its proof and
    publication-novelty status are separate in the accompanying research note.
    """
    _jordan_domain(m, n, degree)
    overlap = m - n + degree
    if degree >= m + n - 1 or overlap <= 0:
        return 0
    residue = m % (degree + 1)
    height = max(min(overlap, residue - 1), overlap - residue)
    length = max(0, height - (overlap + 1) // 2)
    return length * (length + overlap % 2)


def first_power_rank(m: int, n: int, degree: int) -> int:
    """Rank of sum(N_m**i tensor N_n**(degree-i), i=0..degree).

    Unlike the block construction, this needs neither matrices nor a sum over k.
    """
    _jordan_domain(m, n, degree)
    if degree >= m + n - 1:
        return 0
    span = m + n - degree
    peak = min(m, span // 2)
    return peak * (span - peak) - first_power_defect(m, n, degree)


def _exact_operator(operator: ModeOperator[ExactUltra]) -> None:
    if not isinstance(operator, ModeOperator) or type(operator.alpha) is not ExactUltra:
        raise TypeError("This experiment requires an ExactUltra ModeOperator")


def _rational(value: int | Fraction) -> Fraction:
    if isinstance(value, bool) or not isinstance(value, (int, Fraction)):
        raise TypeError("Use an integer or Fraction, without implicit float conversion")
    return Fraction(value)


def critical_center(
    operator: ModeOperator[ExactUltra],
) -> tuple[ExactUltra, ModeOperator[ExactUltra]]:
    """A = mu*Id+B, requiring a repeated body eigenvalue; trace(B)=0 exactly.

    exp(t*A) = exp(t*mu)*critical_polynomial(B,t). The scalar prefactor is kept
    separate: a generic transcendental exponential is not an ExactUltra value.
    """
    _exact_operator(operator)
    matrix = operator.matrix()
    mu = (matrix[0][0] + matrix[1][1]) / 2
    centered = operator - QIDENTITY.scaled(mu)
    _critical_domain(centered)
    return mu, centered


def _critical_domain(centered: ModeOperator[ExactUltra]) -> None:
    _exact_operator(centered)
    matrix = centered.matrix()
    if matrix[0][0] + matrix[1][1] != QZERO:
        raise ValueError("Center the full trace, including its epsilon part, first")
    body = ModeOperator(centered.alpha.primal, centered.beta.primal)
    if body @ body != QNULL:
        raise ValueError("The centered body must square to zero; near-critical is insufficient")


def critical_polynomial(centered: ModeOperator[ExactUltra], time: int | Fraction):
    """Exact exp(time*B) = Id+tB+t²B²/2+t³B³/6 under the stated domain."""
    _critical_domain(centered)
    t = _rational(time)
    return (
        QIDENTITY
        + centered.scaled(QONE * t)
        + (centered**2).scaled(QONE * (t**2 / 2))
        + (centered**3).scaled(QONE * (t**3 / 6))
    )


def corrected_critical_cayley(centered: ModeOperator[ExactUltra], step: int | Fraction, steps: int):
    """Exact exp(n*h*B) = Cayley(h*B/2)**n - n*h³*B³/12.

    Valid also for zero/negative integer n. This is a constant critical-jet
    identity, not a generic nonlinear or time-dependent integration method.
    """
    _critical_domain(centered)
    if type(steps) is not int:
        raise TypeError("steps must be an integer")
    h = _rational(step)
    cayley = centered.cayley(QONE * (h / 2))
    return cayley**steps - (centered**3).scaled(QONE * (steps * h**3 / 12))


def direct_reciprocal(value: Ultra) -> Ultra:
    """Conjugate-form reciprocal protecting small mixed body components.

    Experimental domain: the normalized a²-b² must be separated from zero by
    1e-8*(|a|²+|b|²). This is an explicit scope guard, not a singularity test.
    Tangent products must stay representable; there is no general underflow or
    near-zero-divisor guarantee. No public inverse implementation is replaced.
    """
    if type(value) is not Ultra:
        raise TypeError("Use a numerical Ultra explicitly")
    a, b = complex(value.real, value.i), complex(value.j, value.ij)
    if a == b or a == -b:
        raise NonInvertibleError("A body channel is zero")
    scale = max(map(abs, value.coefficients[:4]))
    a, b = a / scale, b / scale
    denominator = a * a - b * b
    if abs(denominator) <= 1e-8 * (abs(a) ** 2 + abs(b) ** 2):
        raise DomainError("The reciprocal experiment excludes near-zero-divisor cancellation")
    p, q = (a / denominator) / scale, (-b / denominator) / scale
    body = Ultra(p.real, q.real, p.imag, q.imag)
    return body.with_tangent(-(body * value.tangent) * body)
