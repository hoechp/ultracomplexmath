"""Independent, bounded checks for the three scoped novelty investigations.

Run ``python tools/novelty_probe.py --full --output PATH`` to reproduce the
checked-in report. Only --output writes a file. No plotting dependency is needed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from fractions import Fraction as F
from itertools import product
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from examples.novelty_models import (  # noqa: E402
    QNULL,
    corrected_critical_cayley,
    critical_center,
    critical_polynomial,
    direct_reciprocal,
    first_power_defect,
    first_power_rank,
    interval_band,
    interval_band_rank,
    toeplitz_block,
    toeplitz_shape,
)
from ultracomplexmath import ExactUltra, ModeOperator, Ultra, __version__  # noqa: E402


def rational_rank(matrix):
    """Ordinary rational Gaussian elimination; no Ultra or closed rank formula."""
    if not matrix:
        return 0
    a = [list(map(F, row)) for row in matrix]
    rows, columns, rank = len(a), len(a[0]), 0
    if any(len(row) != columns for row in a):
        raise ValueError("Rectangular matrix required")
    for column in range(columns):
        pivot = next((i for i in range(rank, rows) if a[i][column]), None)
        if pivot is None:
            continue
        a[rank], a[pivot] = a[pivot], a[rank]
        for i in range(rank + 1, rows):
            if a[i][column]:
                factor = a[i][column] / a[rank][column]
                for j in range(column, columns):
                    a[i][j] -= factor * a[rank][j]
        rank += 1
        if rank == rows:
            break
    return rank


def interval_graph_rank(matrix):
    """Independent graph certificate: actual column differences, union/find.

    Does not use a residue formula or assume the special Toeplitz shape.
    Every column must be a nonempty interval of ones.
    """
    rows, columns = len(matrix), len(matrix[0])
    parent = list(range(rows + 1))

    def root(vertex):
        while vertex != parent[vertex]:
            parent[vertex] = parent[parent[vertex]]
            vertex = parent[vertex]
        return vertex

    rank = 0
    for j in range(columns):
        column = [0] + [matrix[i][j] for i in range(rows)] + [0]
        difference = [column[i + 1] - column[i] for i in range(rows + 1)]
        ends = [i for i, x in enumerate(difference) if x]
        if len(ends) != 2 or [difference[i] for i in ends] != [1, -1]:
            raise ValueError("Every column must be one nonempty interval of ones")
        a, b = map(root, ends)
        if a != b:
            parent[a] = b
            rank += 1
    return rank


def nilpotent_tensor_matrix(m, n, degree):
    """Multiplication by h_d in Q[x,y]/(x^m,y^n), in monomial order.

    This constructs the full mn by mn operator without Toeplitz-block formulas.
    Only use it for small independent checks.
    """
    matrix = [[0] * (m * n) for _ in range(m * n)]
    for a, b in product(range(m), range(n)):
        for i in range(degree + 1):
            x, y = a + i, b + degree - i
            if x < m and y < n:
                matrix[x * n + y][a * n + b] += 1
    return matrix


def rank_probe(full=False):
    shape_limit, degree_limit = (9, 13) if full else (5, 7)
    interval_cases = 0
    for rows, columns, degree in product(
        range(1, shape_limit + 1), range(1, shape_limit + 1), range(degree_limit + 1)
    ):
        for offset in range(degree + 1):
            if not 0 <= columns - rows + offset <= degree:
                continue
            matrix = interval_band(rows, columns, degree, offset)
            expected = rational_rank(matrix)
            assert interval_band_rank(rows, columns, degree, offset) == expected
            assert interval_graph_rank(matrix) == expected
            interval_cases += 1

    m_limit, n_limit = (12, 15) if full else (6, 8)
    triples = blocks = deficient = 0
    for m in range(1, m_limit + 1):
        for n in range(m, n_limit + 1):
            for degree in range(1, m + n):
                actual_rank = actual_defect = 0
                for k in range(degree + 1, m + n):
                    matrix = toeplitz_block(m, n, degree, 1, k)
                    rank = rational_rank(matrix)
                    rows, columns, offset = toeplitz_shape(m, n, degree, 1, k)
                    assert rank == interval_band_rank(rows, columns, degree, offset)
                    actual_rank += rank
                    actual_defect += min(rows, columns) - rank
                    blocks += 1
                assert first_power_rank(m, n, degree) == actual_rank, (m, n, degree)
                assert first_power_defect(m, n, degree) == actual_defect, (m, n, degree)
                triples += 1
                deficient += bool(actual_defect)

    dense_limit = 7 if full else 4
    dense_cases = 0
    for m in range(1, dense_limit + 1):
        for n in range(m, dense_limit + 1):
            for degree in range(1, m + n):
                assert first_power_rank(m, n, degree) == rational_rank(
                    nilpotent_tensor_matrix(m, n, degree)
                )
                dense_cases += 1

    # A minimal ell=2 counterexample: weights cannot be replaced by their support.
    weighted = toeplitz_block(3, 3, 1, 2, 4)
    support = [[int(bool(x)) for x in row] for row in weighted]
    assert rational_rank(weighted) == 2 and rational_rank(support) == 1
    return {
        "interval_matrices_three_way_checked": interval_cases,
        "interval_grid": {"max_rows_columns": shape_limit, "degree": [0, degree_limit]},
        "jordan_triples": triples,
        "jordan_grid": {"max_m": m_limit, "max_n": n_limit, "degree": "1..m+n-1"},
        "toeplitz_blocks": blocks,
        "triples_with_rank_loss": deficient,
        "independent_full_tensor_matrices": dense_cases,
        "full_tensor_max_m_n": dense_limit,
        "ell_2_counterexample": {"m": 3, "n": 3, "d": 1, "k": 4, "rank": 2, "support_rank": 1},
        "status": "Proof supplied for ell=1; publication novelty unconfirmed; ell>=2 unresolved here",
    }


def matrix_product(left, right):
    return [
        [
            sum(a * b for a, b in zip(row, column, strict=True))
            for column in zip(*right, strict=True)
        ]
        for row in left
    ]


def block_exponential_reference(body, tangent, time):
    """Ordinary Fraction 4x4 Taylor oracle for [[N,E],[0,N]], checked to order 4."""
    block = [
        [body[0][0], body[0][1], tangent[0][0], tangent[0][1]],
        [body[1][0], body[1][1], tangent[1][0], tangent[1][1]],
        [F(0), F(0), body[0][0], body[0][1]],
        [F(0), F(0), body[1][0], body[1][1]],
    ]
    power = [[F(i == j) for j in range(4)] for i in range(4)]
    result = [row[:] for row in power]
    for k in range(1, 5):
        power = matrix_product(power, block)
        if k == 4:
            assert not any(x for row in power for x in row)
        else:
            factor = F(time) ** k / math.factorial(k)
            result = [
                [a + factor * b for a, b in zip(r, p, strict=True)]
                for r, p in zip(result, power, strict=True)
            ]
    return result


def critical_probe(full=False):
    bodies = ((0, 1, 0, 0), (1, 1, -1, -1), (F(1, 2), F(1, 4), -1, F(-1, 2)), (0, 0, 0, 0))
    variations = tuple(product((-1, 0, 1), repeat=4))
    if not full:
        variations = variations[::8]
    cases = cubic_nonzero = noncommuting = 0
    for entries, variation in product(bodies, variations):
        operator = ModeOperator.from_matrix(
            *(ExactUltra(a, eps=e) for a, e in zip(entries, variation, strict=True))
        )
        _, centered = critical_center(operator)
        assert centered**4 == QNULL
        cubic_nonzero += centered**3 != QNULL
        body = [[x.real for x in row] for row in centered.matrix()]
        tangent = [[x.eps for x in row] for row in centered.matrix()]
        noncommuting += matrix_product(body, tangent) != matrix_product(tangent, body)
        reference = block_exponential_reference(body, tangent, F(3, 5))
        actual = critical_polynomial(centered, F(3, 5)).matrix()
        for i, j in product(range(2), repeat=2):
            assert actual[i][j] == ExactUltra(reference[i][j], eps=reference[i][j + 2])
        for n in (-3, 0, 7):
            assert corrected_critical_cayley(centered, F(2, 7), n) == critical_polynomial(
                centered, F(2 * n, 7)
            )
        assert critical_polynomial(centered, F(1, 3)) @ critical_polynomial(
            centered, F(-4, 5)
        ) == critical_polynomial(centered, F(-7, 15))
        cases += 1
    return {
        "exact_jets": cases,
        "noncommuting_body_variation_pairs": noncommuting,
        "nonzero_cubic_coefficients": cubic_nonzero,
        "independent_reference": "4x4 ordinary Fraction block exponential; fourth power zero",
        "cayley_step": "2/7",
        "cayley_step_counts": [-3, 0, 7],
        "status": "Exact Cayley-Hamilton corollary, not claimed as a new theorem",
    }


def reciprocal_probe():
    rows = []
    for exponent in (2, 4, 6, 8, 10, 20, 40, 80, 100, 140):
        h = 10.0**-exponent
        seed = Ultra(1, i=h, ij=h, eps=1)
        exact_h = F(h)
        exact = ExactUltra(1, i=exact_h, ij=exact_h, eps=1).inverse()
        reference_second = float(-exact.j / exact_h**2)
        reference_third = float(-exact.eps_j / exact_h**2)
        core, direct = seed.inverse(), direct_reciprocal(seed)
        second, third = -direct.j / h**2, -direct.eps_j / h**2
        assert math.isclose(second, reference_second, rel_tol=3e-15)
        assert math.isclose(third, reference_third, rel_tol=3e-15)
        rows.append(
            {
                "h": h,
                "exact_finite_step_second": reference_second,
                "core_second": -core.j / h**2,
                "prototype_second": second,
                "exact_finite_step_third": reference_third,
                "core_third": -core.eps_j / h**2,
                "prototype_third": third,
                "log_control_second": -seed.log().j / h**2,
            }
        )
    return {
        "family": "x=1+i*h+i*j*h+eps; extract -j/h² and -eps_j/h² from 1/x",
        "reference": "ExactUltra inverse at the exact rational values of the input floats",
        "second_derivative_limit": 2,
        "third_derivative_limit": -6,
        "samples": rows,
        "status": "Known identity, demonstrated coefficient-accuracy gain, guarded prototype only",
        "negative_finding": "The same log probe retains its small j component; no log failure claimed",
    }


def report(full=False):
    files = (
        "examples/novelty_models.py",
        "tools/novelty_probe.py",
        "tests/test_novelty_models.py",
        "src/ultracomplexmath/core.py",
        "src/ultracomplexmath/exact.py",
        "src/ultracomplexmath/transformations.py",
    )
    return {
        "package_version": __version__,
        "source_review_date": "2026-10-06",
        "paper_version": "Noferini, arXiv:2512.08399v5; Problem 4.19",
        "full": full,
        "source_sha256": {
            name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in files
        },
        "rank": rank_probe(full),
        "critical_jet": critical_probe(full),
        "reciprocal": reciprocal_probe(),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--full", action="store_true", help="Run the larger documented finite grids"
    )
    parser.add_argument("--output", type=Path, help="Write the reproducible JSON report")
    arguments = parser.parse_args()
    data = report(arguments.full)
    if arguments.output:
        arguments.output.parent.mkdir(parents=True, exist_ok=True)
        arguments.output.write_text(json.dumps(data, indent=2, allow_nan=False) + "\n")
    print(json.dumps({key: data[key] for key in ("full", "rank", "critical_jet")}, indent=2))
    print("Reciprocal: exact finite-step references agree with all 10 prototype samples.")


if __name__ == "__main__":
    main()
