# Three concrete investigations beyond the demonstrations

[Research agenda](README.md) · [Rank proof](first-power-rank.md) · [Prototype code](../../examples/novelty_models.py) · [Full report](novelty-verification.json)

The strongest candidate is a **closed first-power rank classification for a subproblem explicitly left open in a recent paper**. Two smaller investigations produce an exact formula compression and a reproducible numerical improvement. All three have executable prototypes and independent checks. Only the first is a candidate for mathematical novelty, and its publication priority is unconfirmed.

| Investigation | Concrete result | What is new here | Assessment |
| --- | --- | --- | --- |
| Nilpotent operator ranks | A residue formula for every first-power block, and total defect L² or L(L+1) | Complete derivation and implementation for ℓ=1 | Strongest research candidate; known graph machinery; specialist prior-art review still needed |
| Critical motion plus parameter variation | A cubic exponential and a one-term exact Cayley correction | A compact, rationally exact prototype using existing `ModeOperator` | Useful simplification of established matrix-function mathematics |
| Tiny mixed reciprocal components | A guarded direct-basis evaluation retains second/third derivative information | Reproducible repair path for a documented accuracy gap | Numerical engineering, not a new algebraic identity |

The connection is **independent nilpotent directions**. An operator's critical geometry and the coefficient epsilon variation can coexist; their mixed product must survive. This leads naturally from the eight-dimensional scalar algebra to operators, their derivatives and rank questions. Arbitrarily large Jordan blocks are not encoded inside one `Ultra`. The rank investigation is an operator-side research extension, while the critical and reciprocal experiments directly use existing algebra types.

## 1. A small part of a real open problem

