# Operation atlas

[Agenda](README.md) · [Applications](applications.md) · [Priorities](roadmap.md)

C = complex (`i²=-1`), S = split-complex (`j²=1`), D = dual (`eps²=0`). Juxtaposition means their commuting tensor union. All seven combinations appear in every domain. Exact coefficients mean Q; numerical functions use finite binary64 coefficients. The tables explain mathematical behavior and uses; each **status** distinguishes shipped code from proposals.

## Arithmetic and division

| Algebra | Distinctive behavior and useful computation |
| --- | --- |
| C | Nonzero values invert; multiplication combines scale and phase: planar phasors and rotations. |
| S | `(1+j)(1-j)=0`; independent idempotent directions: forward/backward components and characteristics. |
| D | `(a+eps*b)⁻¹=1/a-eps*b/a²`, a≠0: sensitivities of ratios. |
| CS | Complex phase and split null divisors coexist: directional complex fields. |
| CD | Complex inverse with a complex first variation: impedance and pole sensitivity. |
| SD | A null sector can obstruct division despite nonzero coefficients: transfer/rapidity sensitivity with singular diagnostics. |
| CSD | Mixed products retain phase, split structure and first variations: differentiable field calculations. |

**Status:** numerical and rational arithmetic, integer powers, conjugations and unit checks exist. Nonunit equations use linear solution families. Small-component division and coefficient protocols remain open [G01/G03](roadmap.md).

## Powers, roots and branches

| Algebra | Distinctive behavior and useful computation |
| --- | --- |
| C | Root phases and logarithmic branches: oscillation modes and frequency laws. |
| S | Real channel roots obey parity/sign restrictions; roots may be nonunique: split factorization. |
| D | Regular roots carry their derivatives; singular bodies require separate tangent equations: length/material sensitivity. |
| CS | A generic unit has n² nth roots over complex coefficients: independent phase sheets and product root basins. |
| CD | A chosen simple complex root has a unique tangent lift: perturbed dispersion roots. |
| SD | Root validity and tangent solvability can differ by sector: null-boundary and bifurcation diagnostics. |
| CSD | Chosen body roots have tangent equations; zero-body factors can produce free families or no roots: multiplicity-aware continuation. |

**Status:** numerical principal functions, independent logarithm branches and closed 2D root APIs exist. Full `Ultra.roots()` families do not. Exact integer powers and rational principal square roots exist; even `ExactUltra(8)**Fraction(1,3)` is currently unsupported. Rational-power and complete-root contracts are separate tasks [G02/G15](roadmap.md).

## Exponential and trigonometry

| Algebra | Distinctive behavior and useful computation |
| --- | --- |
| C | `exp(i*t)=cos(t)+i*sin(t)`; complex cosine grows transversely: harmonic motion and phase. |
| S | `exp(j*t)=cosh(t)+j*sinh(t)`; `cos(x+j*y)` is periodic in both inputs: boosts and split periodic patterns. |
| D | `exp(eps*t)=1+eps*t`; `cos(x+eps*y)=cos(x)-eps*y*sin(x)`: shear and first variations. |
| CS | Circular and hyperbolic factors multiply; `ij` supplies another circular direction: coupling and bicomplex probes. |
| CD | Oscillation and its parameter derivative share one expression: frequency/phase calibration. |
| SD | Hyperbolic motion and its derivative share one expression: growth/boost sensitivity. |
| CSD | All factors and mixed variations coexist: coupled dynamics and critical-regime models. |

**Status:** numerical elementary, inverse and reciprocal functions exist. The exponential's mixed-component defect is corrected. Stable `expm1`, `log1p`, `sinc`, `sinhc`, generalized `C_kappa/S_kappa` and broader special functions are missing. Rational coefficients alone cannot close transcendental evaluation [G01/G05/G12](roadmap.md).

## Angles, logarithms and periodicity

| Algebra | Distinctive behavior and useful computation |
| --- | --- |
| C | Circular phase modulo a turn, local phase derivative away from zero: bearings and phase tracking. |
| S | Rapidity plus one of four non-null sectors; null rays have no finite angle: 1+1 velocity composition. |
| D | Shear y/x plus sign of x; undefined polar parameter at x=0: slope and affine shear. |
| CS | Two complex phase sheets coexist with split structure: relative phase and beating. |
| CD | `d arg(z)=Im(dz/z)` is real-linear, not holomorphic: phase sensor calibration. |
| SD | Rapidity/slope changes must respect sector boundaries: moving-frame estimation. |
| CSD | Circular sheets, split sectors and tangent data need joint tracking: coupled model continuation. |

**Status:** intrinsic polar coordinates, directed relative angles, rotors, sectors, logarithm branches and phase derivatives exist. Derivative-aware `atan2`, path unwrapping, branch histories and automatic chart changes do not. A single real angle would discard essential information [G07](roadmap.md).

## Metrics, norms and order

