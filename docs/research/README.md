# Research agenda: the full union in use

[Documentation](../README.md) · [Geometric structure](geometric-structure.md) · [Operation atlas](operations.md) · [Applications](applications.md) · [Roadmap](roadmap.md) · [Evidence](references.md)

This review starts from **complex, split-complex and dual algebra as a full union**, including all mixed directions. Its central question is which geometries, invariants and physical structures become understandable and computable together. Derivative extraction is one useful consequence; it does not exhaust the meaning of the additional directions.

Begin with [the geometry inside the full union](geometric-structure.md): a complete polar form, three regimes of the same dynamical equation, optics/Lorentz connections, and the projective tangent quadric. Then use the operation atlas and roadmap to turn those structures into reliable interfaces.

For implemented physical-model examples, the [engineering showcase](../gallery/impact.md) now follows these ideas into optical tolerances, coating-impedance identification and critical damping. The [formula audit](../formula-compression.md) derives what becomes simpler and records what does not: mathematical expressiveness does not by itself establish a runtime advantage.

The [three concrete investigations](novelty.md) begin the next research step: a closed first-power classification for a subproblem in Noferini's matrix-function paper, an exact cubic critical flow with a Cayley correction, and a guarded reciprocal prototype that preserves tiny mixed coefficients. The [all-power block reduction and cubic classification](higher-power-rank.md) extend the [first-power proof](first-power-rank.md). Publication priority remains unconfirmed. The other two are useful specializations of known mathematics.

The implementation was reassessed from [the 0.3.0 source snapshot](https://github.com/hoechp/ultracomplexmath/tree/fb4870cbf8a47a89b4ac10cf3ff34f37fe0cc541), with the resulting documentation, scope cleanup and exponential correction included in 0.4.0. Exact coefficients, intrinsic planar geometry, coupled operators and projective points already exist. They must no longer be listed as wholly missing features.

## The strongest findings

| Finding | Why it matters | Present status |
| --- | --- | --- |
| Every invertible value has a full eight-parameter polar form | Common scale, reciprocal stretching, two phases and four shear coordinates compose coherently | Derived, with a coupled phase lattice; bounded reconstruction checks; [polar API and winding continuation](../polar-motion.md) shipped |
| Real nonscalar 2×2 generators have complex, split or dual type | Underdamping, overdamping and critical damping belong to one continuous family | Classification, rational checks and a physical damping demo with convergence; [constant-generator flow](../polar-motion.md) with first variations shipped |
| Two different shears can compose into rotation or hyperbolic motion | Lens/propagation order and critical transitions reveal a connection between the geometries | Exact optical-cell checks; general composition uses existing operators, not scalar multiplication |
| The projective line is the tangent bundle of a complex quadric | The full union has a shared surface with two line families and tangent directions | Derived through chart transitions; rational incidence examples checked; geometric API missing |
| `i*j` is a second commuting imaginary unit | CS supports bicomplex finite-step second derivatives; epsilon can add a mixed third derivative | Derived and checked; exponential cancellation fixed; other primitives need componentwise accuracy work |
| Rational geometry extends naturally into dynamics | Cayley maps can preserve geometric forms and first variations exactly over Q | Existing API, new symplectic/reversibility checks; no general integrator yet |
| Optics, wave interfaces and impedance share transfer geometry | Phase, opposing directions, projective ratios and sensitivities can use one operator framework | Small optical-stack and impedance-fit demos implemented; reusable physical components and stable scattering composition remain open |
| Projective boundaries are richer than one infinity | Mixed charts retain valid states when neither full coordinate is a unit | Point/map APIs exist; automatic continuation and incidence geometry are missing |
| Thermodynamic response is a strong additional candidate | Derivatives of a potential link pressure, response and parameter sensitivity | Established external multicomplex precedent; stable higher-derivative primitives are needed first |
| Modular coefficients reveal different behavior | Characteristic two turns body generators into extra nilpotents | Derived and exhaustively checked in a 256-element probe; no public backend yet |

These are opportunities grounded in algebra and existing literature. No mathematical novelty, universal superiority or engineering readiness is inferred merely from combining the generators.

## What to build first

1. **Reliable coefficient-level numerics and exact domains.** Extend the exponential fix to division/log/trig, and complete supported rational powers. Small geometric components deserve accuracy even when no derivative is being extracted.
2. **Complete polar, branch and singular geometry.** Expose the full polar coordinates, their phase lattice and winding histories; classify zero-divisor strata and retain exact constructions where possible.
3. **Continuous circular–hyperbolic–parabolic dynamics.** Implement stable generalized sine/cosine across the critical parameter, with full generators and exact discrete Cayley maps. Demonstrate a mechanical/RLC equation and an optical cell together.
4. **Exact projective/contact geometry and optics.** Develop constraint and incidence operations, tangent chart transitions and specified optical components. Keep geometric nilpotents distinct from independently requested perturbation directions.

The [roadmap](roadmap.md) supplies dependencies and completion criteria. [Applications](applications.md) compares usefulness, fit and prerequisites. [Experiments](experiments.md) gives derivations and reproducible checks.

## Read the claims precisely

- **Implemented:** a callable interface and tests exist here.
- **Verified experiment:** a bounded script checks the stated example; it is not a production API.
- **Derived:** a mathematical consequence of explicit assumptions.
- **Proposed:** implementation and application validation remain necessary.

The operation atlas examines C, S, D, CS, CD, SD and CSD in every domain. Split eigenspaces give a faithful representation of the union. Geometric interpretation additionally carries the forms, involutions and chosen transformation actions; numerically, these coordinates can also lose tiny mixed components on reconstruction.
