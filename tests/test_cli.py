import pytest

from cicd_demo.cli import main


def test_cli_adds_numbers(capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = main(["add", "2", "3"])

    assert exit_code == 0
    assert capsys.readouterr().out.strip() == "5.0"


def test_cli_prints_fibonacci(capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = main(["fib", "7"])

    assert exit_code == 0
    assert capsys.readouterr().out.strip() == "13"
