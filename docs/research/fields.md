# What the spatial extension makes possible

[Field guide](../fields.md) · [Field showcase](../gallery/fields.md) · [Roadmap](roadmap.md)

The implemented construction is a field of values in the existing algebra, with an independent real domain. It is naturally a section of the trivial algebra bundle `M × A -> M`: in ordinary language, each point carries the same number system. Specifying a field does not yet specify a physical law. Geometry and equations determine how neighbouring values relate.

## Three structures that fit together

For a real coordinate `x`, differentiation acts on all eight coefficient functions. Multiplication remains the original multiplication, so the usual product rule holds for differentiable fields. The current finite-difference implementation approximates these derivatives; it does not make discrete differentiation an exact derivation.

Writing `F = A + eps*B`, with `A,B` in the complex/split-complex subalgebra, gives

$$\partial_x F=\partial_x A+\varepsilon\partial_x B.$$

This exposes a useful mixed quantity: if `B` already represents a parameter sensitivity, the epsilon part of the spatial derivative measures how that sensitivity changes in space. No additional scalar generator is needed. Independent higher parameter jets would still require a separate construction.

The two split idempotents `(1±j)/2` are constant, so spatial derivatives, integrals and scalar geometric operators preserve their decomposition into two complex-dual channels. A pointwise polynomial equation splits into two channel equations; it does not create interactions between channels by itself. A chosen coupled operator or model is required for such interactions. A display containing both channels should not be mistaken for proof of physical coupling.

## A wave and its sensitivity obey related, different equations

Let `c` be a positive real speed, `k` a real wave vector and `omega = |k|`. For an explicitly chosen wave model,

$$A(x,t;c)=\exp\bigl(i(k\cdot x-c\omega t)\bigr),\qquad
F=A(x,t;c+\varepsilon)=A+\varepsilon\partial_cA.$$

The body satisfies `L_c A = 0`, where `L_c = c^-2 ∂t² - Δ`. Differentiating this equation with respect to `c` gives

$$L_c(\partial_c A)=\frac{2}{c^3}\partial_t^2 A
=\frac{2}{c}\Delta A.$$

Consequently `L_c F` need not vanish in its epsilon component. That component is the response to changing a coefficient of the equation itself. `tests/test_fields.py` checks both the homogeneous body and this inhomogeneous sensitivity against their analytic expressions, along with coordinate derivatives of every coefficient down to very small tangent scales.

This is immediately useful for model fitting, sensitivity maps and inverse problems. It is evidence for compatible mathematics, not evidence that epsilon physically *is* time, spin or a spacetime dilation.

## The metric affects the equation

For an embedding `X(u,v)` with Jacobian `J`, the induced metric is `g=JᵀJ`. The implementation uses

$$\nabla_M F=Jg^{-1}\begin{pmatrix}\partial_uF\\\partial_vF\end{pmatrix},\qquad
\Delta_MF=\frac{1}{\sqrt{\det g}}\partial_a\left(\sqrt{\det g}\,g^{ab}\partial_bF\right).$$

These act coefficientwise while preserving algebraic products. The formula is the standard local-coordinate Laplace–Beltrami operator; see the University of Toronto [lecture on coordinate Laplacians](https://www.math.toronto.edu/courses/mat394h1/20139/L22.html). The tests use independent closed expressions rather than a second implementation of the same stencil.

For a torus with major radius `R` and minor radius `r`,

$$g=\operatorname{diag}((R+r\cos v)^2,r^2),\qquad
\Delta_M e^{imu}=-\frac{m^2}{(R+r\cos v)^2}e^{imu}.$$

Even this simple mode has a position-dependent geometric factor. Using an ordinary parameter-space Laplacian would miss it. A stretched plane gives another check: the surface Laplacian of `x²+y²` is `4`, independent of the parameter stretching. Surface quadrature reproduces the torus area `4π²Rr` to rounding accuracy on the stated periodic midpoint grids.

These operators supply building blocks for waves, diffusion or reaction models on a specified surface. This release evaluates operators; it does not solve initial/boundary value problems. Diffusion requires a chosen evolution equation and suitable positivity/stability properties; it does not follow from dual analyticity.

## Topology restricts which formulas are admissible

On a Möbius strip the equivalence is `(u+2π,v) ~ (u,-v)`. Neither `v` nor `sin(u/2)` alone descends to an ordinary scalar field on the strip. Their product does:

$$(-v)\sin((u+2\pi)/2)=v\sin(u/2).$$

Similarly, `v*cos(u/2)` is well-defined. This gives nontrivial, smoothly compatible ultracomplex formulas such as the one in the showcase, without changing any coefficient's interpretation. Transverse coordinate derivatives flip sign at the seam, but the embedded tangent gradient is the same vector of Ultra values on both sides. Tests check values, derivatives, gradients and Laplacians across this transition.

The strip has no consistent global normal direction, yet its positive area density and scalar integration remain meaningful. A field with a deliberate sign, conjugation or internal rotation across a seam would instead require a specified nontrivial bundle and transport law; the current API does not silently introduce one.

## What would make the next extension worthwhile?

1. **A concrete evolution model:** choose a wave or diffusion equation, boundary conditions and observables, then add a convergent solver with independent residual/conservation checks.
2. **Explicit transport:** specify what it means to compare values in changing internal frames. A connection should be motivated by that model; coordinates alone do not determine one.
3. **General geometry:** add chart transitions and a caller-supplied metric, with tensor transformation tests. Lorentzian metrics are a separate extension from the positive surface metrics implemented here.
4. **Physical interpretation:** state units, symmetries, an action/evolution law and measurable predictions before interpreting polar parameters as spacetime or spin. A familiar parameter count is insufficient.

The current extension supports these investigations while keeping the scalar algebra, external geometry and model assumptions independently testable.
