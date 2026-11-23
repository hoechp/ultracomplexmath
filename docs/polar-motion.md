# Polar coordinates, all roots and continuous motion

[Open the browser lab](https://raw.githack.com/hoechp/ultracomplexmath/master/docs/gallery/polar-motion.html) · [Offline file](gallery/polar-motion.html) · [Geometric derivation](research/geometric-structure.md)

## Draw your own field loop

In [the field lab](https://raw.githack.com/hoechp/ultracomplexmath/master/docs/gallery/field-loops.html), trace a polygon with a mouse or touchscreen, or load a preset. Predict the factor and close the loop. For the field `F(z) = z − j`, the plus channel sees `z − 1` and the minus channel sees `z + 1`. Each winding reverses its channel's square root. A loop around +1 gives −j, a loop around −1 gives j, a loop around both gives −1, and a loop around neither gives 1. Multiple turns follow the parity in each channel. The dashed closing edge counts. Touching either marked disk invalidates the lift. [Download the offline file](gallery/field-loops.html).

## Command line

```sh
ultracomplex '1+i+j/2' --polar --json
ultracomplex '1' --roots 2 --json
ultracomplex '0' --roots 3 --json
```

`--polar` returns the unit coordinates and both phases in radians. `--roots N` gives one representative per sheet in the public eight-coefficient order. In JSON, `count` is an integer or the string `"infinite"`. For an infinite family, `free_tangents` names the channels whose complex tangent can be freely chosen. Representatives use zero for those tangents. Both views use numerical arithmetic and accept `--legacy`. Use the default coefficient view for `--exact`.

## Follow a root around a loop

With `p = (1+j)/2`, the input `p*exp(i*t) + (1-p)` goes around the origin in
the plus channel and remains at one in the minus channel. Continuing the root
keeps its plus-channel phase at half the input phase. The plus root ends at −1,
the minus root at +1. Their combination is −j. A second lap returns to +1.

```python
from math import tau
from ultracomplexmath import EPS, I, J, ONE, ZERO, ModeOperator, Ultra

p = (ONE + J) / 2
previous = ONE.polar()
for k in range(1, 257):
    x = p * (I * (tau * k / 256)).exp() + (ONE - p)
    previous = x.polar(previous=previous)
    assert (previous.root() ** 2).isclose(x)
assert previous.root().isclose(-J)
```

For every numerical unit the coordinates are
$r\exp(j\rho+i\theta+ij\phi)(1+\varepsilon v)$.
The four-component body `v` holds the shear. Multiply two `PolarForm` values
to compose their scales, stretches, phases and shears, and call `.reconstruct()`
to recover the result in the coefficient basis. `.phases` gives the lifted
channel angles θ+φ and θ−φ. `.shifted(k,l)` adds 2πk and 2πl to them.
The corresponding changes of θ and φ are π(k+l) and π(k−l).

Continuation selects the nearest lifts. Sample each channel more finely than
half a revolution per step. An antipodal step is ambiguous, and a zero body
channel has no phase. Both raise `DomainError`. An undersampled complete turn
can have the same sampled endpoints as a constant path. Near a zero channel
phases are ill-conditioned. Reconstruction and noninteger powers use binary64
transcendental functions; branch angles that differ below float resolution
cannot be distinguished.

## Enumerate sheets or sample a root family

```python
from math import inf

assert set(ONE.roots().representatives()) == {ONE, -ONE, J, -J}
assert EPS.roots().count == 0
assert ZERO.roots().count == inf
root = ZERO.roots().at(plus_tangent=2 + 3j, minus_tangent=-4j)
assert root**2 == ZERO

family = ((ONE + J) / 2).roots(3)
assert family.strata == ("regular", "zero")
assert family.sheet_counts == (3, 1)
assert (family.at(2, minus_tangent=1j) ** 3).isclose((ONE + J) / 2)
```

For degree n ≥ 2, the equation in one channel is
$(u+\varepsilon v)^n=u^n+\varepsilon n u^{n-1}v=z+\varepsilon w$.

| Input channel | Roots |
| --- | --- |
| z ≠ 0 | n sheets. Each body root u fixes v = uw/(nz). |
| z = 0, w ≠ 0 | Empty. A root with zero body has zero nth power. |
| z = w = 0 | Any pure tangent εv. |

Combine the two channel families independently. `.count` gives the total
cardinality. `.representatives()` lazily yields one value per discrete sheet,
with zero for each free tangent. `.at()` selects zero-based sheet indices
and independent free complex parameters. Degree one returns the input.
`Ultra.sqrt()` continues to select the principal root.

## One differential equation, two physical systems

```python
from math import exp

# x'' + 2*zeta*x' + x = 0, with epsilon seeding a variation of zeta.
zeta = ONE + EPS
generator = ModeOperator.from_matrix(ZERO, ONE, -ONE, -2 * zeta)
initial = Ultra.from_channels((1, 0), (0, 0))  # displacement, velocity
(x, sensitivity), _ = generator.flow(1)(initial).channels()
assert abs(x - 2 / exp(1)) < 1e-12
assert abs(sensitivity - 1 / (3 * exp(1))) < 1e-12
```

The same state is displacement and velocity for a 1 kg mass with a 1 N/m spring,
or charge and current for a series RLC circuit with L = 1 H and C = 1 F.
Damping c = 2ζ N·s/m or resistance R = 2ζ Ω supplies the same normalized
equation. At ζ = 1 the critical response is (1+t)exp(−t). Its derivative
with respect to ζ there is t³exp(−t)/3 for these initial conditions.

`generator.flow(t)` is the numerical exponential of a **constant** complex-dual
2×2 generator. Centering the full trace gives B²=δI. The even and odd series in δ
extend through δ=0 and propagate the epsilon variation of the matrix, including
when the body and perturbation do not commute. Small scaled steps followed by
squaring cover positive and negative times. Unbounded growth, large phases and
ill-conditioned matrix exponentials remain subject to binary64 range and
conditioning. Exact rational Cayley steps and the [critical polynomial](research/novelty.md)
are available separately. Time-dependent generators require ordered evolution.

## Component accuracy

For small split arguments, sine and cosine use the complex addition formulas in
the defining basis. Their epsilon layers use the corresponding first derivative.
This preserves the mixed sine coefficients proportional to sinh²(h) in
1+ih+ijh+ε, tested down to h = 10⁻¹⁴⁰. Large split angles retain channel evaluation.
For a non-real reciprocal the core evaluates the represented binary fractions
exactly and rounds each output coefficient once. This costs more than two
floating-point divisions. General quotients with nonscalar numerator and
denominator still use direct channel division.

The browser lab contains samples generated from these APIs with
`python -m examples.polar_motion`. Both experiments and the two earlier labs
can run offline.