| Algebra | Distinctive behavior and useful computation |
| --- | --- |
| C | Positive form x²+y²: Euclidean lengths and projections. |
| S | Indefinite form x²−y² and nonzero null vectors: causal sectors and flux differences. |
| D | Degenerate form x² preserved by shear: degenerate metric geometry. |
| CS | No positive multiplicative norm on all nonzero elements: choose intensity, split flux or a coordinate norm explicitly. |
| CD | Squared amplitude retains `2 Re(conj(z)*dz)`: intensity gradients. |
| SD | Invariants have differentiated conservation laws: sensitivity of a preserved Lorentzian form. |
| CSD | Energy, flux, metric and coefficient diagnostics coexist: multiple observables for the same model. |

**Status:** coefficient norms, intrinsic forms, projection/reflection and complex observables exist. There is no compatible total order, universal min/max, or positive multiplicative norm on the full ring. Cone orders, operator adjoints/conditioning and interval enclosures require explicit semantics [G10/G13](roadmap.md).

## Differentiation

| Algebra | Distinctive behavior and useful computation |
| --- | --- |
| C | Complex-step first derivatives for suitable real analytic extensions: avoid subtracting nearby real outputs. |
| S | Idempotents package two evaluations, but subtraction retains finite-difference cancellation: paired scenarios. |
| D | Exact first-order chain rule in a square-zero extension: forward directional differentiation. |
| CS | `i` and `ij` support bicomplex mixed second derivatives: analytic Hessian entries. |
| CD | Complex first variations; complex-step plus dual probes can target higher real derivatives: response derivative checks. |
| SD | Each split sector has a first variation; all epsilon-seed products remain zero: paired first-order sensitivities. |
| CSD | Bicomplex second steps plus epsilon can probe third derivatives: potential Hessians with parameter sensitivity. |

