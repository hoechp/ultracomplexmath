# Circular, hyperbolic and parabolic geometry together

[Documentation](README.md) · [Exact arithmetic](exact-arithmetic.md) · [Operations atlas](research/operations.md)

The library makes the full union of complex, split-complex and dual geometry
usable through common constructions. It supplies intrinsic metrics and angles,
rational isometries, exact Euclidean predicates, noncommuting coupled operators
and projective geometry over the complete eight-dimensional algebra. Mixed
directions remain ordinary algebra components throughout these constructions.

![Rational constructions in the three geometries and coupled motion](gallery/assets/rational-geometry.png)

Reproduce the exact demonstrations with `python -m examples.exact_geometry`.
Add `--plot` after installing `.[plot]` to regenerate this figure. Every plotted
point is first computed and checked using fractions; conversion to float is
only for display. The motion panel depicts discrete Cayley steps.

## One plane interface, three meanings

Write `z=x+u*y` with `u*u=s`. The intrinsic quadratic form and its associated
bilinear form are

$$Q_s(z)=x^2-sy^2,\qquad \langle z,w\rangle_s=xx'-syy'.$$

| API | Generator | Quadratic form | Angle parameter | Transformation | Typical application |
| --- | --- | --- | --- | --- | --- |
| `CIRCULAR` | `i²=-1` | `x²+y²` | Radians, modulo a turn | Rotation | Planar mechanisms, phasors, Euclidean constructions |
| `HYPERBOLIC` | `j²=1` | `x²-y²` | Rapidity plus sector | Lorentz boost | 1+1 spacetime, paired expansion/contraction, transfer geometry |
| `PARABOLIC` | `eps²=0` | `x²` | Slope/shear plus orientation | Shear | First-order deformation, affine shear, Galilean-type coordinates |

`plane.point(x,y)` produces a numerical closed value; `plane.exact(x,y)` an
exact rational closed value. `.quadrance(value)` selects the intrinsic form,
and `.classify(value)` distinguishes regular, null, timelike/spacelike or
positive/negative sectors as appropriate. `metric_dot`, `metric_project` and
`metric_reflect` require values from the same algebra and coefficient domain.

Projection uses `n * <v,n>/Q(n)`; reflection with normal `n` is
`v - 2*n*<v,n>/Q(n)`. A null direction cannot be used as the denominator.
In the dual plane the form is degenerate: nonzero vectors can have zero
quadrance. This is part of the geometry, not a rounding error.

These intrinsic operations have separate names from historical Euclidean
display helpers. For example, `Binary.length` remains a Euclidean coordinate
length. It has not been relabelled as a Lorentz norm. A `Mobius` map below is
projective and does not automatically preserve one of these metrics.

## Angles, sectors and exact trigonometric data

`plane.rotor(parameter)` returns the numerical exponential `exp(u*parameter)`:
`cos(t)+i*sin(t)`, `cosh(t)+j*sinh(t)` or `1+eps*t`.
`plane.polar(point)` returns `PlanePolar(kind, radius, parameter, sector)`;
`.reconstruct()` restores the point. Exact points require an explicit
`.approximate()` before numerical angle extraction.

Complex geometry has the principal `atan2` angle and sector `(1,0)`. Split
geometry keeps all four sector units `(±1,0)` and `(0,±1)`, a positive radius
`sqrt(abs(x²-y²))`, and rapidity. Dual geometry keeps `abs(x)`, orientation
`sign(x)` and shear `y/x`. Null points and zero have no finite polar angle.
`plane.angle_between(start,end)` extracts the form of `end/start`, preserving
the relative scale and sector instead of returning an ambiguous single float.
Its direction is **from start to end**; the historical `.angle_to()` convention
remains unchanged.

Rational rotations and boosts need no irrational angle or transcendental
evaluation. For a rational chart parameter `t`, use the shared Cayley formula:

$$R_s(t)=\frac{1+ut}{1-ut}
       =\frac{1+st^2}{1-st^2}+u\frac{2t}{1-st^2},\qquad Q_s(R_s(t))=1.$$

```python
from fractions import Fraction as F
from ultracomplexmath import CIRCULAR, HYPERBOLIC, PARABOLIC

assert CIRCULAR.cayley(F(1, 2)) == CIRCULAR.exact(F(3, 5), F(4, 5))
assert HYPERBOLIC.cayley(F(1, 2)) == HYPERBOLIC.exact(F(5, 3), F(4, 3))
assert PARABOLIC.cayley(F(1, 2)) == PARABOLIC.exact(1, 1)
```

Here `t=tan(theta/2)`, `t=tanh(rapidity/2)` in the identity split sector, and
`t=shear/2` respectively. The circular chart misses `-1`; the split chart has
poles at `t=±1`. Split values with `|t|>1` lie in the opposite timelike sector.
This does not claim every angle has rational sine/cosine. It supplies exact
geometric factors when a rational chart is appropriate.

### Translation, reflection and composition

