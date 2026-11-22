# Exact integer and rational arithmetic

[Documentation](README.md) · [Unified geometry](unified-geometry.md) · [Research status](research/roadmap.md)

Exact arithmetic implements the full union of complex, split-complex and dual
algebras over rational coefficients:

$$A_{\mathbb Q}=\mathbb Q[i,j,\varepsilon]/(i^2+1,j^2-1,\varepsilon^2).$$

Every one of the eight components is a `fractions.Fraction`. Integer inputs
retain every bit, including in mixed directions. Arithmetic, inverses, linear
systems, polynomials, rational geometric constructions and projective maps
stay in this coefficient domain. There is no intermediate conversion to float.
The implementation uses the standard library and adds no dependency.

`Ultra` remains the numerical specialization. `ExactUltra` is the exact
specialization of **the same algebra**, with the same basis, multiplication and
embeddings. Selecting a coefficient domain is distinct from selecting a
complex, split-complex or dual geometry.

## Start with exact inputs

```python
from fractions import Fraction as F
from ultracomplexmath import ExactUltra, QI, QJ, QEPS, QONE, evaluate_exact

x = ExactUltra(real=10**100 + 1, j=F(1, 3), i=F(2, 7), eps_ij=F(5, 11))
assert x * x.inverse() == QONE
assert QI ** (2**53 + 1) == QI
assert (QI + QJ + QEPS) ** 2 == 2 * QI * QJ + 2 * QEPS * (QI + QJ)
assert evaluate_exact("0.1 + 0.2 - 0.3") == ExactUltra()
```

Use `Fraction(1, 10)` or `Fraction("0.1")` in Python. The Python expression
`1 / 10` has already produced a float before a constructor sees it. Exact
constructors therefore reject floats, bools, Python complex values and `Ultra`
instances. This makes loss of exactness visible at the call site.

`ExactComplex(a,b)`, `ExactBinary(a,b)` and `ExactDual(a,b)` provide the closed
two-dimensional rational algebras. Their `.to_ultra()` methods faithfully embed
them in `ExactUltra`; `.from_ultra()` rejects components outside the chosen
subalgebra, with **no numerical tolerance**. `ExactUltra.coerce(value)` is the
common promotion path for any exact closed type or rational scalar.

```python
from ultracomplexmath import ExactComplex, ExactDual

product = ExactComplex(1, 2).to_ultra() * ExactDual(3, 4).to_ultra()
assert product == ExactUltra(real=3, i=6, eps=4, eps_i=8)
```

Mixing closed types directly raises an error. In particular, an imaginary
coordinate is never silently reinterpreted as a split or dual coordinate.
Integer and Fraction scalars work on either side of exact arithmetic.

## Arithmetic and boundaries

| Capability | Exact contract |
| --- | --- |
| `+`, `-`, `*`, unary signs | Closed over all eight rational coefficients |
| `/`, `inverse()` | Exact when the denominator is a unit; otherwise `NonInvertibleError` |
| `** n` | Arbitrarily large positive/negative Python integer exponents; negative powers require a unit; exponent zero gives one |
| `sqrt()`, `** Fraction(1,2)` | Principal square root if its coefficients are rational; otherwise `DomainError` |
| `conjugate("i"/"j"/"eps")` | Exact involutive algebra automorphisms |
| `determinant()` | Exact rational determinant of the 8×8 regular representation |
| `.primal`, `.tangent`, `.with_tangent(seed)` | Body and epsilon coefficient in the full complex/split algebra |
| `real_part()`, `imag_part()`, `abs2()` | Preserve split structure and exact first variations |
| `channels()`, `from_channels()` | Exact computational coordinates using Gaussian rational bodies/tangents |
| `==`, hash | Exact value identity within the same exact value type; no implicit scalar equality or tolerance |
| `to_json()`, `from_json()` | Algebra/version metadata and eight string numerator/denominator pairs |

For an exact closed 2D value, `.determinant` is its quadratic form
`a*a - square*b*b`, rather than the full regular determinant above.

Integers form a subring; division naturally promotes coefficients to rational
fractions. Invertibility means invertibility over **Q**, not over Z. In a split
representation a value is a unit exactly when both Gaussian rational body
components are nonzero. Epsilon coefficients do not affect this decision.
The direct eight-component multiplication remains the algebra's definition;
the alternative representation is useful for inversion and proofs.

### Results that cannot be rational

Rational coefficient support does not make Q algebraically or analytically
closed. `ExactUltra(2).sqrt()` raises because its principal root needs irrational
coefficients. A nonzero pure epsilon value has no square root even in the real
algebra. Other noninteger powers, transcendental functions, complete root
families and symbolic irrational expressions are not implemented in the exact
backend. Even a special rational result of an unsupported operation is not
guessed by the API.

Explicit numerical evaluation is available for the full existing calculus:

```python
numerical = ExactUltra(F(1, 3), i=F(2, 7)).approximate().sin()
```