**Status:** first-order lifts and real-linear observables exist. General JVP/Jacobian/Hessian APIs, seed management, reverse mode and reliable mixed-step pipelines do not. The [new experiment](experiments.md#mixed-higher-derivatives) shows both potential and remaining accuracy problems. Arbitrary exact higher jets require extra generators [G01/G06](roadmap.md).

## Linear algebra and implicit equations

| Algebra | Distinctive behavior and useful computation |
| --- | --- |
| C | Complex systems retain phase: frequency-domain field solves. |
| S | Split factors can have different ranks: characteristic components and constrained modes. |
| D | Regular implicit differentiation gives `F_x dx=-F_p dp`: equilibrium/constraint sensitivity. |
| CS | Complex modal systems may have different nullspaces: spectral constraints. |
| CD | Matrix and RHS variations propagate through complex solves: circuit calibration. |
| SD | Singularities and free tangent directions differ by sector: degenerate constraints. |
| CSD | Coefficient equations expose full solution families even with zero-divisor entries: exact small constraints with phase and sensitivity. |

**Status:** numerical/exact solution-space APIs and exact matrix determinants/inverses exist. Families are real/Q vector spaces, not automatically free modules over the ring. Factorizations, reusable solves, condition estimates, sparse/batch interfaces and implicit nonlinear solvers with rank events are missing [G04/G10](roadmap.md).

## Polynomials, interpolation and integration

| Algebra | Distinctive behavior and useful computation |
| --- | --- |
| C | Complex polynomials, roots and domain-dependent contour integration: approximation and filters. |
| S | Factor components can have different degree/root behavior: paired polynomial laws. |
| D | Evaluation at x+eps yields value and first derivative: Hermite data. |
| CS | Root sets combine complex factors; nonunit leaders matter: dispersion polynomials. |
| CD | Argument and coefficient variations both contribute: shape/response calibration. |
| SD | Hermite data can retain split values and tangents: matched geometric trajectories. |
| CSD | Rational polynomials carry mixed geometric and first-order data: exact curve families and differentiated quadrature. |

**Status:** exact polynomial calculus, antiderivatives, rational-node interpolation/Hermite and division by unit-leading polynomials exist. General quadrature, contours, splines, resultants, factorization and nonunit-leading division theory remain open. Polynomial integration alone is not a general integration package [G09/G12](roadmap.md).

## Geometry and projective constructions

| Algebra | Distinctive behavior and useful computation |
| --- | --- |
| C | Circular isometries and complex fractional-linear maps: mechanisms and conformal models. |
| S | Hyperbolic isometries, null directions and sectors: Lorentzian/transfer geometry. |
| D | Shears, infinitesimal deformations and tangent projective points: local calibration. |
| CS | Circular and split geometry coexist; charts can differ by factor: multi-sector transfer laws. |
| CD | Differentiated rotations, translations and projectivities: geometric phase sensitivity. |
| SD | Differentiated boosts/shears near null boundaries: boundary-aware continuation. |
| CSD | Rational isometries, mixed homogeneous charts and varied coefficients combine: geometry feeding field/kinematic inverse problems. |

**Status:** plane/projective primitives and exact Euclidean predicates exist. Conic/chain incidence, algebraic intersections, automatic continuation, constraint graphs and a coherent 3D pose layer remain open. The dual-plane API implements a shear/reflection/translation subgroup, not the full group preserving a degenerate form [G04/G07/G08](roadmap.md).

## Operators, flows and mechanics

| Algebra | Distinctive behavior and useful computation |
| --- | --- |
| C | Circular scalar generator: harmonic flow. |
| S | Hyperbolic scalar generator: growth/decay and boosts. |
| D | Nilpotent generator has a finite exponential: shear or first-order deformation. |
| CS | Scalar products commute; adding split conjugation permits noncommuting coupling: mode mixing. |
| CD | Operator coefficients retain complex parameter derivatives: phase networks. |
| SD | Nilpotent/critical operators connect to growth regimes: near-critical sensitivity. |
| CSD | Complex-dual 2×2 operators act on the complete state: rational structure-preserving dynamics and interacting fields. |

**Status:** `ModeOperator` composition, inverse and Cayley exist; a general operator has 16 real/rational coordinates. Continuous matrix functions and Fréchet derivatives remain open. For noncommuting perturbations, `d exp(B)` is not generally `exp(B)*dB`. Cayley is a rational time approximation, not the exact exponential [G05](roadmap.md).

## Frequency analysis and differential equations

| Algebra | Distinctive behavior and useful computation |
| --- | --- |
| C | Fourier phase and frequency response: signals, waves and circuits. |
| S | `(dt+j*c*dx)(dt-j*c*dx)=dt²-c²*dx²` for constant c: wave characteristics. |
| D | Response derivatives with respect to speed, material or frequency: calibration. |
| CS | Complex phase follows split characteristic directions: oscillatory travelling waves. |
| CD | Complex response with tangent: filter tuning and group-delay derivatives away from zeros. |
| SD | Characteristic solutions retain speed variation: propagation fitting. |
| CSD | Phase, opposing directions, interfaces and sensitivity can share a model: layered optics, transmission lines and acoustics. |

**Status:** a constant-speed travelling-wave solution and coupled-mode demos exist. General PDE discretization, boundaries/interfaces, FFT/Laplace and causal/passive network libraries do not. Constant-coefficient factorization is not a solver for variable media or nonlinear PDEs [G12/G14](roadmap.md).

## Integer, rational and modular operations

| Algebra | Distinctive behavior and useful computation |
| --- | --- |
| C | Gaussian rational/integer structure; `i²+1` splits according to the field: exact factors and modular roots. |
| S | Idempotents require 1/2; integer channels have parity constraints: lattice/CRT arithmetic. |
| D | Truncated Taylor arithmetic works over suitable rings: polynomial lifting. |
| CS | Odd-prime body decomposition depends on p modulo 4: modular verification. |
| CD | Complex modular structure plus nilpotent correction: lifting over finite extensions. |
| SD | Characteristic two merges split factors into a nilpotent direction: local-ring behavior. |
| CSD | Over F2 three commuting square-zero generators give 256 elements: exhaustive checks and finite-ring models. |

**Status:** rational coefficients and scalar integer/residue utilities exist. Exact `//`, `%`, floor and ceil are real-rational operations, not arbitrary ring division. Modular hypercomplex coefficients, Hensel/Hasse, Gaussian-integer gcd and characteristic-aware root rules remain open [G02/G11](roadmap.md). See [finite coefficients](experiments.md#finite-coefficients).

## Estimation, optimization and uncertainty

| Algebra | Distinctive behavior and useful computation |
| --- | --- |
| C | Complex residuals are paired real observations: phase/amplitude fitting. |
| S | Split factors organize paired responses or characteristics: scenario comparison. |
| D | Directional derivatives linearize real objectives: gradient updates. |
| CS | Bicomplex steps probe analytic Hessians: curvature and thermodynamic response. |
| CD | Real losses need explicit conjugation-aware derivatives: intensity least squares. |
| SD | Sensitivities must be separated from rank/sector changes: geometric continuation. |
| CSD | Mixed derivatives connect geometry, fields and parameters: joint design/calibration. |

**Status:** robot and interference fits are examples, not a general optimizer. Covariance propagation, weighted residuals, constrained optimization and identifiability need dedicated APIs. Dual coefficients are not distributions; split numbers are not automatically interval bounds [G04/G06/G14](roadmap.md).

## Numerical representation and interoperability

| Algebra | Distinctive behavior and useful computation |
| --- | --- |
| C | Branch and range conventions matter: interoperable phase calculations. |
| S | Near-equal channels can erase small split coefficients: condition-aware coordinates. |
| D | Tiny tangents may matter despite a large body: componentwise error budgets. |
| CS | Mixed components can scale as h²: reliable bicomplex evaluation. |
| CD | Real-linear observables require derivative-aware adapters: AD integration. |
| SD | Null structure and tangent scale need separate diagnostics: boundary calculations. |
| CSD | No one representation or norm certifies every component: exact/numerical pipelines with explicit accuracy targets. |

**Status:** immutable typed scalars, explicit conversions and exact JSON exist. NumPy dtype/ufunc support, arbitrary precision, interval certification, compiled batches, units and AD adapters remain open. The exponential fix demonstrates why an algorithm must preserve the requested information [G01/G03/G13](roadmap.md).
