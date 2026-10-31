import io
from contextlib import redirect_stdout

import pytest

from polyglot_python import TokenizeFailure, load_locales, translate

LOCALES = load_locales()
TR = LOCALES["tr"]


def test_keywords_translated_lines_preserved():
    source = "eğer Doğru:\n    geç\ndeğilse:\n    yükselt Hata()\n"
    result = translate(source, TR)
    assert result.python == "if True:\n    pass\nelse:\n    raise Hata()\n"
    assert len(result.python.split("\n")) == len(source.split("\n"))


def test_operators_and_constants():
    source = "eğer değil (a == 1 ve b == 2):\n    geç\n"
    assert translate(source, TR).python == (
        "if not (a == 1 and b == 2):\n    pass\n"
    )


def test_strings_comments_fstrings_untouched():
    source = 'print("eğer")  # değilse\nprint(f"iken {1}")\n'
    assert translate(source, TR).python == source


def test_identifier_substrings_untouched():
    source = "eğerlik = 1\ndeğilseki = 2\n"
    assert translate(source, TR).python == source


def test_attribute_names_untouched():
    source = "nesne.eğer = 1\n"
    assert translate(source, TR).python == source


def test_crlf_normalized():
    source = "eğer Doğru:\r\n    geç\r\n"
    assert translate(source, TR).python == "if True:\n    pass\n"


def test_no_locale_is_identity():
    source = "print(1)\r\nif True:\r\n    pass\r\n"
    result = translate(source, None)
    assert result.python == "print(1)\nif True:\n    pass\n"
    assert result.column_maps == ((), (), (), ())
    assert result.original_column(2, 5) == 5


def test_original_column_maps_across_replacement():
    source = "eğer Doğru:\n    geç\n"
    result = translate(source, TR)
    assert result.python == "if True:\n    pass\n"
    assert result.original_column(1, 4) == 6
    assert result.original_column(1, 2) == 1
    assert result.original_column(2, 5) == 5
    assert result.original_column(99, 5) == 5
    assert result.original_column(0, 7) == 7


def test_column_maps_align_with_output_lines():
    source = "eğer a ve b:\n    döndür a\n"
    result = translate(source, TR)
    assert result.python.split("\n")[0] == "if a and b:"
    for line, column_map in zip(result.python.split("\n"), result.column_maps):
        assert not column_map or len(column_map) == len(line)


def test_unterminated_string_fails_closed():
    with pytest.raises(TokenizeFailure) as caught:
        translate('metin = """açık\n', TR)
    assert caught.value.line >= 1
    assert caught.value.column >= 1
    assert caught.value.detail


def test_indentation_error_fails_closed():
    with pytest.raises(TokenizeFailure) as caught:
        translate("eğer Doğru:\n    geç\n  geç\n", TR)
    assert caught.value.line == 3
    assert caught.value.column >= 1


@pytest.mark.parametrize("code", sorted(LOCALES))
def test_every_locale_executes(code):
    locale = LOCALES[code]
    words = locale.keywords
    source = (
        f"{words['def']} hedef(deger):\n"
        f"    {words['if']} deger > 0:\n"
        f"        {words['return']} \"artı\"\n"
        f"    {words['else']}:\n"
        f"        {words['return']} \"eksi\"\n"
        "\nprint(hedef(5))\n"
    )
    first = translate(source, locale)
    assert translate(source, locale).python == first.python
    output = io.StringIO()
    with redirect_stdout(output):
        exec(compile(first.python, "<memory>", "exec"), {})
    assert output.getvalue().strip() == "artı"
