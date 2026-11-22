# Compatibility and conventions

[Documentation](README.md) · [History](history.md) · [Scope changes](scope.md)

## Values and geometry

- `Binary` means split-complex (`j²=1`). `Dual` means `eps²=0`; neither is a renamed complex number.
- Embed closed values with `.to_ultra()` when combining algebras. Mixed closed-type arithmetic is rejected to prevent accidental coordinate reinterpretation.
- `Ultra` stores finite binary64 coefficients; large integer coefficient literals can round. `ExactUltra` stores Fractions and rejects implicit float/complex conversion. Python integer exponents retain their full value in both backends.
- Exact `==` describes stored value identity; numerical `isclose` is a separate tolerance operation. Do not infer a geometric equivalence from storage equality.
- Historical `length`, display colors and coefficient-vector angles are Euclidean visualization conventions. Intrinsic forms, sectors and angles live in `plane_geometry`.
- `plane.angle_between(start,end)` is directed from start to end. Historical closed-type `.angle_to()` conventions remain as implemented; do not substitute one API for the other without checking the meaning.
- Numerical `.phase()` uses principal body phase but a local unwrapped tangent. It does not unwrap a sampled path.

## Expressions

`Formula` and the default CLI use explicit multiplication and a restricted AST. `Calculation`, `SimpleCalculation` and `--legacy` retain the original expression conventions, including implicit multiplication and word operators. `FormulaSystem` supplies dependency-bound expressions. The exact parser is separate and preserves decimal source literals. Calculator resource limits do not constitute process isolation for hostile workloads.

## M2R is an experiment

`M2R` canonicalizes a real 2×2 matrix into a complex, split or dual representative after each operation. It discards the similarity basis; its repeated composition is **not associative**. It is retained because the elliptic/hyperbolic/parabolic classification is related to this project's mathematics and old fixtures exercise it. Use `Matrix`, `ExactMatrix` or `ModeOperator` for ordinary composition. A basis-retaining canonical-form interface is a future task, not a property of `M2R`.

## 0.4.0 removals

General clustering, classification, association rules, concept hierarchies and RSA exercises have moved out of this package. Their old imports and two GUI modes are deliberately removed. See the [complete separation map](scope.md). Integer and scalar modular foundations remain.

## Historical regression evidence

Tests retain independently captured mathematical outputs from the Java implementation in `tests/fixtures`. Corrections to mathematical defects are intentional departures from those old outputs, not compatibility failures. The old migration inventory is archived through immutable Git links; it is no longer a requirement that unrelated exercises ship in the algebra package.
