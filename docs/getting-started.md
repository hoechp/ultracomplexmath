# Getting started

[Documentation](README.md) · [API map](api.md) · [Showcase](gallery/README.md)

## Install from the repository

Use Python 3.12 or later. The version in this repository is not published on PyPI.

```sh
git clone https://github.com/hoechp/ultracomplexmath.git
cd ultracomplexmath
python -m venv .venv
. .venv/bin/activate
python -m pip install -e .
```

On Windows activate with `.venv\Scripts\Activate.ps1` in PowerShell. The core requires only Python's standard library. Add plots and desktop widgets with `python -m pip install -e '.[plot]'`.

## Choose coefficients, then geometry

| Need | Full algebra | Closed two-dimensional types |
| --- | --- | --- |
| Transcendental functions and numerical models | `Ultra` | `Complex`, `Binary`, `Dual` |
| Exact integers and fractions | `ExactUltra` | `ExactComplex`, `ExactBinary`, `ExactDual` |

`Binary` is the split-complex algebra; it does not mean a binary coefficient format. Numerical and exact values are separate types. Cross from exact to numerical explicitly with `.approximate()`.

```python
from fractions import Fraction as F
from ultracomplexmath import Ultra, ExactUltra, I, J, EPS, QI, QJ, QEPS

z = Ultra(real=2, i=0.5, j=0.25, eps_ij=1)
assert z.exp().log().isclose(z)  # This example stays on the principal sheets.
assert I * I == Ultra(-1)
assert J * J == Ultra(1)
assert EPS * EPS == Ultra()
q = ExactUltra(2, i=F(1, 2), j=F(1, 4), eps_ij=1)
assert q.approximate() == z
assert (QI + QJ + QEPS) ** 2 == 2 * QI * QJ + 2 * QEPS * (QI + QJ)
```

The constructor order is `(real, j, i, ij, eps, eps_j, eps_i, eps_ij)`; named arguments are easiest to read. Closed values embed with `.to_ultra()`. Different closed algebras are not silently reinterpreted as one another.

## Evaluate formulas

```sh
python -m ultracomplexmath 'cos(i+j+eps)'
python -m ultracomplexmath 'log(1+i)' --json
python -m ultracomplexmath --exact '0.1+0.2-0.3'
python -m ultracomplexmath --exact '(1/3+i)^2' --json
```

`evaluate()` and `evaluate_exact()` provide the same calculators in Python. Use explicit multiplication. `^` is accepted as exponentiation. Exact decimal literals are parsed as fractions. Python's expression `1/3` is already a float, so use `Fraction(1,3)` in exact Python code. `--legacy` selects the separate compatibility formula grammar and cannot be combined with `--exact`.

## Propagate a first variation

```python
import math
from ultracomplexmath import Ultra

x = Ultra.dual(0.7, 1)
y = x.sin() * x.exp()
assert math.isclose(y.real, math.sin(0.7) * math.exp(0.7))
assert math.isclose(y.eps, (math.sin(0.7) + math.cos(0.7)) * math.exp(0.7))
```

For full algebra values, `.primal`, `.tangent` and `.with_tangent(seed)` expose the epsilon extension. It is exact first-order algebra, evaluated with the chosen coefficient arithmetic. It does not assert that a finite parameter change has no higher-order remainder. [Higher derivatives](research/experiments.md#mixed-higher-derivatives) require additional care.

## Construct exact geometry

```python
from fractions import Fraction as F
from ultracomplexmath import CIRCULAR, PlaneIsometry, line_intersection2d

motion = PlaneIsometry(CIRCULAR.cayley(F(1, 2)), CIRCULAR.exact(2, 1))
point = CIRCULAR.exact(3, F(1, 7))
assert motion.inverse()(motion(point)) == point
assert line_intersection2d((0, 0), (3, 2), (1, 0), (0, 1)) == (F(3, 5), F(2, 5))
```

The [geometry guide](unified-geometry.md) extends the same interface to boosts, shears, exact predicates, coupled operators and projective maps.

## Explore and reproduce

```sh
python -m examples.automatic_differentiation
python -m examples.exact_geometry
python -m examples.exact_geometry --plot
python -m examples.gallery --quick --output /tmp/ultra-gallery
python -m examples.applications --quick --output /tmp/ultra-applications
ultracomplex-gui --view domain --formula 'cos(x)'
ultracomplex-gui --view mechanism
```

The formula explorer has `components`, `paths`, `domain` and `vectors` views. `--output figure.png` renders without a display. The showcase explains color conventions, assumptions and reproduction settings. Generic clustering and data-mining explorers now live in a [separate package](scope.md).

## Interpret errors

- `NonInvertibleError`: a divisor has a zero body in at least one split eigenspace. A nonzero value can still be a zero divisor.
- `DomainError`: the selected function, branch or coefficient domain cannot supply the result; for example an irrational square root in the rational backend.
- `SingularSystemError` / `InconsistentSystemError`: a unique linear solution does not exist / no solution exists. Use a solution-space API to inspect free families.
- `NonFiniteError` or numeric overflow: the numerical calculation left the supported finite range.

No global ordering, full-algebra floor or universal geometric angle is invented. Choose an intrinsic geometry, a real scalar projection or a documented observable.
