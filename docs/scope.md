# Project scope

[Documentation](README.md) · [Compatibility](compatibility.md) · [History](history.md)

The project centers on the full union of complex, split-complex and dual algebra and computations that gain something concrete from this union. Exact coefficients, geometry, calculus, transformations and application examples belong together when their mathematical connection is explicit.

## Kept in the main project

- Numerical and rational coefficient arithmetic, formulas, linear systems and polynomials.
- Circular, hyperbolic, parabolic, Euclidean and projective geometry; matrices and geometric mechanisms.
- Elementary functions, angles, first variations and physical observables.
- Located values and rule-defined numerical fields on independent real spatial/time coordinates; slices, sampling, coordinate derivatives and optional labeled-array exports.
- Static parametric surfaces, induced Euclidean metrics, scalar surface calculus and explicit seam diagnostics. These add domain geometry without changing the value algebra.
- Wavelength/phase, characteristic directions, coupled motion and geometric inverse-problem examples.
- Integer roots, Bézout identities, primality, factorization and scalar residue rings as foundations for exact and future modular algebra. These helpers do not imply an implemented modular hypercomplex backend.
- Mathematical regression fixtures and narrowly identified compatibility interfaces.

A new module should explain which algebraic structure it exercises, what it preserves and how its correctness is checked. A use case does not have to consume every coefficient to belong here.

## Separated in 0.4.0

| Previous code | Destination in the standalone package |
| --- | --- |
| `classification.py` | `algorithm_experiments.classification` |
| `clustering.py` | `algorithm_experiments.clustering` |
| `concepts.py` | `algorithm_experiments.concepts` |
| `rules.py` | `algorithm_experiments.rules` |
| `number_theory.RSAData`, `generate_rsa`, `rsa_transform`, `encrypt_rsa`, `decrypt_rsa`, `break_rsa`, `rsa_decoder` | `algorithm_experiments.number_theory` |
| `gui.ClusteringExplorer`, GUI `clustering` view | `algorithm_experiments.gui`, `algorithm-clusters` command |
| `visuals.cluster_domain`, GUI `domain-clusters` view | Optional `algorithm_experiments.domain_bridge` function; no longer a main GUI view |
| `examples/discovery.py` and generic algorithm tests | Separate examples and test suite |

These are useful general algorithms, but their implementations do not rely on ultracomplex geometry or its calculus. The pixel clustering adapter used weighted coordinates, amplitude and raw phase; it was a heuristic feature experiment, not an intrinsic decomposition of the algebra.

They are preserved in **philipp-algorithm-experiments.zip**, supplied separately as an installable source package with its own README, license, tests and provenance hashes. This release does not create a second GitHub repository or publish a new PyPI package. The exact original files are also permanently addressable in [commit fb4870c](https://github.com/hoechp/ultracomplexmath/tree/fb4870cbf8a47a89b4ac10cf3ff34f37fe0cc541), including the [old mixed tests](https://github.com/hoechp/ultracomplexmath/blob/fb4870cbf8a47a89b4ac10cf3ff34f37fe0cc541/tests/test_discovery_integer.py). The archive contains original source snapshots alongside adapted independent modules.

The main working tree, imports, GUI options, tests and package build no longer ship these unrelated components. Git history is retained. This is a deliberate API removal; users of those modules must install the separated package or pin the earlier commit.
