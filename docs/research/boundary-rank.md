# Boundary coefficients determine two Toeplitz block ranks

**Research note · Ultracomplex Math · November 2026**

**Abstract.** We compute the rank of a rectangular window of the convolution
kernel $(1+z+\cdots+z^d)^\ell$ for $\ell=1,2$. Two short tails of a product
polynomial encode its entire nullspace. Counting their exponents modulo $d+1$
gives the first-power rank over any field and the second-power rank in
characteristic zero. Each block requires a bounded number of integer operations.
The first-power aggregate formula is available in the [companion proof](first-power-rank.md).

## Statement

Let $r,q\ge1,\ d\ge0,\ D=d+1,\ K=1+z+\cdots+z^d,\ s=\ell d$.
Choose $0\le c\le s$ with $0\le q-r+c\le s$.
The $r\times q$ matrix has entries $R_{ij}=[z^{c+j-i}]K^\ell$, indexed from zero
and extended by zero outside the coefficient range. Put $a=q+c-r,\ b=q+c,\ e=q+s$.
In the two disjoint half-open intervals $E=[0,a)\cup[b,e)$ of integer exponents,
let $m_t$ count members congruent to $t\bmod D$, for $0\le t<D$.
Write $n_0,n_1$ for the numbers of empty and singleton classes, and $x_+=\max(0,x)$.

| Power and field | Nullity of $R$ |
| --- | --- |
| $\ell=1$, any field | $\sum_t(m_t-1)_+ + \mathbf1_{n_0=0}$ |
| $\ell=2$, characteristic zero | $\sum_t(m_t-2)_+ + \mathbf1_{n_0=0}(2-n_1)_+$ |

**Rank is $q-\mathrm{nullity}$**. The block defect is $\min(r,q)-\mathrm{rank}$.
For Noferini's Definition 4.10 take $r=u(k-s), q=u(k), c=\min(s,\max(0,k-n))$,
where $u(k)=\min(k,m,n,m+n-k)$, $m\le n$, and $s+1\le k\le m+n-1$.
Summing the block ranks gives the operator rank for that power. If the index
range is empty, the rank is zero.

## Proof

Encode a column vector $v$ as $V(z)=\sum_{j=0}^{q-1}v_j z^{q-1-j}$.
Row $i$ of $Rv$ extracts coefficient $b-1-i$ from $W=K^\ell V$.
The rows therefore require every coefficient in $[a,b)$ to vanish.
Multiplication by $K^\ell$ identifies the kernel bijectively with polynomials
supported in $E$ that are divisible by $K^\ell$. Indeed each such polynomial
has degree below $q+s$, so its quotient has degree below $q$.

**First power.** Reduce $W$ modulo $z^D-1=(z-1)K$. Its coefficient at
residue $t$ becomes the sum of the weights in that class. Since the remainder
has degree less than $D$, it is divisible by $K$ precisely when all residue
sums have one common value. Each nonempty class contributes $m_t-1$ free
weights once this value is fixed. An empty class forces the common value to zero.
This proves the first assertion, including in positive characteristic.

**Second power.** In characteristic zero, $K$ has simple, nonzero roots
(the nontrivial $D$-th roots of unity in a splitting field). Thus $K^2\mid W$
exactly when both $W$ and $zW'$ are divisible by $K$.
Applying the preceding remainder argument twice requires the pairs
$$
\left(\sum_{k\equiv t}w_k,\ \sum_{k\equiv t}k\,w_k\right)
$$
to be the same pair $(A,B)$ for all $t$. In class $t$ the moment map has
columns $(1,k)$. Two different exponents give determinant $k'-k\ne0$.
The local kernel contributes $(m_t-2)_+$. The set of feasible common pairs is
the intersection of the local images. An empty class forces $(0,0)$.
With no empty classes, a singleton at $k$ imposes $B=kA$. Two singleton
classes have distinct exponents and force both moments to zero. Zero or one
singleton leaves two or one common dimensions, respectively. Summing local
kernel dimensions and the dimension of the common image proves the formula. ∎

## Computation and checks

The number of exponents below $N$ in residue class $t$ is
$\lfloor(N+D-1-t)/D\rfloor$. Hence the counts $m_t$ change only at the
residues of $a,b,e$. Summing over at most four constant intervals gives the
stated arithmetic complexity, even when the block could never be materialized.

* Noferini's Example 4.17 gives $r=q=3,d=3,c=1,\ell=2$.
  The tails have exponents $0,4,5,6,7,8$. Their counts are $3,1,1,1$.
  Nullity is one and rank is two. The vector $(1,-2,1)$ lies in the kernel.
* For $r=q=2,d=c=1,\ell=2$, the matrix has diagonal 2 and off-diagonal 1.
  It has rank two over the rationals and rank one over the field of three
  elements. This example explains the field assumption and the importance of
  retaining the convolution weights.

The [implementation](../../examples/novelty_models.py) and
[verification program](../../tools/novelty_probe.py) compare against exact
rational elimination and a separate monomial-basis construction of the squared
operator. The [full report](novelty-verification.json) records the grid and counts.

## Scope and provenance

[Noferini, arXiv:2512.08399v5, §4.3](https://arxiv.org/html/2512.08399v5#S4.SS3)
asks for the rank defects for all powers in Problem 4.19.
The [higher-power note](higher-power-rank.md) computes the intersections of moment images for arbitrary positive powers and gives the cubic classification.
The first-power graph proof also relates to [Evans, Greene and Van Veen](https://emis.de/ft/34371).
Convolution, polynomial divisibility and confluent Vandermonde rank are classical.
The priority of these particular block formulas awaits specialist literature
review and independent assessment.