[Noferini, arXiv:2512.08399v5](https://arxiv.org/abs/2512.08399v5), Problem 4.19, requests a characterization of rank losses in structured Toeplitz blocks arising in matrix-function derivatives. We derive a complete formula **for power ℓ=1**, including rectangular blocks and all admissible sizes. Higher powers remain unresolved here.

The useful change of representation is simple: taking differences of a column containing an interval of ones leaves only its two endpoints. Columns become graph edges. Linear dependencies become cycles. For these particular bands, cycles can then be counted by integer residues. Summing the resulting block defects yields only squares or products of consecutive integers.

The [separate proof](first-power-rank.md) states every parameter and establishes both formulas. For example:

```python
from examples.novelty_models import first_power_defect, first_power_rank

assert first_power_defect(5, 5, 4) == 4
assert first_power_rank(5, 5, 4) == 5
# A rank computation for an implicit 10**36 by 10**36 operator:
n = 10**18
assert first_power_rank(n, n, n - 1) == n
```

The large example illustrates the formula's representation advantage; that special family's rank is not itself claimed novel. More generally, rank tells us how many independent perturbations a matrix function can see to first order. This could support symbolic sensitivity classification at singular operators. No engineering speed benchmark or new physical effect has been established.

**Next research target:** ℓ=2. Since

\[
(1-z)^\ell(1+z+\cdots+z^d)^\ell=(1-z^{d+1})^\ell,
\]

higher differences turn the untruncated convolution kernel into a sparse binomial stencil. A promising next step is to account for the finite-boundary terms and characterize the remaining dependencies. The identity is established algebra; a closed higher-power rank classification has not been derived here. A checked counterexample already prevents silently replacing weighted blocks by their supports.

## 2. Critical dynamics and sensitivity collapse to a cubic

Let A be a constant 2×2 matrix over complex-dual coefficients, represented by `ModeOperator`. Suppose its body has a repeated eigenvalue. Center the **full** trace, including epsilon:

\[
\mu=\tfrac12\operatorname{tr}A,\qquad B=A-\mu I.
\]

Cayley–Hamilton gives B²=δI. Criticality makes the body of δ zero, so δ²=0 and B⁴=0. Consequently,

\[
\boxed{e^{tA}=e^{t\mu}
\left(I+tB+\frac{t^2}{2}B^2+\frac{t^3}{6}B^3\right).}
\]

This is exact for the whole first variation. It is not a Taylor approximation in time. The scalar factor e^(tμ) may be transcendental; the rational implementation keeps it separate. Criticality concerns the body only: the perturbation may move the system away from criticality to first order.

For the existing Cayley map, define C_h=(I+hB/2)(I−hB/2)^(−1). Nilpotence gives

\[
C_h=I+hB+\frac{h^2}{2}B^2+\frac{h^3}{4}B^3,
\qquad
\boxed{e^{nhB}=C_h^n-\frac{nh^3}{12}B^3.}
\]

To see the second identity, C_h=e^(hB)(I+h³B³/12). These factors commute, (B³)²=0, and e^(nhB)B³=B³. Integer powers therefore yield exactly one correction term, also for negative n.

The cubic term can be essential. For B=[[0,1],[epsilon,0]], B²=epsilon I and B³ is nonzero. Reusing one scalar epsilon for both the operator nilpotent and the perturbation would erase this information. The matrix/operator distinction preserves it.

```python
from fractions import Fraction as F

from examples.novelty_models import (
    corrected_critical_cayley,
    critical_center,
    critical_polynomial,
)
from ultracomplexmath import QEPS, QONE, QZERO, ModeOperator

# Normalized oscillator: x'' + 2*(1+eps)*x' + x = 0.
a = ModeOperator.from_matrix(QZERO, QONE, -QONE, -2 * (QONE + QEPS))
mu, b = critical_center(a)
assert mu == -QONE - QEPS
assert corrected_critical_cayley(b, F(1, 7), 17) == critical_polynomial(b, F(17, 7))
# The full flow additionally has the scalar factor exp(-t)*(1-eps*t).
```

This supplies an exact reference for critical damping and for other specified constant critical two-mode models. It does not solve nonlinear dynamics, approximate near-critical bodies by critical ones, or remove time ordering for variable generators. The prototype rejects bodies that are merely close to critical.

The underlying mathematics follows established Fréchet/block-matrix methods, including [Al-Mohy and Higham (2009)](https://eprints.maths.manchester.ac.uk/1218/). The contribution here is the explicit specialization, the exact Cayley correction and its usable implementation, without a claim of first discovery.

## 3. A known reciprocal formula gives a real accuracy gain

Write x=a+jb+epsilon(c+jd), where a,b,c,d are ordinary complex numbers. If a²−b²≠0, then

\[
u=\frac{a-jb}{a^2-b^2},\qquad
\boxed{x^{-1}=u-\varepsilon u(c+jd)u.}
\]

This familiar conjugate identity follows from j²=1 and epsilon²=0. It avoids reconstructing tiny basis components by subtracting nearly equal split-channel answers. The prototype first scales a,b and deliberately excludes ill-conditioned cancellation in a²−b².

For f(x)=1/x, evaluate x=1+ih+ijh+epsilon. The quantities −[j]f(x)/h² and −[epsilon j]f(x)/h² approach f''(1)=2 and f'''(1)=−6. The test oracle is the exact rational result at the **actual floating-point input values**, so finite-step truncation and implementation error are distinguished.

| h | Existing inverse: second | Prototype: second | Existing inverse: third | Prototype: third |
| --- | --- | --- | --- | --- |
| 10^-8 | 2.22044604925 | 1.999999999999999 | −6.66133814775 | −5.999999999999995 |
| 10^-10 | 0 | 2 | 0 | −6 |
| 10^-100 | 0 | 2 | 0 | −6 |
| 10^-140 | 0 | 2 | 0 | −6 |

These are measured probe results, not guarantees for all reciprocal inputs. Additional exact-oracle tests vary every component and use scales 10^-150, 1 and 10^150. The scoped prototype is in `examples`, and the shipped inverse remains unchanged. Near-zero-divisor behavior, intermediate overflow/underflow and complementary evaluation charts need a broader accuracy contract before a core replacement.

A useful negative result: `log` retains the tiny component for this same probe family. Its possible numerical gaps must be demonstrated separately; this inverse experiment is not evidence of a logarithm failure.

## Reproduce and inspect

From an installed development checkout, with no additional numerical dependencies:

```sh
python -m pytest tests/test_novelty_models.py
python tools/novelty_probe.py
python tools/novelty_probe.py --full --output docs/research/novelty-verification.json
```

The default probe runs a smaller deterministic grid suitable for CI. The full report records source hashes, input ranges and counterexamples:

| Check | Full run | Independent reference |
| --- | --- | --- |
| Interval-band formula | 5,565 matrices | Fraction Gaussian elimination and graph union/find |
| Aggregate first-power formula | 1,638 triples / 12,869 blocks | Sum of individually eliminated blocks |
| Matrix-to-block correspondence | 196 full operators | Direct action on Q[x,y]/(x^m,y^n) monomials |
| Critical exponential and correction | 324 exact jets, 226 noncommuting body/variation pairs | Ordinary 4×4 Fraction block exponential; semigroup and negative-step checks |
| Reciprocal derivative components | 10 step sizes | ExactUltra at exact rational float inputs; componentwise checks |

## Sources and search boundaries

Reviewed on **2026-10-06**. This is a bounded public-source review, not a bibliographic novelty certification.

| Primary source | Role and boundary |
| --- | --- |
| [Noferini, arXiv:2512.08399v5](https://arxiv.org/abs/2512.08399v5) | Precise target: Definition 4.10, Proposition 4.16, Examples 4.15/4.17/4.18, Problem 4.19. The note addresses only ℓ=1. |
| [Evans, Greene, Van Veen, *Nullities for a class of 0–1 symmetric Toeplitz band matrices* (2021)](https://emis.de/ft/34371) | Graph-cycle prior art. Their symmetric zero-diagonal family differs from the rectangular bands with nonzero diagonal here. |
| [Al-Mohy and Higham, matrix exponential Fréchet derivative (2009)](https://eprints.maths.manchester.ac.uk/1218/) | Established matrix-function sensitivity and polynomial/rational evaluation framework. |
| [Luna-Elizarrarás et al., *Bicomplex Numbers and their Elementary Functions* (2012)](https://www.scielo.cl/pdf/cubo/v14n2/art04.pdf) | Established bicomplex algebra and inverse/function theory; no novelty claim for the conjugate identity. Their second imaginary unit differs from this project's split generator. |

Search families included the exact paper identifier/title and Problem 4.19; “Toeplitz rank consecutive ones”; and “Toeplitz nullity diagonal all ones.” Coverage was uneven, and no complete catalog of older interval/network-matrix results was checked. No identical aggregate formula was found in the inspected material. That absence is weak evidence of novelty. An independent mathematical review and deeper prior-art search remain the next gates for a publication claim.

The next implementation priorities are narrow: investigate the boundary equations for ℓ=2; extend reciprocal evaluation only after its excluded domains are analyzed; and use the cubic critical flow as a reference when building continuous operator functions. Reinterpreting algebra coefficients as spatial coordinates is unnecessary for all three investigations.
