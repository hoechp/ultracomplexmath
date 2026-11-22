# The geometry inside the full union

[Documentation](../README.md) · [Agenda](README.md) · [Geometry APIs](../unified-geometry.md) · [Roadmap](roadmap.md) · [Sources](references.md)

The guiding question is **which geometries, transformations and physical laws become intelligible together through complex, split-complex and dual numbers?** Derivative extraction is one consequence of this structure. Rotation, reciprocal stretching, shear, null directions, projective incidence and their transitions deserve equal mathematical attention.

This chapter works over real coefficients unless stated otherwise. It derives consequences of the defining relations and connects them to established geometry. The [probe](../../tools/geometric_structure_probe.py) checks bounded examples, with a [recorded report](geometric-verification.json). A derivation is not a claim of mathematical novelty; a checked example is not a shipped solver.

## Three Euler formulas, three geometries

For a commuting generator with $u^2=s$, multiplication by $u$ on $x+uy$ has matrix

$$U_s=\begin{pmatrix}0&s\\1&0\end{pmatrix},\qquad U_s^2=sI.$$

| Algebra | Exponential | Action on the plane | Preserved quadratic form |
| --- | --- | --- | --- |
| Complex, $i^2=-1$ | $\cos t+i\sin t$ | Rotation | $x^2+y^2$ |
| Split-complex, $j^2=1$ | $\cosh t+j\sinh t$ | Lorentz boost / reciprocal stretch | $x^2-y^2$ |
| Dual, $\varepsilon^2=0$ | $1+t\varepsilon$ | Shear $(x,y)\mapsto(x,y+tx)$ | $x^2$, a degenerate form |