`PlaneIsometry(factor, translation, reflected=False)` applies
`factor*z + translation`, or `factor*conjugate(z) + translation` when reflected.
The factor must have unit quadrance (exactly for fractions, within tolerance
for numerical input). Composition is `A @ B`, meaning apply `B` first.
`.inverse()` and `.homogeneous_matrix()` preserve the coefficient domain.

```python
from ultracomplexmath import PlaneIsometry

move = PlaneIsometry(CIRCULAR.cayley(F(1, 2)), CIRCULAR.exact(F(2, 3), 1), True)
p = CIRCULAR.exact(7, F(3, 5))
assert move.inverse()(move(p)) == p
```

The matrix acts on `(x,y,1)` and retains Fraction entries in the exact case.
Differences between points preserve their quadratic form. In the parabolic
plane these transformations form the shear/translation/reflection subgroup;
they are not the whole linear group preserving the degenerate form `x²`.
Large numerical boosts can lose their unit-quadrance identity through binary64
cancellation and be rejected by validation; exact Cayley factors avoid that
rounding problem.

## Exact geometric decisions and constructions

For Euclidean affine coordinates, the following helpers accept two-component
sequences of integers/Fractions and reject floats:

| API | Result and meaning |
| --- | --- |
| `orientation2d(a,b,c)` | Signed twice-area, with exact sign and exact collinearity |
| `line_intersection2d(a,b,c,d)` | Unique rational intersection of two infinite lines; parallel/coincident or degenerate lines raise |
| `segment_intersection2d(a,b,c,d)` | Empty tuple, one point, or endpoints of an overlapping closed segment; point segments are supported |
| `barycentric2d(p,a,b,c)` | Three exact weights summing to one; rejects a collinear triangle |
| `circumcircle2d(a,b,c)` | Rational center and radius **squared**, avoiding an unnecessary irrational root |
| `incircle2d(p,a,b,c)` | `+1` inside, `0` on, `-1` outside, independent of triangle winding |

A translation by `10**100` does not erase a separation of `1/10**100`.
This is useful for CAD constraints, exact intersections, triangulation predicates
and reproducible geometric fixtures. These helpers specify Euclidean geometry;
an incircle test is not automatically a hyperbolic or parabolic incircle test.

## Coupled operators: composition adds new capabilities

The scalar algebra remains commutative. Its geometry can nevertheless use
noncommuting operators. With `sigma(x)=x.conjugate("j")`, define

$$T(x)=\alpha x+\beta\sigma(x).$$

`ModeOperator(alpha,beta)` supports application, addition, subtraction,
composition, integer powers, determinant, inverse, output scaling and Cayley
transforms. Both `Ultra` and `ExactUltra` work; mixing coefficient domains is
explicitly rejected.

The composition rule follows directly from `sigma²=Id`:

$$(\alpha,\beta)\circ(\gamma,\delta)
=(\alpha\gamma+\beta\sigma(\delta),\;
  \alpha\delta+\beta\sigma(\gamma)).$$

In a split-mode basis this is a full 2×2 matrix over the complex-dual algebra.
`ModeOperator.from_matrix(a,b,c,d)` accepts entries with no `j` components;
`.matrix()` returns that matrix. This representation verifies the operator
and gives access to genuinely interacting modes; it does not redefine the
purpose of the underlying eight-dimensional numbers. A general operator has
16 real/rational components acting on an eight-component state.

Let `S(x)=sigma(x)` and `J(x)=j*x`. Then `S²=J²=Id`, `SJ=-JS`,
`(JS)²=-Id`, and `(J+JS)²=0`. Thus the operator layer contains circular,
hyperbolic and nonzero parabolic generators while retaining the original
complex/split/dual state algebra. Tests verify these identities directly.

### Rational motion through the parabolic transition

Choose the retained matrix generator

$$B_\kappa=\begin{pmatrix}0&1\\\kappa&0\end{pmatrix},\qquad B_\kappa^2=\kappa I.$$

Its Cayley map is

$$C_h(B_\kappa)=(I+hB_\kappa)(I-hB_\kappa)^{-1}
=\frac{1}{1-\kappa h^2}
\begin{pmatrix}1+\kappa h^2&2h\\2\kappa h&1+\kappa h^2\end{pmatrix}.$$

It describes circular, hyperbolic and parabolic rational step maps for negative,
positive and zero kappa. It is regular at kappa zero and retains the generator
there. It preserves `y²-kappa*x²` exactly for rational inputs. The poles at
`1-kappa*h²=0` remain explicit.

```python
from ultracomplexmath import ExactUltra, ModeOperator, QZERO, QONE, QEPS

# kappa = 0, with a first variation in kappa.
B = ModeOperator.from_matrix(QZERO, QONE, QEPS, QZERO)
step = B.cayley(ExactUltra(F(1, 3)))
assert step.matrix()[0][0] == QONE + F(2, 9) * QEPS
assert step.matrix()[0][1] == F(2, 3) * QONE + F(2, 27) * QEPS
```

