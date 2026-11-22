"""Reproducible replacement for the print-only UltraPerformanceTest experiment."""

import argparse
import json
import platform
import timeit

from ultracomplexmath import Formula, Ultra


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--iterations", type=int, default=1000)
    args = parser.parse_args()
    if args.iterations < 1:
        parser.error("iterations must be positive")
    value = Ultra(2, 0.1, 0.2, 0.1, 0.2, 0.1, 0.1, 0.1)
    formula = Formula("exp(x)+sin(x)")
    operations = {
        "multiply": lambda: value * value,
        "inverse": value.inverse,
        "exp": value.exp,
        "log": value.log,
        "formula": lambda: formula({"x": value}),
    }
    print(
        json.dumps(
            {
                "python": platform.python_version(),
                "iterations": args.iterations,
                "seconds_per_operation": {
                    name: min(timeit.repeat(fn, number=args.iterations, repeat=3)) / args.iterations
                    for name, fn in operations.items()
                },
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
