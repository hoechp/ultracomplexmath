# Sources and evidence

[Agenda](README.md) · [Experiments](experiments.md) · [Roadmap](roadmap.md)

Sources checked for the renewed review and geometric follow-up on 2026-10-03–04 (UTC). Established background is separate from project derivations, implementation findings and proposals. This is a focused feasibility review, not an exhaustive novelty search.

## Primary sources

| Key | Source | Use and scope |
| --- | --- | --- |
| R1 | Dray and Manogue, [The Split Complex Numbers](https://books.physics.oregonstate.edu/GELG/csplit.html) | Split forms, null directions and boosts |
| R2 | Kisil, [Erlangen Program at Large—2: Inventing a wheel. The parabolic one](https://arxiv.org/abs/0707.4024) | Broader elliptic/parabolic/hyperbolic geometry; a dual shear is not all of parabolic geometry |
| R3 | Havlicek, [Projective Ring Lines and Their Generalisations](https://arxiv.org/abs/1210.1921) | Ring-line background; the specialized chart criterion is derived here |
| R4 | Deiters and Bell, [Precise Numerical Differentiation of Thermodynamic Functions with Multicomplex Variables](https://pmc.ncbi.nlm.nih.gov/articles/PMC11424140/) | Mixed derivatives, thermodynamic use and numerical limitations; not evidence of a shipped Ultra Hessian API |
| R5 | Hairer, [Geometric Numerical Integration, Lecture 2](https://unige.ch/~hairer/poly_geoint/week2.pdf), 2010 | Midpoint, symplecticity and quadratic invariants; the exact Cayley identities here are derived explicitly |
| R6 | Monzón and Sánchez-Soto, [Origin of the Thomas rotation that arises in lossless multilayers](https://opg.optica.org/josaa/abstract.cfm?uri=josaa-16-11-2786), 1999 | Author abstract establishes the multilayer/SU(1,1)/Lorentz bridge; paywalled details were not used |
| R7 | Al-Mohy and Higham, [Computing the Fréchet Derivative of the Matrix Exponential](https://eprints.maths.manchester.ac.uk/1218/), 2009 | Matrix sensitivity/conditioning and noncommuting perturbations |
| R8 | Lynch and Park, [Modern Robotics §6.2](https://modernrobotics.northwestern.edu/nu-gm-book-resource/6-2-numerical-inverse-kinematics-part-1-of-2/) | Jacobian-based inverse kinematics; exact constraint graphs are a further proposal |
| R9 | Keith Conrad, [Hensel's lemma](https://kconrad.math.uconn.edu/blurbs/gradnumthy/hensel.pdf) | Simple-root lifting and its derivative condition |
| R10 | Swastik Kopparty, [Some remarks on multiplicity codes](https://arxiv.org/abs/1505.07547) | Finite-field polynomial/derivative evaluations; no coding backend is shipped |
| R11 | NIST DLMF, [§4.14](https://dlmf.nist.gov/4.14), [§4.23](https://dlmf.nist.gov/4.23) | Complex trigonometry and inverse branches |
| R12 | JAX authors, [Complex numbers and differentiation](https://docs.jax.dev/en/latest/301/cookbook.html#complex-numbers-and-differentiation) | Real-linear complex differentiation as an ecosystem comparison; no JAX adapter exists here |
| R13 | Rooney, [On the Three Types of Complex Number and Planar Transformations](https://journals.sagepub.com/doi/10.1068/b050089), 1978 | Accessible author abstract: rotation, Lorentz boost and dual shear; paywalled full text was not used |
| R14 | Bașkal and Kim, [Lorentz Group in Ray and Polarization Optics](https://arxiv.org/abs/1204.5071), 2012 | Primary exposition of optical matrices and their group geometry; explicit cell identities here are independently calculated |
| R15 | Han, Kim and Noz, [Stokes Parameters as a Minkowskian Four-vector](https://arxiv.org/abs/physics/9707016), 1997 | Jones/coherency/Stokes relation and Lorentz structure; applies to the specified normalized, nondepolarizing actions |
| R16 | Libine, [Hyperbolic Cauchy Integral Formula for the Split Complex Numbers](https://arxiv.org/abs/0712.0375), 2007 | Split analytic functions, wave operator and hyperbolic Cauchy integration; no mixed-algebra PDE solver is implied |
| R17 | Stacks Project, [§33.16: Tangent spaces](https://stacks.math.columbia.edu/tag/0B28) | Geometric meaning of points with values in dual numbers |
| R18 | Vakil, [Foundations of Algebraic Geometry, classes 15–16](https://math.stanford.edu/~vakil/0708-216/216class1516.pdf) | Segre embedding and the two rulings of a smooth quadric |
| R19 | Chaniotakis and Cory, MIT [Sinusoidal Steady State Response of Linear Circuits](https://ocw.mit.edu/courses/6-071j-introduction-to-electronics-signals-and-measurement-spring-2006/96c80ce0d5513139310a9526fdadb419_sss_phsor_impdce.pdf), 2006 | Separate voltage/current phasors related by impedance |

The [implemented applications](../gallery/applications.md) also cite their own physical-model sources. References support only the background they discuss; actual package behavior is checked locally.

The [engineering showcase](../gallery/impact.md) adds primary sources for multilayer optics (Byrnes), photovoltaic cover-glass coatings (Karin, Miller and Jain), coating equivalent circuits (Gamry), and damped mechanical modes (MIT). Their physical context is separate from the locally generated, synthetic example results.

## Project-specific derivations

The seven subalgebras, unit criterion and epsilon ideal follow from the defining relations. This review additionally derives the bicomplex extraction sign, Cayley symplectic/quadratic identities, transfer/Riccati correspondence and characteristic-two presentation. Root tangent equations and limits on order, norms and rational closure follow similarly. These are direct calculations, not novelty claims.

The [geometric follow-up](geometric-structure.md) supplies explicit derivations of the full polar factorization and phase lattice, real 2×2 classification, finite shear, optical-cell transition and the projective tangent-quadric identification. It states the scalar/operator distinction and real-structure assumptions. These arguments supply the general conclusions; bounded numerical and exact examples check specified calculations rather than proving a global theorem by sampling.

The [novelty investigation](novelty.md#sources-and-search-boundaries) adds a dated source ledger for Noferini's first-power rank subproblem and relevant graph/matrix-function/bicomplex prior art. Its [rank note](first-power-rank.md) includes a full derivation, explicitly separating proof, finite verification and unestablished publication novelty.

## Reproduce

```sh
python tools/research_probe.py
python tools/frontier_probe.py
python tools/geometric_structure_probe.py
python tools/novelty_probe.py
python -m examples.exact_geometry
python -m pytest
```

| Evidence | Coverage | Limit |
| --- | --- | --- |
| [research_probe.py](../../tools/research_probe.py), [verification.json](verification.json) | Trig/operator identities, intensity, critical series, unit-root examples, one Hensel lift | Selected bounded cases; not a general function library |
| [frontier_probe.py](../../tools/frontier_probe.py), [frontier-verification.json](frontier-verification.json) | Mixed derivatives, exact steps/maps, exhaustive F2 and rational-power gap | Specified functions/ranges and one small finite ring |
| [geometric_structure_probe.py](../../tools/geometric_structure_probe.py), [geometric-verification.json](geometric-verification.json) | Unit polar reconstruction/branches; 81 exact matrix classifications; finite shear; optical cells; Stokes invariants; quadric/chart equations; analytic cubics | Moderate numerical units and specified rational examples; no global accuracy, topology-by-sampling or physical-device validation |
| [Component regression tests](../../tests/test_component_accuracy.py) | Tiny exponential coefficients and compensated large values | Does not certify every other function |
| [Novelty probe](../../tools/novelty_probe.py), [full report](novelty-verification.json) | First-power rank formulas versus exact elimination, graph and tensor representations; critical flows versus 4×4 rational blocks; reciprocal components versus exact arithmetic | ℓ=1 only; critical constant generators; reciprocal excludes near-zero-divisor cancellation; priority unconfirmed |
| [Exact geometry example](../../examples/exact_geometry.py) | Rational constructions/invariants | Float conversion only for display |
| [Gallery tests](../../tests/test_gallery.py), [application tests](../../tests/test_applications.py) | Independent formulas, conservation, roots and inverse problems | Idealized models, not real-hardware measurements |
| [Engineering tests](../../tests/test_impact_models.py), [full render report](../gallery/assets/impact-report.json) | Fresnel recursion and power balance; circuit derivatives and inverse fit; rational residuals; critical damping, dissipation and convergence | Specified model grids, synthetic observations and separate rational fixtures; includes small-channel numerical error |

Checked-in figure reports describe their full render datasets; routine CI checks the models without regenerating all assets. New probes record version/source context. Tests, lint, formatting, typing, documentation checks, probes and builds protect this release. Their success does not imply that every proposed feature exists or every numerical corner case has been eliminated.
