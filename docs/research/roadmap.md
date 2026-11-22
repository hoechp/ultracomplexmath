# Prioritized implementation roadmap

[Agenda](README.md) · [Geometric structure](geometric-structure.md) · [Operations](operations.md) · [Applications](applications.md)

Reviewed against 0.3.0 and updated for 0.5.0. **P0** protects numerical correctness; **P1** continues exact coefficients and geometry; **P2** broadens application coverage. Proposed APIs below are not imports.

Version 0.5.0 ships the [UltraField foundation](../fields.md): independent real space/time coordinates, located values, lazy numerical fields, slices, sampling, coordinate derivatives, torus/Möbius geometry, induced surface calculus and optional array adapters. These implement specific parts of G08/G12/G13/G18/G19; they do not complete a PDE solver, general geometric transport or independent higher parameter jets. See the [field consequences](fields.md) for verified identities and the next model-driven steps.

The geometric follow-up adds G16–G19 and changes the suggested sequence: full polar structure, critical dynamics and projective geometry lead the applications. Existing derivative proposals remain useful parts of the toolkit.

The [engineering showcase](../gallery/impact.md) now gives bounded baselines for G05/G14/G19: a two-polarization optical stack with tolerance prediction, an identifiable impedance fit with frequency-information analysis, and discrete critical damping with exact differentiated energy balance. Its [formula audit](../formula-compression.md) also makes G10 concrete: the current packed solve repeats the shared body solve rather than reusing a factorization. These examples do not complete continuous operator functions, general scattering networks or application validation against measured devices.

## Correctness before new promises

The huge-integer exponent bug is fixed: `I**(2**53+1)==I`. Rational coefficients, exact matrices/polynomials and geometry are implemented. The renewed review found a different defect: channel reconstruction erased the `j` coefficient of `exp(1+i*h+ij*h)`. Version 0.4.0 uses component-preserving factors and scaled real exponentials, with tests down to h=`1e-100` and large compensated split exponents.

The same accuracy risk remains in other operations, including channel-based logarithm and inverse. A dominant body can be accurate while a tiny mixed coefficient is wrong. The frontier probe reports this explicitly; a general bicomplex Hessian API would currently promise too much.

The [novelty investigations](novelty.md) now supply a guarded inverse prototype for G01 and an exact cubic critical-flow reference for G05/G19. The reciprocal tests demonstrate a specific inverse failure; the logarithm succeeds on that same family. Neither prototype is a general replacement for the core APIs. On the operator side, a [closed first-power rank derivation](first-power-rank.md) addresses a subproblem in current literature; deeper prior-art review and the higher-power boundary equations are the next research targets.

## Work packages

