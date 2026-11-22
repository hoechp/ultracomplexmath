# Applications worth pursuing

[Agenda](README.md) · [Geometric structure](geometric-structure.md) · [Operations](operations.md) · [Roadmap](roadmap.md) · [Implemented showcase](../gallery/README.md)

The ranking favors the shared geometric structure and exact coefficients. The [geometric investigation](geometric-structure.md) derives the links behind the proposals: damping regimes, optical cells, polarization/Lorentz invariants and the tangent quadric. Derivative applications remain valuable without defining the project's identity. Projects below are proposals unless identified as implemented examples; accuracy, speed and usability advantages require appropriate baselines.

## Implemented engineering baselines

The [engineering showcase](../gallery/impact.md) now supplies three concrete baselines: lossless two-polarization optical stacks with thickness sensitivity; a two-parameter coating-impedance fit with local frequency information; and damped midpoint dynamics through criticality with exact differentiated dissipation. A [fourth demo](../formula-compression.md) proves the packed-solve identity and states its computational cost. These are bounded examples built on existing APIs, not general optical, electrochemical or ODE solvers.

## Candidate comparison

| Priority | Application | Combined contribution | Starting point | Main missing capability |
| --- | --- | --- | --- | --- |
| 1 | Exact geometric constraints/calibration | C rotations, S alternate geometric forms, D variations | Exact predicates, Cayley isometries, matrices, curves | Constraint graph, implicit derivatives, rank events, algebraic coordinates |
| 2 | Structure-preserving critical dynamics | Circular, hyperbolic and parabolic regimes of one equation, with rational invariants | Exact Cayley operators and checked damping classification | Continuous functions, time-step control, complete generator metadata |
| 3 | Optical cells, polarization and wave transfer | C phase, S reciprocal scales/null structure, D shear and critical behavior | Mode operators, exact optical/Stokes checks, projectivities | Physical components, coherency/Stokes API, scattering composition, conditioning |
| 4 | Full polar geometry and projective continuation | Shared scale, two phases, hyperbolic scale, shear and tangent-quadric charts | Log/exp, projective points, cross ratios, derived polar and chart laws | Structured polar object, branches, singular strata, quadric incidence and real structures |
| 5 | Harmonic, wave and contact-field models | Different analyticity equations encode different geometric laws | Scalar functions, polynomial examples and derived CR relations | Domain/regularity definitions, characteristic and integral machinery, boundary-value models |
| 6 | Higher derivatives of geometry and thermodynamic potentials | `i` and `ij` probe curvature; epsilon adds parameter differentiation | Corrected exponential and polynomial calculus | Stable mixed-component primitives and derivative API |
| 7 | Frequency-domain identification | Complex response, split modes, dual derivatives | Interference fit and coupled motion | Arrays, response blocks, noise/uncertainty and passivity models |
| 8 | Finite coefficients and polynomial lifting | Field-specific C/S factors and nilpotents | Scalar residues, exact polynomials, exhaustive F2 probe | Modular backend, Hensel/Hasse, reconstruction |

The complete polar form is foundational mathematics rather than an engineering solver. Its immediate application is an explorer that follows phase winding, reciprocal stretching and shear through products, then shows what breaks at each zero-divisor stratum. The projective follow-up tracks the same constructions across finite and infinite charts. Both should retain the exact/rational representation wherever the coordinates permit it.

## Exact constraints: geometry that remains auditable

A linkage/CAD constraint can use rational points, quadrances and Cayley parameters. Dual seeds give an exact rational Jacobian. Exact rank distinguishes regular and singular configurations without a tolerance. The current planar robot demo is a numerical baseline, not an exact constraint engine.

**First deliverable:** a closed linkage represented by a constraint graph. Compute exact residuals, Jacobians and admissible infinitesimal motions at rational configurations. Check regular and singular cases against independent geometry.

Circular joints, indefinite constraints and shear/deformation variables can share construction and differentiation. Every physical robot need not use all three. Generic circle intersections require irrational coordinates: retain constraints implicitly or introduce a scoped algebraic-number domain. At a singular configuration, an infinitesimal motion need not integrate into a finite motion.

## Higher derivatives: geometry meets thermodynamic response

CS is bicomplex: `i` and `ij` commute and both square to minus one. Mixed steps expose second derivatives if elementary algorithms preserve the small component. Epsilon differentiates that probe with respect to an additional parameter.

This connects geometric curvature/calibration Hessians to **thermodynamic potentials**: derivatives relate pressure, response and material sensitivity. Deiters and Bell document established multicomplex methods in thermodynamics [R4](references.md). The proposal here is an application of the existing union and exact polynomial models, not a claim of a new differentiation method.

**First deliverable:** a bounded analytic potential with one mixed Hessian entry and its parameter derivative, checked against symbolic formulas and independent high precision over step sizes. Report requested-coefficient errors.

Division, logarithm and other primitives need the same care as the corrected exponential. Piecewise branches, absolute values and physical phase transitions invalidate naive analytic-step assumptions. This package currently supplies neither a thermodynamic solver nor a general Hessian API.

## Dynamics across circular, hyperbolic and critical regimes

