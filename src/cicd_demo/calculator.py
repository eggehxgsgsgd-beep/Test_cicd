"""Small functions used by the CI demo and tests."""


def add(left: float, right: float) -> float:
    """Return the sum of two numbers."""
    return left + right


def divide(dividend: float, divisor: float) -> float:
    """Return dividend divided by divisor.

    The explicit ValueError makes the behavior easy to test in CI.
    """
    if divisor == 0:
        raise ValueError("divisor must not be zero")

    return dividend / divisor


def fibonacci(position: int) -> int:
    """Return the Fibonacci number at a zero-based position."""
    if position < 0:
        raise ValueError("position must be zero or positive")

    current, next_value = 0, 1
    for _ in range(position):
        current, next_value = next_value, current + next_value

    return current
