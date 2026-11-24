# Five experiments with three imaginary units

The original Java gallery drew the same exponential in three different planes. These five experiments start with that question of interpretation and take it in different directions.

| Question | Experiment |
| --- | --- |
| How many exact square roots does one number have? | Enumerate the rational sheets and parameterize the free tangents. |
| How far do the same initial data determine a field? | Change the square of the generator while keeping two polynomial traces fixed. |
| What surface contains the two projective channels? | Construct both rulings of the Segre quadric and recover the factors, including tangents at infinity. |
| What can an optical measurement see? | Convert Jones amplitudes to Stokes observables and propagate partially polarized light. |
| What does a zero divisor sound like? | Listen to complementary comb filters and measure group delay on either side of a spectral null. |

[Open the interactive experiments](https://raw.githack.com/hoechp/ultracomplexmath/master/docs/gallery/five-experiments.html) · [Download the offline HTML](gallery/five-experiments.html)

## All rational square roots

One equation in each Gaussian-rational channel determines the answer. If $(u+εv)^2=z+εw$ and $z$ is nonzero, each Gaussian-rational square root $u$ fixes $v=w/(2u)$. To find $u=a+ib$ exactly, compute $r=\sqrt{(\Re z)^2+(\Im z)^2}$, $a^2=(r+\Re z)/2$, and $b^2=(r-\Re z)/2$. Each required square root must have a square numerator and denominator. The imaginary part of $z$ fixes the relative sign when both components are nonzero. The two channel signs are independent.

If $z=0$, a nonzero $w$ rules out every square root. When both vanish, any $v$ works. One such channel paired with a solvable channel gives countably infinitely many rational roots.

```python
from ultracomplexmath import ExactComplex, QEPS, QI, QJ, QONE, QZERO

plus, minus = (QONE + QJ) / 2, (QONE - QJ) / 2
assert set((-QONE).square_roots().representatives()) == {QI, -QI, QI * QJ, -QI * QJ}
family = plus.square_roots()
assert family.sheet_counts == (2, 1)
assert family.at(1, minus_tangent=ExactComplex(2, -3)) ** 2 == plus
assert (2 * QONE).square_roots().count == QEPS.square_roots().count == 0
```

From the command line run `python -m ultracomplexmath "(1+j)/2" --exact --roots 2 --json` to see the two sheets and the free minus-channel tangent.

The two empty cases above have different explanations. The real number 2 needs irrational coefficients. The pure tangent ε has no square root even over real coefficients. `.sqrt()` still returns the principal rational representative where it exists.

## One pair of Cauchy data

Write $z=x+uy$ with $u^2=s$. Prescribe $U(x,0)=f(x)$ and $U_y(x,0)=g(x)$ for real rational polynomials. Let $G'=g$. With $[1]$ and $[u]$ denoting the two coefficient projections, one formula solves three equations,

$$U(x,y)=[1]f(z)+[u]G(z),\qquad U_{yy}=s U_{xx}.$$

Indeed, two derivatives in $y$ multiply a polynomial's second derivative by $u^2$. On $y=0$ the two projections recover the prescribed data. The PDE determines each successive coefficient in $y$, which proves uniqueness among polynomials. The wave case also gives d'Alembert's half-sum of the two translated traces plus half the difference of the translated primitives. For $s=0$ the result reduces to $f(x)+yg(x)$. Harmonic continuation here takes exact polynomial data. General noisy elliptic Cauchy data can be ill-conditioned.

```python
from ultracomplexmath import CIRCULAR, HYPERBOLIC, PARABOLIC, ExactPolynomial, PolynomialCauchyField

f, g = ExactPolynomial([0, 0, 1]), ExactPolynomial([1])
planes = (CIRCULAR, HYPERBOLIC, PARABOLIC)
assert [PolynomialCauchyField(p, f, g)(2, 3) for p in planes] == [-2, 16, 7]
```

## Two rulings and a tangent

Two homogeneous channel points $[s:t]$ and $[u:v]$ give four complex-dual coordinates $[su:sv:tu:tv]$. Arrange them as a two-by-two matrix. Its determinant vanishes in both body and tangent. Conversely, any nonzero body entry supplies a unit pivot. Its column recovers the first factor and its row recovers the second, each up to its own invertible scale. The inverse therefore works in all four charts.

```python
from ultracomplexmath import ProjectivePoint, SegreQuadricPoint

p = ProjectivePoint((2 + QEPS) * plus + minus, plus + QEPS * minus)
q = SegreQuadricPoint.from_projective(p)
assert q.su * q.tv == q.sv * q.tu
assert q.to_projective().equivalent(p)
```

The plotted saddle is the real slice $[ab:a:b:1]$. Varying only $a$ or only $b$ traces a line. If both increase at unit speed, the vertical velocity is $a+b$. The Python API also covers complex coordinates, rational derivatives and points at infinity. The [geometric derivation](research/geometric-structure.md#the-projective-completion-is-tangent-geometry-on-a-quadric) explains the underlying tangent bundle.

## Light and its observable phase

The split channels store Jones amplitudes $u,v$. The coherency cross term $H_{12}=u\bar v=(S_2+iS_3)/2$ fixes our sign convention. A common phase cancels. A relative phase rotates $(S_2,S_3)$ and remains observable. For partially polarized light, propagate the coherency matrix by $H\mapsto GHG^\dagger$. Four times its determinant is $S_0^2-S_1^2-S_2^2-S_3^2$, including its epsilon derivative.

```python
from ultracomplexmath import ExactStokes, ModeOperator

mixed = ExactStokes(2, 0, 1, 0)
plate = ModeOperator.from_matrix(QI * (1 + QI * QEPS), QZERO, QZERO, QONE)
out = mixed.through(plate)
assert out == ExactStokes(2, 0, -QEPS, 1)
assert out.interval == mixed.interval == 3 * QONE
assert ExactStokes.from_coherency(out.coherency()) == out
```

The plate is evaluated at a quarter-turn and ε measures change per radian. The implementation accepts exact nondepolarizing Jones elements, including singular ideal analyzers. Physical input bodies lie in the future intensity cone. A two-sided differentiable state at a nonzero boundary point has tangent derivative of the interval zero. At darkness, every such first variation vanishes. Partially polarized input may be specified directly. [Han, Kim and Noz, *Stokes Parameters as a Minkowskian Four-vector*](https://arxiv.org/abs/physics/9707016).

## Hear one channel disappear

With direct gain one, echo gain $g$ and delay $D$ samples, the two transfer functions share an expression,

$$H(ω)=\frac{1+jg\exp(-iDω)}{1+g}.$$

The sum channel adds the delayed copy and the difference channel subtracts it. Substituting $ω+ε$ supplies $H'$ in the same arithmetic. Group delay in samples is $-\Im(H'/H)$ in each nonzero channel. At full echo gain it is $D/2$ wherever the channel survives. A zero output has undefined phase and group delay.

```python
from examples.comb_filter import comb_response, group_delays

# 1500 Hz at 48000 samples/s with D=48: exp(-i D omega) = -1.
response = comb_response(ExactComplex(-1), 48)
assert response.primal == minus
assert group_delays(response) == (None, 24)
assert response.tangent != QZERO
```

The sound lab covers one fringe from 1 to 2 kHz. A rational parametrization of the unit circle gives exact amplitudes and derivatives at each plotted sample, including both cancellation points. Displayed frequencies, plots and audio use floating point. Playback synthesizes a finite, faded excerpt of the steady-state sinusoid. Changing gain to ½ removes the exact null even at the same frequency. [Julius O. Smith, *Phase and Group Delay*](https://www.dsprelated.com/freebooks/filters/Phase_Group_Delay.html).

## Reproduce

Run `python -m examples.five_experiments` from an installed checkout to regenerate the self-contained page. Open it in a browser and choose an experiment. Playback starts on a button press. Run `python -m pytest tests/test_five_experiments.py` for exact coefficient, PDE, projective, optical and independent discrete Fourier checks and a comparison with the shipped page.
