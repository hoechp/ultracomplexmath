# A closed rank formula for the first power

[Research investigations](novelty.md) · [Executable prototypes](../../examples/novelty_models.py) · [Verification report](novelty-verification.json)

**Status:** a derivation supplied here, with independent exact checks. Publication novelty has not been established. The graph method is classical; the specific closed classification below is the candidate contribution. No claim is made to solve the higher-power problem.

## The precise subproblem

Vanni Noferini's [arXiv:2512.08399v5](https://arxiv.org/abs/2512.08399v5), Definition 4.10 and Problem 4.19, asks for the rank losses of a family of Toeplitz blocks. We address **all parameters with power ℓ=1**. Fix positive integers m≤n and d≥1, and write

\[
u(k)=\min(k,m,n,m+n-k),\qquad d+1\le k\le m+n-1.
\]

The first-power block has r=u(k−d) rows, q=u(k) columns, offset c=min(d,max(0,k−n)), and zero-based entries

\[
(R_k)_{ij}=\begin{cases}1&0\le j-i+c\le d,\\0&\text{otherwise}.\end{cases}
\]

Let N_s be the nilpotent Jordan block of size s. The block ranks sum to the rank of

\[
H_d=\sum_{i=0}^{d}N_m^i\otimes N_n^{d-i}.
\]

The statements below hold over **any field**, because the proof uses graph incidence, without division by a characteristic-dependent integer. Noferini's matrix-function setting has its own field assumptions; this claim concerns the displayed 0–1 matrices themselves.

## Individual blocks: a residue count

More generally let R be any r×q matrix of the displayed form, where r,q≥1, d≥0, 0≤c≤d, and 0≤q−r+c≤d. These conditions say that the upper-left and lower-right entries are both 1. If r<q, transpose and replace c by d−c. We can therefore assume r≥q.

Set D=d+1 and, for an integer T≥0, define

\[
F_c(T)=\left\lfloor\frac{T}{D}\right\rfloor(D-c)
       +\max(0,(T\bmod D)-c).
\]

Then the closed formula is

\[
\boxed{\operatorname{rank}R=q-\max\{0,F_c(q+c)-F_c(r-1)-1\}.}
\]

### Proof

Apply the injective first-difference map

\[
(x_0,\ldots,x_{r-1})\longmapsto
(x_0,x_1-x_0,\ldots,x_{r-1}-x_{r-2},-x_{r-1}).
\]

Column j of R is an interval of ones. Its first difference is

\[
e_{\max(0,t-D)}-e_{\min(r,t)},\qquad t=j+c+1.
\]

Thus the transformed matrix is an oriented incidence matrix on vertices 0,…,r, with one edge per column, indexed by c+1≤t≤c+q. The first-difference map preserves the column rank.

Every interior edge joins vertices a distance D apart. Consequently, interior components are paths in individual residue classes modulo D. At each interior vertex there is at most one edge in each direction. Edges from 0 start in distinct residue classes, since their indices lie in [c+1,D]. Edges into r also end in distinct residue classes: their index range [r,q+c] has length at most c+1≤D. The corner assumptions give r≤q+c.

It follows that every cycle arises from two different paths joining 0 to r. All remaining pieces are trees, possibly attached to these boundary vertices. A terminal edge with index t∈[r,q+c] is connected back to 0 exactly when the representative of t modulo D in {1,…,D} is at least c+1. The intervening indices are present because the complete edge-index range is consecutive. The number of such boundary-to-boundary paths is therefore

\[
P=F_c(q+c)-F_c(r-1).
\]

P paths between the same two endpoints contribute max(0,P−1) independent cycles. An incidence matrix with q edges has rank q minus the dimension of its cycle space: a spanning forest has independent columns by leaf elimination, and each additional edge closes one cycle. This argument works in every characteristic. Hence rank R=q−max(0,P−1), as asserted. ∎

For example, the 5×5 tridiagonal all-ones band (d=2,c=1) becomes two paths 0→2→5 and 0→3→5, plus the isolated edge 1→4. Its single cycle gives rank 4; a kernel vector is (1,−1,0,1,−1). This is also the block in Noferini's Example 4.18.

## All blocks at once: squares and consecutive products

Define the total defect relative to the maximum possible block ranks by

\[
\Delta(m,n,d)=\sum_{k=d+1}^{m+n-1}
 \bigl(\min(u(k),u(k-d))-\operatorname{rank}R_k\bigr).
\]

If d≥m+n−1, there are no blocks, H_d=0 and Δ=0. Otherwise set

\[
K=m-n+d.
\]

If K≤0, then Δ=0. If K>0, set

