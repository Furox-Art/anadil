from pathlib import Path

import pytest

from polyglot_python.cli import main

EXAMPLES = sorted(
    Path(__file__).resolve().parents[1].joinpath("examples").glob("classify.*")
)


def _expected_lines():
    lines = []
    for number in range(1, 16):
        if number % 15 == 0:
            lines.append("FizzBuzz")
        elif number % 3 == 0:
            lines.append("Fizz")
        elif number % 5 == 0:
            lines.append("Buzz")
        else:
            lines.append(str(number))
    return lines


def test_examples_are_present():
    assert {path.suffix for path in EXAMPLES} == {
        ".tr",
        ".es",
        ".pt",
        ".de",
        ".fr",
        ".zh",
        ".hi",
        ".ar",
        ".ru",
    }


@pytest.mark.parametrize("path", EXAMPLES, ids=lambda path: path.suffix[1:])
def test_example_checks_and_runs(path, capsys):
    assert main(["check", str(path)]) == 0
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""

    assert main(["run", str(path)]) == 0
    assert capsys.readouterr().out.splitlines() == _expected_lines()