These transformations are the classical starting point described by [Rooney](https://journals.sagepub.com/doi/10.1068/b050089), whose abstract is accessible. The table concerns these specific multiplication actions. For example, the split-complex plane is flat with a Lorentzian form; it is not itself the negatively curved hyperbolic plane. Broader elliptic/parabolic/hyperbolic constructions require specifying the acting group and homogeneous space ([R2](references.md)).

### Why split-complex is geometrically substantial

Set $p=x+y$ and $q=x-y$. A boost becomes

$$p\longmapsto e^t p,\qquad q\longmapsto e^{-t}q,\qquad x^2-y^2=pq.$$

Yes: split arithmetic is exactly componentwise real arithmetic in these coordinates. This is an isomorphism, not an approximation. The same coordinates expose the two lightlike directions. Split conjugation exchanges them, and their product is the invariant. The boost's opposite scale factors therefore have a precise relation.

Changing coordinates does not erase geometry. To express that geometry, carry the form, conjugation and interpretation of the coordinates along with the arithmetic. Null divisors such as $1+j$ and $1-j$ then identify null directions; they are geometrically meaningful even though division by them fails. This agrees with the [split-complex treatment by Dray and Manogue](https://books.physics.oregonstate.edu/GELG/csplit.html).

### Why dual multiplication describes finite motion

The nilpotent relation gives an exact shear for **any finite real $t$**:

$$(1+t\varepsilon)(v+\varepsilon x)=v+\varepsilon(x+tv).$$

With this deliberately chosen state encoding, multiplication advances a freely moving point by time $t$, holding velocity fixed. Units must be assigned consistently to the two coordinates and the parameter. There is no small-time approximation, and

$$(1+t\varepsilon)(1+s\varepsilon)=1+(t+s)\varepsilon.$$

The vanished square removes quadratic feedback, not motion. Epsilon is a formal square-zero direction, not a nonzero real number and not an invertible infinitesimal in an ordered field. The same algebra also describes first-order neighborhoods of curves and surfaces; these are different, compatible interpretations of its multiplication law.

## Every nonscalar real 2 by 2 generator has one of these types

Take any real matrix $M$ and write

$$a=\frac{\operatorname{tr}M}{2},\qquad B=M-aI,\qquad
\Delta=a^2-\det M.$$

Cayley–Hamilton gives **$B^2=\Delta I$**. If $B\ne0$, the algebra spanned by $I,B$ is complex for $\Delta<0$, split-complex for $\Delta>0$, and dual for $\Delta=0$. Normalize $B$ by $\sqrt{|\Delta|}$ in the first two cases. If $B=0$, only scalar scaling remains; it is not a faithful dual algebra.

This is a classification of each generator's algebra, not a simultaneous identification of all real matrices with commuting scalars. Different generators generally do not commute.

The complete exponential follows without diagonalization:

$$e^{tM}=e^{at}\bigl(C_\Delta(t)I+S_\Delta(t)B\bigr),$$

$$C_\Delta(t)=\sum_{n\ge0}\frac{\Delta^n t^{2n}}{(2n)!},\qquad
S_\Delta(t)=\sum_{n\ge0}\frac{\Delta^n t^{2n+1}}{(2n+1)!}.$$

| Sign | $C_\Delta(t)$ | $S_\Delta(t)$ |
| --- | --- | --- |
| $\Delta=-\omega^2<0$ | $\cos(\omega t)$ | $\sin(\omega t)/\omega$ |
| $\Delta=0$ | $1$ | $t$ |
| $\Delta=\kappa^2>0$ | $\cosh(\kappa t)$ | $\sinh(\kappa t)/\kappa$ |

The series are entire in $\Delta$. The parabolic case is the regular meeting point of the other two, even when eigenvector formulas become singular. A robust implementation should evaluate this family across zero rather than divide small differences or normalize a vanishing discriminant.

### Mechanical damping and electrical resonance

After dividing by mass or inductance, both a linear damped mechanical oscillator and a series RLC circuit's unforced charge equation have the form

$$\ddot q+2\gamma\dot q+\omega_0^2 q=0,\qquad
M=\begin{pmatrix}0&1\\-\omega_0^2&-2\gamma\end{pmatrix}.$$

For the RLC model, $\gamma=R/(2L)$ and $\omega_0^2=1/(LC)$. Here $a=-\gamma$ and $\Delta=\gamma^2-\omega_0^2$:

| Regime, with $\gamma\ge0,\omega_0>0$ | Algebra after factoring out $e^{-\gamma t}$ | Observable behavior |
| --- | --- | --- |
| Underdamped | Complex | Oscillation with decaying envelope |
| Overdamped | Split-complex | Two different decay rates |
| Critically damped | Dual | $q(t)=e^{-\gamma t}[q_0+(v_0+\gamma q_0)t]$ |

The dual term is essential to the critical solution. The three geometries are regimes of the **same physical equation**, including a meaningful transition between them.

For sinusoidal steady state, voltage and current are each separate complex phasors, related by $V=ZI$. They are not generally the real and imaginary parts of one number. Complex coordinates encode amplitude and phase; the circuit's laws determine the relation between the two phasors ([MIT circuit notes](https://ocw.mit.edu/courses/6-071j-introduction-to-electronics-signals-and-measurement-spring-2006/96c80ce0d5513139310a9526fdadb419_sss_phsor_impdce.pdf)).

## Two parabolic elements can produce another geometry

Consider normalized, lossless paraxial ray coordinates. Free propagation through length $L$ and a thin lens of focal length $f\ne0$ act by

$$P_L=\begin{pmatrix}1&L\\0&1\end{pmatrix},\qquad
F_f=\begin{pmatrix}1&0\\-1/f&1\end{pmatrix}.$$

Both are $I+N$ with nonzero $N^2=0$ when their parameters are nonzero. Their ordered product is

$$T=P_LF_f=\begin{pmatrix}1-L/f&L\\-1/f&1\end{pmatrix},\qquad
\det T=1,\quad\operatorname{tr}T=2-L/f.$$

For a periodically repeated cell with $L/f>0$, $0<L/f<4$ is elliptic and has bounded ray iterates; $L/f>4$ is hyperbolic with a growing direction. At $L/f=4$, $N=T+I\ne0$ satisfies $N^2=0$:

$$T^n=(-1)^n(I-nN).$$

This boundary has linear growth for generic rays. The scalar exceptional matrices $\pm I$ require separate treatment. The calculation above is checked exactly for three rational cells; the broader optics/group connection is established in [Bașkal and Kim](https://arxiv.org/abs/1204.5071).

There is a second description using the fractional-linear map $z\mapsto(az+b)/(cz+d)$. Its fixed-point equation is

$$cz^2+(d-a)z-b=0,\qquad D=(\operatorname{tr}T)^2-4\det T.$$

Thus the same discriminant controls fixed-point collision on the real projective boundary. In the usual complex Gaussian-beam description, the upper-half-plane fixed point of an elliptic cell provides its repeated beam parameter. Real rays, complex beam parameters and critical shear meet in one transformation law.

**Implementation consequence:** retain the full matrices and their order. `ModeOperator` already represents these maps exactly. Multiplying two scalar epsilon exponentials cannot substitute for the two different, noncommuting lens/propagation generators. The older `M2R` canonicalization is not an associative operator representation; see [compatibility](../compatibility.md).

## Polarization makes the circular and hyperbolic connection visible

Let $H$ be a positive Hermitian coherency matrix, with $H=\psi\psi^\dagger$ for a fully coherent Jones vector $\psi=(u,v)$. Choose

$$H=\frac12\begin{pmatrix}S_0+S_1&S_2+iS_3\\S_2-iS_3&S_0-S_1\end{pmatrix}.$$

Then

$$4\det H=S_0^2-S_1^2-S_2^2-S_3^2.$$

For any Jones matrix $G$ with determinant one, $H\mapsto GHG^\dagger$ preserves this Lorentzian expression. Pure states lie on its future null cone; partially polarized states lie inside it. The $S_3$ sign here is an explicit convention.

| Determinant-one Jones action | Stokes geometry |
| --- | --- |
| $\operatorname{diag}(e^{i\phi/2},e^{-i\phi/2})$ | Rotation of $(S_2,S_3)$ by $\phi$ |
| $\operatorname{diag}(e^\rho,e^{-\rho})$ | Boost of $(S_0,S_1)$ with rapidity $2\rho$ |
| $\begin{pmatrix}1&t\\0&1\end{pmatrix}$, real $t\ne0$ | Parabolic Lorentz transformation |

This established bridge is described by [Han, Kim and Noz](https://arxiv.org/abs/physics/9707016). Our rational examples check determinant preservation and explicit rotation/boost coefficients. An arbitrary determinant-one matrix need not be passive; attenuation factors must be restored for a physical device. Depolarizing Mueller maps require a larger model. The algebra alone does not identify physical space-time with polarization.

In the library, a Jones state can occupy the two split components of a CS value. Multiplication by $e^{ij\phi/2}$ performs the displayed relative phase change, while $e^{j\rho}$ performs the reciprocal amplitude change. These are direct mixed-generator meanings. General polarization mixing uses `ModeOperator`; CD coefficients can additionally carry first variations if desired. A reusable coherency/Stokes API and physical component models remain unimplemented.

## A full polar form for all eight dimensions

Write a value as $X=A+\varepsilon B$, where $A,B$ are complex–split values, and assume $A$ is invertible. Define

$$v=A^{-1}B=v_0+v_j\,j+v_i\,i+v_{ij}\,ij.$$

Let $z_+,z_-$ be the two nonzero complex components of $A$. Select arguments $\alpha_+,\alpha_-$ and set

$$r=\sqrt{|z_+||z_-|},\quad
\rho=\tfrac12\log\frac{|z_+|}{|z_-|},\quad
\theta=\tfrac12(\alpha_++\alpha_-),\quad
\phi=\tfrac12(\alpha_+-\alpha_-).$$

Every such value has the factorization

$$\boxed{X=r\,e^{j\rho}\,e^{i\theta}\,e^{ij\phi}\,(1+\varepsilon v).}$$

It follows by evaluating $j$ at $+1$ and $-1$, then using $\varepsilon^2=0$. The factors themselves live in the full union.

| Coordinate | Geometric/group meaning | Real parameters |
| --- | --- | --- |
| $r>0$ | Common scale | 1 |
| $\rho$ | Reciprocal hyperbolic stretching | 1 |
| $\theta$ | Common circular phase | 1 |
| $\phi$ | Opposite circular phases generated by $ij$ | 1 |
| $v$ | Four commuting nilpotent shear directions | 4 |

The final four parameters need not be interpreted as derivatives. Multiplication by $1+\varepsilon v$ sends a general state $C+\varepsilon D$ to $C+\varepsilon(D+vC)$: a shear between two four-dimensional layers.

For products, scales multiply and $\rho,\theta,\phi,v$ add, subject to the phase identifications. This is a direct analogue of the usefulness of ordinary complex polar form.

### Branches and singular strata are part of the geometry

Changing the component arguments by $2\pi m,2\pi n$ changes

$$(\theta,\phi)\longmapsto
(\theta+\pi(m+n),\ \phi+\pi(m-n)),\qquad m,n\in\mathbb Z.$$

In particular, shifting both angles by $\pi$ does nothing to $X$. Treating each angle as independently unique modulo $2\pi$ would double-count values. The unit group is

$$\mathcal A_{\mathbb R}^{\times}\cong
(\mathbb R_{>0})^2\times(S^1)^2\times(\mathbb R^4,+).$$

This product description retains the geometry; it identifies its topology precisely. It also explains why the logarithm has two independent winding integers.

The polar form does not cover zero divisors. If one body component vanishes, its phase is undefined; if both vanish, the value lies entirely in the square-zero ideal. These strata need their own charts and invariants. Even with rational input, logarithmic and angular coordinates generally leave rational coefficients.

**Current status:** scalar exponentials, logarithms and Euler-component accessors exist. The formula is derived and its reconstruction, multiplication law and branch lattice are checked on 72 moderate inputs. A structured polar object, branch continuation, singular-stratum classification and robust conditioning diagnostics are missing. Existing inverse/logarithm cancellation near tiny components is still an open correctness issue; the bounded check does not remove it.

## The projective completion is tangent geometry on a quadric

This construction concerns the library's **projective line over the algebra**, not the affine scalar algebra itself. Over real coefficients,

$$\mathcal A_{\mathbb R}\cong\mathbb C[\varepsilon]\times\mathbb C[\varepsilon],
\qquad\varepsilon^2=0.$$

A unimodular homogeneous pair over this product is exactly one such pair over each factor. Unit rescaling also separates. Consequently

$$\mathbb P^1(\mathcal A_{\mathbb R})\cong
\mathbb P^1(\mathbb C[\varepsilon])\times
\mathbb P^1(\mathbb C[\varepsilon]).$$

To identify either factor geometrically, examine its overlapping affine charts:

$$z+\varepsilon w\longmapsto
\frac1{z+\varepsilon w}=\frac1z-\varepsilon\frac{w}{z^2},\qquad z\ne0.$$

The body changes by $z\mapsto1/z$, and the extra coordinate changes by its derivative. This is exactly the transition law of the **holomorphic tangent bundle** of the complex projective line. Dual-valued points and tangent vectors have a standard general treatment in the [Stacks Project](https://stacks.math.columbia.edu/tag/0B28).

The two complex projective lines also form a smooth quadric through the Segre map:

$$([s:t],[u:v])\longmapsto[su:sv:tu:tv],\qquad
Q:\ X_0X_3-X_1X_2=0\ \subset\mathbb {CP}^3.$$

Fixing either input gives one of its two families of projective lines. These are the two rulings of the quadric; see [Vakil's treatment](https://math.stanford.edu/~vakil/0708-216/216class1516.pdf). Combining the explicitly described charts gives

$$\boxed{\mathbb P^1(\mathcal A_{\mathbb R})\cong
T(\mathbb {CP}^1\times\mathbb {CP}^1)\cong TQ.}$$

Here $T$ is the holomorphic tangent bundle, viewed also as a real eight-dimensional manifold. The quadric has complex dimension two; its tangent bundle has complex dimension four. Thus the split factors identify two line families on one surface, the complex directions provide its projective complex geometry, and the dual extension records tangent directions on that surface.

This identification is derived from the chart laws above. The probe checks rational examples of the quadric equation, its linearized equation, unit rescaling and all four chart combinations. It does not establish global topology by sampling; that conclusion uses the gluing argument. `ExactUltra` supplies a rational subset of this geometry, not all complex points.

A further algebraic connection is the determinant

$$\det\begin{pmatrix}t+z&x-iy\\x+iy&t-z\end{pmatrix}
=t^2-x^2-y^2-z^2.$$

Over complex coordinates, its projectivized null cone is the same smooth quadric after an invertible linear coordinate change. Real space-time requires a Hermitian reality condition, which relates the two projective factors. It does not follow merely from having eight scalar coefficients. This gives a precise research path toward conformal/null geometry, with explicit reality conditions instead of an assertion of additional physical dimensions.

## Analyticity connects the algebras to different field equations

For $u^2=s$ and $F(x+uy)=f(x,y)+ug(x,y)$, require the differential to be multiplication by one algebra value. For sufficiently smooth $f,g$ this gives

$$F_y=uF_x\quad\Longleftrightarrow\quad f_y=s g_x,\quad g_y=f_x.$$

Differentiating once more gives $f_{yy}=s f_{xx}$ and $g_{yy}=s g_{xx}$:

| Algebra | Component equations | Geometric/physical direction |
| --- | --- | --- |
| C | Laplace equation | Harmonic potentials, local conformal maps |
| S | Wave equation | Characteristics and left/right propagation |
| D | $f_y=0$, $g_y=f_x$ | First-order contact and tangent extension |

On a local product domain the dual solution is $F=f(x)+\varepsilon[yf'(x)+h(x)]$. This is a degenerate analytic structure, **not the heat equation**. The split case has a developed analysis, including a hyperbolic Cauchy integral formula ([Libine](https://arxiv.org/abs/0712.0375)); singularities on characteristic directions require different treatment from ordinary complex contour arguments.

For a smooth constraint $G(x,y)=0$, substitution of $(x+\varepsilon a,y+\varepsilon b)$ gives both the point equation and $G_xa+G_yb=0$. This makes contact geometry computationally accessible. At singular points, linearized solutions can exceed actual curve directions: for $G=xy$ at the origin every $(a,b)$ satisfies the first-order equation, but an actual differentiable curve with that initial velocity must have $ab=0$.

Here contact means first-order tangency of curves or constraints. A contact distribution in the more specialized sense has not been specified.

The full union offers a common coefficient language for these equations, their transformations and local variations. A multi-variable domain, regularity condition and physical boundary data must still be defined. Evaluating scalar `sin`, `log` or `exp` does not supply a mixed-algebra field theory or PDE solver.

## What each combination contributes

| Combination | Natural geometric structure to investigate | Useful meeting point |
| --- | --- | --- |
| C | Circle phases and complex projective line | Oscillation, harmonic fields, optical beam parameter |
| S | Null axes and reciprocal scales | Characteristics, boost invariants, growth/decay modes |
| D | Finite shear and first-order neighborhoods | Free propagation, critical Jordan motion, tangent constraints |
| CS | Two circular phases plus common/relative scale | Polarization state and diagonal Jones actions |
| CD | Tangent directions on complex curves | Contact of conformal/projective maps and their deformations |
| SD | Tangent directions attached to both null components | Varying characteristics, boost/shear geometry |
| CSD | Full polar group and projective tangent quadric | Shared phase, null, projective and contact constructions |

Different rows refer to explicitly constructed spaces or actions; they are not all metrics on the same affine plane. The [operation atlas](operations.md) separately compares arithmetic, roots, trigonometry, integration and other computational domains for all seven combinations.

## A geometry-first development sequence

Correctness and exact coefficient preservation remain the first gate. After that, prioritize these concrete deliverables:

1. **Full polar and singular geometry** — a structured decomposition, reconstruction, correct phase lattice, winding histories and zero-divisor strata. Test branch loops and coefficient-level accuracy, including cases excluded by the current bounded probe. Extends G01/G07 into G16.
2. **Continuous EPH dynamics** — the entire $C_\Delta,S_\Delta$ family, full generator metadata, stable operator exponentials and exact Cayley steps. Use one mechanical/RLC equation and one optical cell as linked demonstrations across the critical transition. G05/G14.
3. **Projective and contact geometry** — reciprocal-chart tangent transitions, conics/quadrics, incidence and real structures. Connect the existing projective point API to the explicit $TQ$ construction and distinguish infinitesimal flexes from realizable finite motion. G04/G08/G17.
4. **Polarization and transfer geometry** — coherency/Stokes observables, model-specific invariants, passive component models and ordered composition. Compare scalar diagonal actions to the existing general operator layer, and then add perturbations where useful. G14/G17.
5. **An analysis of fields over the three geometries** — domains, Cauchy–Riemann operators, characteristics, contour/integral contracts and carefully specified mixed extensions. Begin with polynomial identities and boundary-value examples. G18, with G12 numerical integration support.

One design trap deserves a specific rule: **a geometric epsilon and an independent perturbation epsilon must not silently be identified**. Doing so would discard mixed information. Introduce an independent coefficient extension when needed, or retain a nilpotent geometry operator separately from the coefficient epsilon. The latter is already possible with `ModeOperator`; the probe verifies that their product need not vanish. This is G19, an explicit extension beyond the original eight-dimensional scalar algebra.

These projects pursue geometry first, while retaining derivatives as a valuable operation within it. The aim is a coherent language with verified conversions, invariants and singular cases. Whether it outperforms established matrix, geometric-algebra or symbolic tools must be measured on concrete tasks; no such general advantage is established here.
