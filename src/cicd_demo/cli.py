"""Command line entry point for the CI/CD demo."""

from __future__ import annotations

import argparse

from cicd_demo.calculator import add, divide, fibonacci


def build_parser() -> argparse.ArgumentParser:
    """Build the command line parser."""
    parser = argparse.ArgumentParser(
        prog="cicd-demo",
        description="Run small calculator commands for the CI/CD demo.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    add_parser = subparsers.add_parser("add", help="Add two numbers")
    add_parser.add_argument("left", type=float)
    add_parser.add_argument("right", type=float)

    divide_parser = subparsers.add_parser("divide", help="Divide two numbers")
    divide_parser.add_argument("dividend", type=float)
    divide_parser.add_argument("divisor", type=float)

    fibonacci_parser = subparsers.add_parser(
        "fib",
        help="Print the Fibonacci number at a zero-based position",
    )
    fibonacci_parser.add_argument("position", type=int)

    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the CLI and return a process exit code."""
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "add":
        print(add(args.left, args.right))
        return 0

    if args.command == "divide":
        print(divide(args.dividend, args.divisor))
        return 0

    if args.command == "fib":
        print(fibonacci(args.position))
        return 0

    parser.error(f"unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
