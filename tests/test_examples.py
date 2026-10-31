from pathlib import Path

import pytest

from polyglot_python import load_locales, resolve_locale
from polyglot_python.cli import main
from polyglot_python.translator import translate

EXPECTED_SUFFIXES = {
    ".tr",
    ".es",
    ".pt",
    ".de",
    ".fr",
    ".zh",
    ".hi",
    ".ar",
    ".ru",
    ".it",
    ".nl",
    ".pl",
    ".id",
    ".vi",
    ".ja",
    ".ko",
    ".uk",
    ".ro",
    ".sv",
    ".el",
}

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = sorted(ROOT.joinpath("examples").glob("classify.*"))
TOURS = sorted(ROOT.joinpath("examples").glob("tour.*"))
TOUR_REFERENCE = ROOT.joinpath("tests", "data", "tour.py")

TOUR_OUTPUT = [
    "fib [0, 1, 1, 2, 3, 5, 8, 13, 21]",
    "even sum 10",
    "squares [0, 2, 2, 4]",
    "zero count 1",
    "div 3.0",
    "root 9",
    "positive 5",
    "report other",
    "registry True",
    "calls 2",
    "clean True",
]


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
    assert {path.suffix for path in EXAMPLES} == EXPECTED_SUFFIXES


def test_tour_examples_are_present():
    assert {path.suffix for path in TOURS} == EXPECTED_SUFFIXES


@pytest.mark.parametrize("path", EXAMPLES, ids=lambda path: path.suffix[1:])
def test_example_checks_and_runs(path, capsys):
    assert main(["check", str(path)]) == 0
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""

    assert main(["run", str(path)]) == 0
    assert capsys.readouterr().out.splitlines() == _expected_lines()


@pytest.mark.parametrize("path", TOURS, ids=lambda path: path.suffix[1:])
def test_tour_example_checks_and_runs(path, capsys):
    assert main(["check", str(path)]) == 0
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""

    assert main(["run", str(path)]) == 0
    assert capsys.readouterr().out.splitlines() == TOUR_OUTPUT


@pytest.mark.parametrize("path", TOURS, ids=lambda path: path.suffix[1:])
def test_tour_example_translates_to_reference(path):
    source = path.read_text(encoding="utf-8")
    code = resolve_locale(None, source, str(path))
    assert code is not None
    translation = translate(source, load_locales()[code])
    assert translation.python == TOUR_REFERENCE.read_text(encoding="utf-8")
