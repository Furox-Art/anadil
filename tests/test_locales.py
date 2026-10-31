import keyword

import pytest

from polyglot_python import load_locales, resolve_locale

EXPECTED_CODES = {
    "tr",
    "es",
    "pt",
    "de",
    "fr",
    "zh",
    "hi",
    "ar",
    "ru",
    "it",
    "nl",
    "pl",
    "id",
    "vi",
    "ja",
}


def test_all_locales_present_and_complete():
    locales = load_locales()
    assert set(locales) == EXPECTED_CODES
    for code, locale in locales.items():
        assert locale.code == code
        assert locale.name
        assert set(locale.keywords) == set(keyword.kwlist)
        assert len(locale.keywords) == 35
        values = list(locale.keywords.values())
        assert len(set(values)) == len(values)
        assert all(value.isidentifier() for value in values)
        assert set(locale.messages) == {
            "syntax_error",
            "runtime_error",
            "token_error",
        }


def test_reverse_keywords_roundtrip():
    for locale in load_locales().values():
        reverse = locale.reverse_keywords
        assert len(reverse) == len(locale.keywords)
        for python_word, local_word in locale.keywords.items():
            assert reverse[local_word] == python_word


@pytest.mark.parametrize(
    ("code", "python_word", "local_word"),
    [
        ("tr", "if", "eğer"),
        ("es", "def", "función"),
        ("pt", "else", "senão"),
        ("de", "while", "solange"),
        ("fr", "return", "retourner"),
        ("zh", "class", "类"),
        ("hi", "return", "लौटाओ"),
        ("ar", "import", "استورد"),
        ("ru", "if", "если"),
        ("it", "if", "se"),
        ("nl", "if", "indien"),
        ("pl", "while", "dopóki"),
        ("id", "return", "kembalikan"),
        ("vi", "import", "nhập"),
        ("ja", "class", "クラス"),
    ],
)
def test_known_mappings(code, python_word, local_word):
    assert load_locales()[code].keywords[python_word] == local_word


def test_resolve_explicit_wins():
    assert resolve_locale("ES", "# polyglot-python: tr\n", "x.fr") == "es"


def test_resolve_directive():
    assert resolve_locale(None, "# polyglot-python: zh\nprint(1)\n") == "zh"


def test_resolve_suffix():
    assert resolve_locale(None, "print(1)\n", "program.DE") == "de"


@pytest.mark.parametrize("code", sorted(EXPECTED_CODES))
def test_every_locale_resolves_by_suffix(code):
    assert resolve_locale(None, "print(1)\n", f"program.{code}") == code


def test_resolve_none():
    assert resolve_locale(None, "print(1)\n", "program.py") is None
    assert resolve_locale(None, "print(1)\n") is None


def test_resolve_directive_must_be_first_line():
    assert resolve_locale(None, "x = 1\n# polyglot-python: tr\n") is None