The epsilon coefficients are exact parameter sensitivities at the critical
case; no derivative of `sqrt(kappa)` is taken. `step` must be in the central
complex-dual subalgebra so it commutes with the generator operator.

A Cayley step is a rational discrete motion law. It is generally an
approximation to `exp(2hB)`, not that exponential itself. Continuous-time
generalized sine/cosine, damping envelopes and stable matrix exponential
derivatives remain future work. This distinction prevents an attractive
discrete demonstration from claiming a solved continuous ODE problem.

## Projective geometry over all eight components

`Mobius(a,b,c,d)` represents `(a*z+b)/(c*z+d)` and requires its determinant
`a*d-b*c` to be a unit. It supports composition and inversion.
`cross_ratio(a,b,c,d)` uses `(a-c)*(b-d)/((a-d)*(b-c))` and is invariant under
these maps whenever all displayed affine denominators are units.
Epsilon coefficients carry the derivative of the complete rational map,
including changes to its coefficients.

For an affine chart boundary use `ProjectivePoint(x,y)`. Valid coordinates are
**unimodular**, meaning that `a*x+b*y=1` has a solution. For this algebra the
test is explicit: in each complex body component, at least one of `x` or `y`
must be nonzero. Merely checking the eight-component pair is not both zero
would be wrong. The criterion follows because the algebra is a product of
two complex-dual local rings, whose units are exactly nonzero bodies.

```python
from ultracomplexmath import QJ, Mobius, ProjectivePoint

p, m = (QONE + QJ) / 2, (QONE - QJ) / 2
boundary = ProjectivePoint(p, m)
assert boundary.charts == ("x", "y")
swap = Mobius(QZERO, QONE, QONE, QZERO)
assert swap.apply_projective(boundary) == ProjectivePoint(m, p)
assert swap.apply_projective(swap.apply_projective(boundary)).equivalent(boundary)
```

Neither coordinate here is a unit, yet together they are valid homogeneous
coordinates. `.affine()` correctly refuses to divide by `m`; `.charts`
indicates which coordinate can be a denominator in each mode.
`.equivalent()` checks projective equality, exactly for fractions and with an
explicit tolerance for floats. Structural `==` compares stored representatives.
`[1:0]` is also valid; `[eps:0]` is not. No fake infinity or NaN is inserted.

This creates a practical starting point for projective calibration, fractional
transfer laws and geometric continuation near null-divisor boundaries. Chart
selection is exposed, while a general automatic path-continuation engine and
complete circle/chain incidence library are not yet supplied. The underlying
definition follows the established projective line over a ring, described by
[Havlicek](https://arxiv.org/abs/1210.1921); the specialized criterion above is
derived for this algebra.

## Measurements connecting geometry to applications

The numerical `Ultra` API provides `.primal`, `.tangent`, `.with_tangent`,
`real_part()`, `imag_part()`, `abs2()`, `amplitude()` and `phase()`.
The last two return real values and real directional derivatives in each split
mode; they are not presented as holomorphic functions:

$$d|z|=\operatorname{Re}(\bar z\,dz)/|z|,\qquad
d\arg z=\operatorname{Im}(dz/z),\qquad
d|z|^2=2\operatorname{Re}(\bar z\,dz).$$

Phase at a zero body is rejected. Amplitude at a zero with nonzero tangent is
also rejected as nondifferentiable. At the negative real phase cut the value
is `+pi`; the tangent is the local **unwrapped** phase derivative. Automatic
path unwrapping is not implied. The exact backend supplies the polynomial
observables and tangent operations; amplitude and phase require explicit
numerical conversion when they leave rational coefficients.

These measurements let exact geometry, coupled complex fields and calibration
share derivatives without confusing `.real` (one coefficient) with a
derivative-preserving real projection.

## Continue the geometry

The [geometry inside the full union](research/geometric-structure.md) derives a complete unit polar form and connects critical dynamics, optical transformations, field equations and the projective tangent quadric. The [research roadmap](research/roadmap.md) prioritizes the missing polar/branch APIs, exact constraints, continuous critical dynamics and projective constructions. [Application proposals](research/applications.md) connect them to calibration, optics and mechanics. Those pages distinguish implemented primitives from missing higher-level solvers.

## Verification and references

The geometry tests check exact quadratic invariants, independent homogeneous
matrix action, affine inverse/composition, all split sectors, exact degenerate
intersections, independent matrix coupling, cross-ratio invariance, invalid
projective coordinates, mixed charts and analytic first variations. The full
pre-existing numerical suite also passes with the regression fixes.

For background, see the authors' [split-complex geometry text](https://books.physics.oregonstate.edu/GELG/csplit.html),
[Kisil's elliptic/parabolic/hyperbolic treatment](https://arxiv.org/abs/0707.4024),
and [Havlicek's projective ring-line survey](https://arxiv.org/abs/1210.1921).
The Cayley identities and critical-parameter derivatives above are direct
derivations, independently checked by the rational tests in this repository.
