# New findings and reproducible experiments

[Agenda](README.md) · [Roadmap](roadmap.md) · [Sources](references.md)

Run `python tools/frontier_probe.py` from the repository root. [frontier-verification.json](frontier-verification.json) records its output, source hashes and version. The script needs only this package and the standard library. These are bounded reference experiments, not production derivative/ODE/modular APIs.

## Mixed higher derivatives

Set `k=i*j`. Then `k²=-1` and `ik=ki=-j`. Taylor expansion of a real analytic scalar function on a consistent extension gives

$$f(x+h(i+k))=\sum_{n\geq0}\frac{f^{(n)}(x)}{n!}h^n(i+k)^n.$$

The square contributes `-2-2j`, while odd powers have no j component. Therefore

$$-\frac{[j]f(x+ih+kh)}{h^2}=f''(x)+O(h^2).$$

For several real arguments, perturb argument a along i and b along k to obtain a mixed Hessian entry. Repeated evaluations supply other entries. Seeding a parameter p with epsilon differentiates that finite-step expression; for the same scalar input the `eps*j` extraction tends to the third derivative.

This does not contradict the square-zero epsilon ideal: the second derivative comes from a bicomplex **finite step**, and epsilon adds an algebraically exact first variation of that step. Floating error, truncation and underflow remain. Comparisons, clipping and conjugation do not automatically respect the intended analytic extension.

### A reproduced defect and its correction

For f=exp at x=1, the exact j coefficient is `-e*sin(h)²`. Channel reconstruction subtracts two almost equal real values:

| h | Second-derivative estimate with the earlier channel algorithm | Component-preserving exp in 0.4.0 |
| --- | --- | --- |
| `1e-3` | about 2.71828092235 | about 2.71828092237 |
| `1e-8` | about 2.22044604925 | about 2.71828182846 |
| `1e-10` | 0 | about 2.71828182846 |

The limiting reference is e; finite steps have O(h²) truncation error. Last digits may vary by math library.

The correction factors the body as `exp(a+i*c) * (cosh(b+i*d)+j*sinh(b+i*d))` and evaluates small components directly. Scaled real factors avoid an overflowing intermediate cosh when the complete result is finite. The tangent uses direct basis multiplication. Tests include h=`1e-100`, mixed epsilon coefficients and compensated large exponents.

**Remaining gap:** inverse and logarithm still lose some O(h²) coefficients. The probe reports estimates next to their limiting second derivatives 2 and −1 at x=1. A dominant-body norm would hide these losses; a general Hessian API is therefore still a proposal. Multicomplex differentiation is established [R4](references.md); this extraction sign and implementation correction are derived for the project's basis.

## Exact geometric time steps

Let

$$B_\kappa=\begin{pmatrix}0&1\\\kappa&0\end{pmatrix},\qquad M_h=(I+\tfrac h2B_\kappa)(I-\tfrac h2B_\kappa)^{-1}.$$

The API call is `B.cayley(h/2)`: its argument is a Cayley parameter, not the physical time step h. Where the denominator is invertible, `M_(-h)=M_h⁻¹`. Define

$$\Omega=\begin{pmatrix}0&1\\-1&0\end{pmatrix},\qquad H_\kappa=\begin{pmatrix}-\kappa&0\\0&1\end{pmatrix}.$$

From `BᵀΩ+ΩB=0` and `BᵀH+HB=0`, direct expansion gives

$$M_h^T\Omega M_h=\Omega,\qquad M_h^TH_\kappa M_h=H_\kappa.$$

These identities hold exactly over Q and its central dual extension. For `kappa=k+eps`, epsilon coefficients give the differentiated invariants. The probe checks k=−2,0,2 and h=1/5. At zero kappa the quadratic form is degenerate, but the symplectic form is not.

This is linear implicit midpoint: a second-order approximation, not the exact continuous flow. Hairer supplies the general symplectic context [R5](references.md). Error control, pole handling and fraction-growth measurements remain necessary for a usable integrator.

## Transfer maps and Riccati evolution

For `v'=B*v`, `v=(x,y)`, `B=[[a,b],[c,d]]`, and r=x/y where y is a unit,

$$r'=b+(a-d)r-cr^2.$$

A finite map `M=[[A,B],[C,D]]` instead acts by `(A*r+B)/(C*r+D)`. This connects linear operators, Riccati equations and Möbius geometry. The probe compares exact Cayley matrix action with `Mobius`.

Homogeneous coordinates can cross affine poles while the pair remains unimodular; mixed split charts already exist. Automatic continuation and physical optical/impedance components remain open. The algebraic bridge does not impose the same conservation law on every model.

## Finite coefficients

The quotient can be defined over any commutative coefficient ring. The public exact backend uses Q; this probe studies a future domain.

For odd prime p, factoring the defining polynomials gives:

| Prime | Eight-dimensional algebra over Fp |
| --- | --- |
| p ≡ 3 mod 4 | Two copies of `F_(p²)[eps]/(eps²)` |
| p ≡ 1 mod 4 | Four copies of `Fp[eps]/(eps²)` |

For p=2 set `r=i+1`, `s=j+1`. Then

$$\mathcal A_{\mathbb F_2}\cong\mathbb F_2[r,s,\varepsilon]/(r^2,s^2,\varepsilon^2).$$

This local ring has 256 elements. Its maximal ideal `m=(r,s,eps)` consists of zero-constant values in the new basis. Exactly 128 elements are units, each `1+n` with n in m. Every individual n squares to zero in characteristic two, so every unit is its own inverse. Nevertheless `r*s*eps≠0`: `m³≠0` and `m⁴=0`. Powers of an ideal are different from powers of individual elements.

The probe verifies a bijective change of basis and all 64 basis products against the original relations, then searches inverses exhaustively. It checks the unit count, square identities, nonzero mixed cubic and its annihilation. The ideal-power statement also follows directly from the monomial presentation.

A modular backend cannot reuse division by two or characteristic-zero branch rules. Hensel corrections require the relevant derivative to be a unit [R9](references.md). Hasse derivatives use Taylor coefficients without factorial division, useful in positive-characteristic multiplicity evaluation [R10](references.md).

Over Z, arbitrary integer channels may reconstruct half-integral coefficients: the channel pairs need parity agreement. Preserve the direct basis and coefficient-domain-specific units.

## A concrete exact-support gap

`ExactUltra(8)**Fraction(1,3)` currently raises `DomainError` although the real rational result 2 exists. This is an unimplemented rational-power contract. Rational principal square roots already work where supported. General power/root APIs need branches and singular-family semantics before extrapolating from a special case.

The report identifies evaluated source files so the evidence remains distinguishable from a global guarantee for future code.