`.approximate()` converts to binary64; large inputs may exceed its finite range.
`ExactUltra.from_approximate(value)` captures the **represented binary fractions**,
not an assumed intended decimal. For example, binary64 `0.1` does not become
`Fraction(1,10)`. There is currently no arbitrary-precision floating backend.
Exact arithmetic is bounded by memory and execution time, and decimal string
conversion is subject to Python's integer-string resource limits.

## Exact formulas and command line

`ExactFormula` and `evaluate_exact` evaluate a restricted AST. Decimal and
scientific literals are read from their source text, so neither `0.1` nor
`1e-400` passes through a binary float. Variables accept exact values.

Supported functions are `inverse`, `sqrt`, `conjugate`, `conj_j`, `conj_eps`,
`abs2`, `real_part`, `imag_part`, `primal`, `tangent`, `floor` and `ceil`.
`%`, `//`, `floor` and `ceil` require **real rational scalars**; there is no
invented ordering or Euclidean remainder on the full hypercomplex ring.
`^`, `²`, `³` and `ε` are accepted aliases. The exact parser requires explicit
multiplication; the legacy parser remains numerical.

```sh
python -m ultracomplexmath --exact '0.1 + 0.2 - 0.3'
python -m ultracomplexmath --exact --json '(1/3 + i + j + eps)^3'
```

The JSON schema uses string pairs so consumers cannot round large numerators
to JavaScript numbers. `--exact` and `--legacy` are mutually exclusive.
Formula limits are 4,096 characters, 512 AST nodes, depth 64, exponent magnitude
10,000 and coefficient bit-size 1,000,000. These are calculator guardrails, not
a hostile-input isolation boundary. Direct Python arithmetic has no expression
exponent cap. Existing `Formula` and the default CLI keep their numerical
literal and function semantics.

## Exact linear systems, including null divisors

`ExactMatrix` stores `ExactUltra` entries and supports addition, subtraction,
scalar multiplication, `@`, `.transpose`, `.apply(vector)`, `.determinant()`,
`.inverse()`, `.solve(rhs)` and integer powers. Determinants use the
Faddeev–LeVerrier recurrence, dividing only by positive integer scalars over Q.
They never require a matrix entry itself to be invertible.

Solvers expand an equation into rational component equations and use exact
RREF. There is no pivot tolerance and no rounded rank decision.

```python
from ultracomplexmath import ExactMatrix, exact_solution_space

p, m = (QONE + QJ) / 2, (QONE - QJ) / 2
matrix = ExactMatrix([[p, m], [m, p]])
assert matrix @ matrix.inverse() == ExactMatrix.identity(2)

family = exact_solution_space([[QEPS]], [QEPS])
assert len(family.basis) == 4
assert QEPS * family.at(F(1, 3), 2, -3, 4)[0] == QEPS
```

Every entry of that invertible matrix is a zero divisor. The solution family
of `eps*x=eps` contains four rational free directions. `exact_solve` requires a
unique solution; a consistent free system raises `SingularSystemError`, and an
inconsistent system raises `InconsistentSystemError`. Rectangular systems are
supported. `basis_indices=(0,4)`, for example, restricts unknowns to the dual
subalgebra. All eight equation components are still enforced.

Basis vectors of a solution family are **Q-vector-space** directions, and
`.at()` takes rational parameters. They are not advertised as a free module
basis over a ring with zero divisors. These dense reference solvers prioritize
correctness; sparse/factored and large-scale numerical solvers remain separate
work.

## Exact polynomials and first variations

`ExactPolynomial` stores ascending power coefficients. It supports evaluation,
addition, multiplication, repeated derivatives, integration with a chosen
constant, division with remainder when the divisor's leading coefficient is a
unit, interpolation at distinct rational nodes and Hermite interpolation with
one value and first derivative at each node.

```python
from ultracomplexmath import ExactPolynomial

p = ExactPolynomial([F(1, 3), QI, QJ, 7])
assert p.integral().derivative() == p
assert p(2 + QEPS).tangent == p.derivative()(2)

h = ExactPolynomial.hermite([0, 1], [QONE, QI], [QJ, QEPS])
assert h(0) == QONE and h(1) == QI
assert h.derivative()(0) == QJ and h.derivative()(1) == QEPS
```

If coefficients already contain epsilon, their own variations also contribute:
`p(x + eps).tangent == p(x).tangent + p.derivative()(x).primal` for epsilon-free
`x`. This is useful for simultaneous curve evaluation and coefficient
calibration. Polynomial root classification, factorization and modular/Hensel
backends remain research tasks.

## Evidence

`tests/test_exact.py` checks all 64 basis products against a literal independent
table, rational algebra laws, 400-digit inputs, exact inverses, root domains,
parser/serialization behavior, the zero-divisor matrix above, determinants
against a permutation formula, full solution families and interpolation.
The geometric tests and [executable example](../examples/exact_geometry.py)
exercise the exact backend outside scalar arithmetic.

Python's [Fraction documentation](https://docs.python.org/3.12/library/fractions.html)
specifies the coefficient type and why conversion from a float records its
binary value. The algebraic identities and implementation choices here are
derived and tested in this repository.
