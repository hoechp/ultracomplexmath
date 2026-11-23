# Four bars at dead centre

[Open the browser lab](https://raw.githack.com/hoechp/ultracomplexmath/master/docs/gallery/four-bar.html) · [Offline HTML](gallery/four-bar.html) · [Executable model](../examples/four_bar.py)

Two pivots are fixed at $A=(0,0)$ and $D=(3,0)$. The crank $AB$ and rocker $DC$
have length one and the coupler $BC$ has length three. Given the crank end $B$,
the position of $C$ is the intersection of the circle about $B$ of radius three
with the circle about $D$ of radius one. At each collinear pose the two
assemblies occupy the same position. Their velocities distinguish them.

## Two finite motions in one expression

Represent a planar vector by a complex number. Write $u=e^{i\theta}$ for the
crank. The parallelogram has $C=3+u$. Reflect its rocker $u$ across the line
with direction $u-3$ to obtain the other rocker. Reflection multiplies
$\bar u$ by $(u-3)/\overline{u-3}$. Substituting $\bar u=1/u$ gives
$(u-3)/(1-3u)$. The reflection and its simplified formula are well-defined on the unit circle.

With $s=3(1-j)/2$, both closed assemblies and their angular velocities follow from

$$
U=u(1+i\varepsilon),\qquad C=3+\frac{U-s}{1-sU}.
$$

In the $j=+1$ channel, $s=0$. In the $j=-1$ channel, $s=3$. The complex body
gives the joint position and the epsilon coefficient gives the velocity for
unit crank speed. Channel labels follow the same finite motion through a toggle.
Ordering the two circle intersections by which side of the centre line they
occupy would exchange labels there.

```python
from ultracomplexmath import QI, QJ, QEPS, QONE, ExactComplex

s = 3 * (QONE - QJ) / 2
u = 1 + QI * QEPS
parallel, reflected = (3 + (u - s) / (1 - s * u)).channels()
assert parallel == (ExactComplex(4), ExactComplex(0, 1))
assert reflected == (ExactComplex(4), ExactComplex(0, -2))
```

## What the constraint equations see

For each edge let $e=p_i-p_j$, $v=v_i-v_j$ and $a=a_i-a_j$. Differentiating
the fixed length condition $e\cdot e=L^2$ gives $e\cdot v=0$ and then
$e\cdot a=-v\cdot v$. A pin contributes two coordinate equations with zero
velocity and acceleration. The same rational matrix therefore supplies the
velocity nullspace, the response to prescribed driving velocities, and an
acceleration witness if the second system is consistent. This is the standard
second-order flex test for bar frameworks. [Connelly and Whiteley, *Second-Order Rigidity and Prestress Stability for Tensegrity Frameworks*](https://pi.math.cornell.edu/~connelly/pdf/10.1137_S0895480192229236.pdf)

```python
from ultracomplexmath import BarFramework2D, InconsistentSystemError

bars = ((0, 1), (1, 2), (2, 3))
regular = BarFramework2D(((0, 0), (0, 1), (3, 1), (3, 0)), bars, pins=(0, 3))
assert len(regular.velocity_basis()) == 1
assert regular.solve_velocity({1: (-1, 0)})[2] == (-1, 0)

pose = ((0, 0), (1, 0), (4, 0), (3, 0))
assert not any(regular.position_residuals(pose))
toggle = BarFramework2D(pose, bars, pins=(0, 3))
assert len(toggle.velocity_basis()) == 2
trial = ((0, 0), (0, 0), (0, 1), (0, 0))
assert not any(toggle.first_order_residuals(trial))
try:
    toggle.acceleration_for(trial)
except InconsistentSystemError:
    pass
else:
    raise AssertionError("This velocity has no compatible acceleration")
```

At a toggle, both moving joints have vertical velocities. Let $v$ and $w$
denote the vertical speeds of $B$ and $C$. The acceleration equations give the
following exact compatibility conditions.

| Crank end | Output position | Velocity condition | Slopes $w/v$ for $v\ne0$ |
| --- | --- | --- | --- |
| $B=(1,0)$ | $C=(4,0)$ | $(w-v)(w+2v)=0$ | $1,\ -2$ |
| $B=(-1,0)$ | $C=(2,0)$ | $(w-v)(2w+v)=0$ | $1,\ -1/2$ |

For example, at the inner toggle the crank and rocker impose $a_{Bx}=-v^2$
and $a_{Cx}=-w^2$. The coupler then gives $3(v^2-w^2)=-(w-v)^2$.
The entire two-dimensional velocity plane passes the first-order equations.
Exactly two lines extend to second order. For **this linkage** the two explicit
finite assembly laws above realize every velocity on those lines, by rescaling
crank speed. For an arbitrary framework, a compatible acceleration alone leaves
finite mobility undecided. At regular poses the input determines the output
uniquely. At a toggle, `solve_velocity` reports a free linearized response.

## Exact circle intersections

`circle_intersection2d` takes two centres and their **squared** radii.
It distinguishes an empty set, a point, a pair and coincident positive-radius
circles. For a pair it retains the rational midpoint $M$, direction $n$
and squared factor $q$, giving the real points $M\pm n\sqrt q$. Calling
`rational_points()` returns coordinates when the full finite set is rational.
An irrational pair or infinite family raises `DomainError`.

```python
from fractions import Fraction
from ultracomplexmath import circle_intersection2d

cut = circle_intersection2d((0, 1), 9, (3, 0), 1)
assert set(cut.rational_points()) == {(3, 1), (Fraction(12, 5), Fraction(-4, 5))}
lens = circle_intersection2d((0, 0), 1, (1, 0), 1)
assert lens.kind == "pair" and lens.radicand == Fraction(3, 4)
```

The standalone lab samples one turn with four rational Cayley charts. Its exact
circle intersections, independent bar equations and two closed assembly laws
are cross-checked before display. Rebuild with `python -m examples.four_bar`.