\[
v=m\bmod(d+1),\quad
h=\max\{\min(K,v-1),K-v\},\quad
L=\max\left(0,h-\left\lceil K/2\right\rceil\right).
\]

The complete first-power classification is

\[
\boxed{\Delta(m,n,d)=L\bigl(L+(K\bmod2)\bigr).}
\]

Thus **some block is rank deficient exactly when L>0**. The total defect is a square for even K and a product of consecutive integers for odd K. For d<m+n−1, define S=m+n−d and a=min(m,⌊S/2⌋). This also gives

\[
\boxed{\operatorname{rank}H_d=a(S-a)-\Delta(m,n,d).}
\]

This calculation uses a fixed number of integer operations, with no matrices and no sum over k. It is not a constant-bit-cost claim for arbitrarily large integers.

### Proof of the total formula

The blocks with c=0 or c=d have a triangular maximal minor with diagonal entries 1. The remaining blocks have 0<c<d. Reflection k↦m+n+d−k preserves their ranks and exchanges their row and column counts. It exchanges offsets c and K−c. We therefore count only c≥⌈K/2⌉, where r≥q.

In this half, q=m−c and r=min(n+c−d,m). If K≤0, or if c≥K, then r=m=q+c. The path-count interval has one element, so no rank is lost. In the remaining cases,

\[
r=m-K+c,\qquad q+c=m,\qquad K\le d.
\]

The path count is the count of residues in the interval [m−K+c,m] whose representatives in {1,…,D} exceed c. This interval has length K−c+1≤D and therefore wraps at most once. Put A=K−c; since c≥⌈K/2⌉, A≤c.

If v>A, the interval does not wrap. Counting its residues above c gives defect

\[
\max(0,\min(K,v-1)-c).
\]

If v≤A, it wraps (including v=0). Its upper segment has A−v+1 eligible residues. Its lower segment has none, since v≤A≤c. The defect is A−v=K−v−c. Combining the two cases gives the particularly simple block defect

\[
\max(0,h-c).
\]

The positive defects on the chosen half are therefore L,L−1,…,1. No domain endpoints truncate this list: h≤K≤d; also h≤m−1, because when m≥D this follows from K≤d, and when m<D it follows from v=m and K≤2m−2. A positive defect has c<h, so all listed blocks exist and have positive dimensions.

Reflection doubles the sum L(L+1)/2. For even K there is a central block c=K/2 that must be counted only once, subtracting L. This yields L² for even K and L(L+1) for odd K.

Finally,

\[
\sum_k\min(u(k),u(k-d))
=\sum_{t=1}^{S-1}\min(t,m,S-t)=a(S-a).
\]

Subtracting Δ proves the total rank formula. ∎

## Consequences and limits

For m=n, H_d is similar to the matrix representing the Fréchet derivative of X↦X^(d+1) at N_m. Its kernel counts perturbation directions invisible to first order. This is a direct use of the polynomial derivative identity, rather than a new physical model.

If 2d≥m+n−1, H_d²=0 by degree. In that region its entire Jordan form follows from the rank r: r blocks of size 2 and mn−2r blocks of size 1. Outside that region, the first-power rank alone does not determine the Jordan form.

| m | n | d | Sum of maximal block ranks | Actual rank | Defect |
| --- | --- | --- | --- | --- | --- |
| 4 | 4 | 4 | 4 | 3 | 1 |
| 5 | 5 | 4 | 9 | 5 | 4 |
| 6 | 6 | 2 | 25 | 24 | 1 |

The formula does **not** apply to higher powers by replacing d with ℓd. At m=n=3,d=1,ℓ=2,k=4, the weighted block is [[2,1],[1,2]], of rank 2 over Q; its 0–1 support is the all-ones matrix, of rank 1. Weighted convolution information is essential.

The [full probe](../../tools/novelty_probe.py) checks 5,565 interval matrices by rational elimination and independently by graph components; 12,869 blocks for 1,638 parameter triples; and 196 full tensor operators built directly in a monomial basis. These finite tests support the implementation. The proof supplies the general statement; neither tests nor proof establish publication priority.

## Prior art and remaining review

Graph interpretations of Toeplitz nullspaces are established: [Evans, Greene and Van Veen (2021)](https://emis.de/ft/34371) study a different, zero-diagonal symmetric band family through graph cycles. Their result must not be confused with novelty of the present incidence construction. Consecutive-ones matrices also belong to classical network-matrix theory.

The specific residue-count specialization and the aggregate L²/L(L+1) formula were not located in the bounded source search recorded in the [investigation note](novelty.md#sources-and-search-boundaries). A specialist review of interval/network matrices and banded Toeplitz rank formulas remains necessary before presenting this as a new published result.
