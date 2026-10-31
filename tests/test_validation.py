import keyword

import pytest

from anadil.translator import (
    LocaleError,
    _parse_locales,
    _validate_keywords,
    _validate_messages,
)


def _valid_keywords():
    return {word: word for word in keyword.kwlist}


def test_identity_keyword_table_is_valid():
    result = _validate_keywords("xx", _valid_keywords())
    assert result["if"] == "if"


def test_keywords_must_be_object():
    with pytest.raises(LocaleError):
        _validate_keywords("xx", [])


def test_keyword_keys_must_match_exactly():
    table = _valid_keywords()
    table.pop("if")
    with pytest.raises(LocaleError):
        _validate_keywords("xx", table)


def test_localized_keyword_must_be_identifier():
    table = _valid_keywords()
    table["if"] = "1x"
    with pytest.raises(LocaleError):
        _validate_keywords("xx", table)


def test_localized_keyword_must_not_collide_with_other_python_keyword():
    table = _valid_keywords()
    table["if"] = "else"
    with pytest.raises(LocaleError):
        _validate_keywords("xx", table)


def test_identical_python_keyword_mapping_is_allowed():
    result = _validate_keywords("xx", _valid_keywords())
    assert result["else"] == "else"


def test_duplicate_localized_keywords_rejected():
    table = _valid_keywords()
    table["else"] = "aynı"
    table["if"] = "aynı"
    with pytest.raises(LocaleError):
        _validate_keywords("xx", table)


def test_messages_must_be_complete():
    with pytest.raises(LocaleError):
        _validate_messages("xx", {"syntax_error": "x"})


def test_messages_must_be_object():
    with pytest.raises(LocaleError):
        _validate_messages("xx", None)


def test_messages_accepted():
    messages = {
        "syntax_error": "a",
        "runtime_error": "b",
        "token_error": "c",
    }
    assert _validate_messages("xx", messages)["runtime_error"] == "b"


def test_locale_document_needs_locales_object():
    with pytest.raises(LocaleError):
        _parse_locales('{"locales": []}')


def test_locale_entry_must_be_object():
    with pytest.raises(LocaleError):
        _parse_locales('{"locales": {"tr": []}}')


def test_locale_entry_needs_name():
    with pytest.raises(LocaleError):
        _parse_locales('{"locales": {"tr": {"keywords": {}, "messages": {}}}}')