| ID / priority | Gap | Next deliverable | Completion evidence |
| --- | --- | --- | --- |
| G01 / P0 | Componentwise accuracy and near-zero functions | Audit inverse/division/log/trig; stable selected paths, `expm1`, `log1p`, `sinc`, `sinhc` | Independent analytic/high-precision scale sweeps; coefficient errors; branch, range, underflow and compensated-large cases |
| G02 / P1 | Rational powers whose result is rational | Exact nth-root detection and explicit rational-power branches, starting with real/closed inputs | Cube root of 8, negative odd roots, reciprocals, irrational/singular cases and exact powered-back identities |
| G03 / P1 | Coefficient-domain extensibility | Minimal shared coefficient protocol; scoped algebraic/high-precision adapters | Same basis laws, domains and serialization; no implicit float conversion |
| G04 / P1 | Exact constraints and implicit geometry | Constraint graph, rational Jacobians, exact rank/free motions and regular implicit sensitivities | Closed linkage/CAD examples; independent singularity classification; infinitesimal versus finite motion distinguished |
| G05 / P1 | Continuous dynamics and matrix functions | Entire `C_kappa/S_kappa`, operator exponential/Fréchet derivative, midpoint time-step interface | Critical limits, independent ODE/matrix oracle, convergence order, invariant and differentiated identities |
| G06 / P1 | General derivative interface | JVP/seed helpers, real-linear contracts, scoped bicomplex Hessian entries and epsilon variations | Analytic oracles, non-holomorphic contracts, step/underflow diagnostics, repeated-seed Jacobians |
| G07 / P1 | Angles and projective continuation | Derivative-aware `atan2`, phase/sector histories and chart events | Loops/cuts/zeros/null rays/mixed-chart poles; agreement with homogeneous evolution |
| G08 / P1 | Conics and spatial geometry | Incidence, algebraic intersections, separate 3D pose/operator layer | Exact degeneracies/transformed incidence; noncommuting pose composition |
| G09 / P2 | Polynomial algebra over a ring | Nonunit-leading division strategy, factor/root metadata, resultants and rational splines | Degenerate/zero-divisor examples; field assumptions explicitly checked |
| G10 / P1 | Reusable and conditioned linear algebra | Factorizations, condition/rank diagnostics, repeated RHS, adjoints and sparse adapters | Exact residuals, independent references, singular families and scale tests |
| G11 / P2 | Modular hypercomplex coefficients | Full `A_(Z/nZ)`, unit algorithms, Hensel/Hasse and reconstruction | Exhaustive small rings including F2, odd-prime factors, lifted residuals/nonunit failures |
| G12 / P2 | Integration, transforms, special functions | Selected derivative-preserving quadrature/response APIs and FFT adapter | Scalar/complex references, branch/singularity contracts and convergence evidence |
| G13 / P2 | Ecosystem interoperability | NumPy batching/ufunc policy, schemas, units and AD boundaries | Round trips, dtype/shape errors and benchmarks with equal requested work |
| G14 / P2 | Validated application components | One transfer/scattering network, observations, fit and noise model | Model-specific conservation/passivity, independent solver, derivatives and identifiability |
| G15 / P1 | Complete root families | Independent sheets, tangent families and singular classifications; exact counterparts where supported | n² unit roots, empty/infinite cases, residuals and path consistency |
| G16 / P1 | Full polar structure and singular strata | Structured eight-parameter unit decomposition, coupled phase lattice, multiplication and zero-divisor classifications | Reconstruction across scales; branch-loop histories; singular boundaries; agreement with G01 accuracy contracts |
| G17 / P1 | Geometric models and real structures | Quadric/tangent-chart adapters, coherency/Stokes conversions and explicit reality conditions | Exact quadric/tangent incidence, all chart overlaps, positivity and determinant invariants; physical model assumptions retained |
| G18 / P2 | Analysis over the three geometries | Specified analytic domains, Cauchy–Riemann operators, characteristic/contour examples and scoped mixed extensions | Independent harmonic/wave/contact examples; characteristic singularities and boundary data; no identification of dual analyticity with diffusion |
| G19 / P1 | Independent geometric and perturbation directions | Explicit direction semantics; separate nilpotent operators or an optional larger coefficient algebra when two roles are required | Nonvanishing mixed-direction examples; deliberate truncation rules; no silent reuse of one epsilon for independent variables |

## Suggested sequence

**Milestone A: trustworthy exact and polar geometry.** G01, the small rational-root portion of G02, G16 polar/stratum structure and G04 exact constraints. Deliver polar reconstruction with correct branch metadata and a closed-linkage showcase with exact residuals. Introduce G03 abstractions around concrete coefficient needs; use G06 helpers where they serve the geometry.

**Milestone B: motion and charts.** G05 generalized functions with existing exact Cayley steps, plus G07 continuation. Show one oscillator and one optical cell across all three motion regimes. Include G17 tangent chart transitions and apply G19 whenever geometric and perturbation nilpotents meet.

**Milestone C: a full-union application.** G14's optical/transfer network with G17 Stokes/coherency observables and the relevant G10/G13 pieces. Connect phase, boosts, shears and projective observations. Compare transfer/scattering stability and solve an identifiable inverse problem.

**Research branches:** develop the G18 field-equation foundations and the G17 quadric/null-geometry interpretation with explicit domains and reality conditions. After G01, investigate bicomplex/dual higher derivatives on a thermodynamic potential. Modular G11 work can proceed independently. These are dependency recommendations, not implementations already underway.

## Decisions that remain explicit

- Full-algebra order, floor, remainder and probability need chosen semantics; naming them does not inherit real-number laws.
- Exact coefficient domains must state their closure. Q excludes generic radicals; a small algebraic extension excludes generic transcendental values.
- The epsilon ideal alone gives first-order jets. Arbitrary exact higher jets need a larger algebra; bicomplex finite steps are a different opportunity within the current algebra.
- A finite geometric shear and a parameter derivative can require independent square-zero directions. G19 must preserve that distinction; adding a second scalar generator changes the eight-dimensional coefficient algebra.
- General 3D poses need noncommuting operators or another extension. Keep scalar, operator and point types distinct.
- Accuracy contracts must identify protected components, not merely a body-dominated total norm.

No existing benchmark establishes an advantage over specialized arrays or established AD libraries. Compare equal requested outputs and accuracy in each concrete application.
