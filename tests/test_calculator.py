import pytest

from cicd_demo.calculator import add, divide, fibonacci


def test_adds_two_numbers() -> None:
    assert add(2, 3) == 5


def test_divides_two_numbers() -> None:
    assert divide(10, 2) == 5


def test_divide_rejects_zero_divisor() -> None:
    with pytest.raises(ValueError, match="divisor must not be zero"):
        divide(10, 0)


@pytest.mark.parametrize(
    ("position", "expected"),
    [
        (0, 0),
        (1, 1),
        (2, 1),
        (7, 13),
    ],
)
def test_fibonacci(position: int, expected: int) -> None:
    assert fibonacci(position) == expected


def test_fibonacci_rejects_negative_position() -> None:
    with pytest.raises(ValueError, match="position must be zero or positive"):
        fibonacci(-1)
