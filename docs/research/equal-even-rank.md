# Equal Jordan sizes and even powers

Let $h_d(x,y)=\sum_{j=0}^d x^j y^{d-j}$ act by multiplication on $F[x,y]/(x^m,y^m)$, with $m\ge1$, $d\ge0$ and $F$ a field of characteristic zero. For every positive even power $\ell=2s$, **each existing graded block has its maximum possible rank**, and the total rank is

$$\operatorname{rank}(h_d^{2s})=\max(0,m-sd)^2.$$

The following proof applies directly to the indexing in [Noferini, Definition 4.10 and Problem 4.19](https://arxiv.org/html/2512.08399v5#S4.SS3). It gives a family recognizable from the parameters alone.

## A square minor inside every block

Put $H=sd$, $D=2H$, $K(z)=1+z+\cdots+z^d$ and $\gamma_j=[z^j]K^{2s}$, taking missing coefficients to be zero. Block $R_k$ has entries $\gamma_{c+j-i}$, for zero-based indices. For $D+1\le k\le2m-1$ its shape is
$$r=u(k-D),\qquad q=u(k),\qquad c=\min(D,(k-m)_+),\qquad u(t)=\min(t,2m-t).$$

Since $u(t)=t-2(t-m)_+$ on this interval and its translate back by $D$, we get $q-r=D-2c$. Set $b=\min(r,q)$. If $q\ge r$, select $b$ consecutive columns starting at $(q-r)/2=H-c$ and keep all rows. If $r>q$, select $b$ rows starting at $(r-q)/2=c-H$ and keep all columns. Both starts are nonnegative integers within the block. The selected square has entries $\gamma_{H+j-i}$.

## The centered square is a Gram matrix

Let $v_a=[z^a]K^s$, extended by zero outside $0,\ldots,H$. Symmetry gives $v_{H-a}=v_a$. Hence $\gamma_{H+t}=\sum_a v_a v_{a-t}$. The centered square is the Gram matrix of the coefficient vectors of $K^s,zK^s,\ldots,z^{b-1}K^s$ under the ordinary real dot product. These vectors are independent: any relation gives $K^s\sum_j c_j z^j=0$ in the polynomial ring. Their Gram determinant is therefore a positive integer. It stays nonzero in every field of characteristic zero. This proves $\operatorname{rank} R_k=b$.

**More general shortcut.** For an admissible rectangular window with offset $c$ and even power, the same minor fits whenever $H$ lies between $c$ and $c+q-r$, inclusive. Select columns starting at $H-c$ for a wide window or rows starting at $c-H$ for a tall one. The [block algorithm](../../examples/moment_ranks.py) uses this sufficient condition and its existing moment reduction for the remaining windows.

## Summing the ranks

Here $b=\min(k-D,2m-k)$. The image spaces for distinct source degrees occur in distinct target degrees, so the ranks add. If $N=m-H>0$, the sequence of ranks is $1,2,\ldots,N,\ldots,2,1$, with sum $N^2$. For $N\le0$ the admissible index range is empty and the multiplication operator vanishes. The argument includes $d=0$, which gives the identity.

```python
from examples.moment_ranks import equal_even_power_rank

assert equal_even_power_rank(5, 2, 2) == 9
assert equal_even_power_rank(5, 2, 6) == 0
assert equal_even_power_rank(10**30, 3, 4) == (10**30 - 6) ** 2
```

## Boundaries and prior work

* **Unequal sizes.** At $(m,n,d,\ell,k)=(4,8,3,2,9)$ the 3-by-3 block has rank 2 (Noferini's Example 4.17).
* **Odd power.** At $(6,6,2,1,7)$ a 5-by-5 block has rank 4 (Example 4.18).
* **Positive characteristic.** At $(3,3,1,2,4)$ the centered square has rows $(2,1),(1,2)$ and determinant 3. Its rank drops modulo 3.

Noferini formulates the general classification and gives the first two examples in [§4.3](https://arxiv.org/html/2512.08399v5#S4.SS3). The positive Toeplitz quadratic form for a nonnegative symbol is classical; see [Gray, *Toeplitz and Circulant Matrices*, §4.1](https://ipgold.epfl.ch/~leveque/Matrix/gray.pdf). In this case the symbol is exactly $|K(e^{it})|^{2s}$, and the finite Gram construction gives the proof above. The scoped contribution here is the placement of a maximal centered minor and the resulting aggregate rank for this family. A literature check establishes these connections; priority for this specialization remains unverified. The [moment reduction](higher-power-rank.md) handles other shapes blockwise.

For reproduction, run `python tools/novelty_probe.py --full`. The [report](novelty-verification.json) records 2,517 explicit rational block ranks for $2\le m\le16$ and powers 2, 4, 6, 8 and 10, plus independent full multiplication-matrix checks and empty index ranges.
