"""Command-line calculator: python -m ultracomplexmath 'exp(pi*i)' --json."""

from __future__ import annotations

import argparse
import json
import math

from .core import Ultra
from .formula import evaluate
from .polar import UltraRoots


def _print_roots(roots: UltraRoots, as_json: bool) -> None:
    count = roots.count
    strata = roots.strata
    free = [
        name
        for name, kind in zip(("+", "-"), strata, strict=True)
        if kind == "zero" and count == math.inf
    ]
    if as_json:
        metadata = {
            "degree": roots.degree,
            "count": "infinite" if free else count,
            "strata": strata,
            "sheet_counts": roots.sheet_counts,
            "free_tangents": free,
        }
        # Stream the finite list of representatives even for parametrized families.
        print(json.dumps(metadata)[:-1] + ', "representatives": [', end="")
        for i, root in enumerate(roots.representatives()):
            print((", " if i else "") + json.dumps(root.coefficients, allow_nan=False), end="")
        print("]}")
    else:
        print("Roots:", "infinitely many" if free else count)
        if free:
            print("Free complex tangents in channel(s)", ", ".join(free), "(set to zero below)")
        for root in roots.representatives():
            print(root)


def _print_polar(value: Ultra, as_json: bool) -> None:
    polar = value.polar()
    data = {
        "r": polar.r,
        "rho": polar.rho,
        "theta": polar.theta,
        "phi": polar.phi,
        "v": polar.v.coefficients[:4],
        "phases": polar.phases,
    }
    if as_json:
        print(json.dumps(data, allow_nan=False))
    else:
        for key, item in data.items():
            print(f"{key} = {item}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Eight-dimensional ultracomplex calculator")
    parser.add_argument(
        "expression", help="Formula with explicit multiplication; quote in your shell"
    )
    parser.add_argument("--json", action="store_true", help="Print the selected result as JSON")
    view = parser.add_mutually_exclusive_group()
    view.add_argument(
        "--polar",
        action="store_true",
        help="Show unit polar coordinates and both phases in radians",
    )
    view.add_argument(
        "--roots",
        type=int,
        metavar="N",
        help="Describe all numerical Nth roots and print one representative per sheet",
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--exact",
        action="store_true",
        help="Use exact integer/rational coefficients and decimal literals",
    )
    mode.add_argument(
        "--legacy",
        action="store_true",
        help="Accept implicit multiplication and original word operators",
    )
    args = parser.parse_args()
    if args.exact and (args.polar or args.roots is not None):
        parser.error(
            "--polar and --roots use numerical coordinates and cannot be combined with --exact"
        )
    try:
        if args.exact:
            from .exact_formula import evaluate_exact

            exact = evaluate_exact(args.expression)
            print(exact.to_json() if args.json else str(exact))
            return
        if args.legacy:
            from .expressions import Calculation

            result = Calculation(args.expression).result()
        else:
            result = evaluate(args.expression)
        if args.polar:
            _print_polar(result, args.json)
        elif args.roots is not None:
            _print_roots(result.roots(args.roots), args.json)
        else:
            print(json.dumps(result.coefficients, allow_nan=False) if args.json else str(result))
    except (ArithmeticError, ValueError, TypeError) as error:
        parser.exit(2, f"error: {error}\n")


if __name__ == "__main__":
    main()