For `B_kappa=[[0,1],[kappa,0]]`, `B_kappa²=kappa*I`. Entire functions of kappa express the exponential without taking a singular derivative of `sqrt(kappa)` at zero. Exact Cayley maps already cover all three regimes discretely.

**Implemented baseline:** the [vibration demo](../gallery/impact.md#3-vibration-settling-through-critical-damping) compares rational midpoint steps with independent continuous solutions across critical damping. It checks second-order convergence, parameter derivatives, exact differentiated dissipation and the nonvanishing product of the critical Jordan operator with epsilon. General continuous operator functions and step control remain open. The established midpoint context is documented by Hairer [R5](references.md).

Exact geometry and numerical evolution can share generators and invariants. But invariant preservation does not guarantee trajectory accuracy. Fraction denominators grow; Cayley poles, time-step choice and damping/loss models require explicit handling. General noncommuting perturbations require a Fréchet derivative.

## Optical layers, wave interfaces and impedance

A complex pair can represent forward/backward fields. Interfaces and layers mix them; a component ratio evolves by a Möbius map. Suitable lossless optical transfer models belong to SU(1,1), linking them to Lorentz geometry [R6](references.md). Circular phase, indefinite flux and observable intensity are thus closely connected.

Epsilon carries thickness, refractive-index or frequency sensitivity through a network. Transmission-line impedance and Riccati propagation share this **mathematical pattern**, with different physical meanings and admissibility conditions.

**Implemented baseline:** the [optical demo](../gallery/impact.md#1-antireflection-coatings-with-manufacturing-tolerances) composes a small lossless stack with stated field conventions, both polarizations and thickness sensitivity. It checks Fresnel recursion, R+T and its derivative, and a sampled design/tolerance problem. Optical parameter recovery, stable long-stack scattering and loss remain open; the separate impedance demo supplies an inverse-problem baseline in a different physical model.

Long stacks and evanescent fields can make transfer matrices ill-conditioned. Provide scattering composition and conversions alongside them. Loss, total internal reflection and normalization affect the relevant metric/group; SU(1,1) is not a universal label. Full 3D Maxwell simulation is outside this first project.

## Projective continuation: a coordinate pole can be traversable

For a matrix `[[a,b],[c,d]]` acting on `(x,y)`, the ratio evolves as `(a*r+b)/(c*r+d)`. Its affine denominator can cease to be a unit while the homogeneous state remains valid. Different split factors may require different charts; `ProjectivePoint` already handles this.

**First deliverable:** continue a parameterized family through an affine pole, preserving homogeneous data and first variations. Compare with the underlying linear evolution and record chart changes separately from physical singularities.

This brings together projective calibration, impedance/Riccati evolution and mode networks. Automatic charts and boundary events are still absent. Non-unimodular homogeneous pairs remain invalid; chart changes cannot repair them.

## Signals, fitting and uncertainty

Extend the current wave/interference examples with explicit response blocks, weighted real residuals and covariance propagation through a Jacobian. Amplitude, phase and power are different observations with different singularities.

**Implemented baseline:** the [coating-impedance demo](../gallery/impact.md#2-impedance-diagnostics-identify-the-parameters-not-just-a-curve) estimates two positive resistances using one complex solve with two tangent channels. Synthetic observations come from an independent series/parallel formula. The example reports weighted residuals, known-noise local information and the collapse of identifiability in a restricted frequency band. Real data, nuisance parameters and model selection remain open.

Arrays and reusable factorizations are likely essential to performance. Epsilon is a derivative, not a noise distribution. Phase needs zero handling and path unwrapping. Compare equal outputs/accuracy against ordinary complex arrays plus an established AD library before claiming a speed advantage.

## Finite coefficients and exact lifting

Over odd prime fields the algebra's factors depend on whether −1 is a square. Over F2, `i+1`, `j+1` and epsilon are three square-zero generators. The [probe](experiments.md#finite-coefficients) checks all 256 elements.

**First deliverable:** direct-basis modular coefficients, unit detection and serialization; then simple-root Hensel steps with exact lifted residuals. Singular roots and p=2 need separate rules. Hasse derivatives avoid invalid factorial division in positive characteristic.

Uses include modular verification, rational reconstruction and scoped multiplicity-evaluation/coding experiments [R9/R10](references.md). This does not establish a new cryptographic primitive; generic RSA exercises have been separated.

## Additional directions

| Direction | Why it belongs | Remaining work |
| --- | --- | --- |
| Conics, chains and rational curves | C/S/D projective geometry connects exact constructions and transfer diagrams | Incidence definitions, degeneracy and algebraic intersections |
| Lie/Clifford or matrix poses | Spatial mechanisms require noncommuting rotations/translations | A separate representation with explicit laws/dimension; scalar Ultra is not a dual quaternion |
| Bifurcation and repeated modes | Retain a critical generator when eigenvalue coordinates coalesce | Jordan/Schur-aware methods, rank events and conditioning |
| Certified computation | Exact rational constructions supply numerical reference data | Interval/ball arithmetic or independent high precision with error contracts |
| PDE interface methods | Split characteristics naturally combine with complex phase | Boundary operators, discretization accuracy, dispersion and stability |

The testable research question is whether a coherent algebraic interface improves composition, verification or numerical reliability in a specified task. The union does not automatically solve every application.
