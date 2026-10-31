# anadil

Write Python in your own language, deterministically.

anadil is a keyword transpiler for Python. You keep Python's grammar and write
programs with localized keywords; anadil maps those keywords to the real Python
keywords and hands the result to CPython. No AI, no network, no randomness:
the same source, locale and version always produce byte-identical Python.

It is not a prose-to-code translator and it does not guess intent. It is Python
syntax with your words.

## Install

```bash
pip install -e .
```

Requires Python 3.12+. Python 3.10/3.11 are not supported because their
tokenizer splits Indic combining marks, so several Hindi keywords would not
translate. No runtime dependencies.

## Quick start

`examples/classify.tr`:

```python
fonksiyon classify(n):
    eğer n % 15 == 0:
        döndür "FizzBuzz"
    değilse_eğer n % 3 == 0:
        döndür "Fizz"
    değilse_eğer n % 5 == 0:
        döndür "Buzz"
    değilse:
        döndür str(n)

için n içinde range(1, 16):
    print(classify(n))
```

```bash
anadil run examples/classify.tr
anadil translate examples/classify.tr
anadil translate examples/classify.tr -o classify.py
```

The same FizzBuzz program is included for every locale under `examples/`.

## Locales

| Code | Language   | `if`     | `def`       | `return`  |
|------|------------|----------|-------------|-----------|
| tr   | Türkçe     | `eğer`   | `fonksiyon` | `döndür`  |
| es   | Español    | `si`     | `función`   | `devolver`|
| pt   | Português  | `se`     | `função`    | `retornar`|
| de   | Deutsch    | `wenn`   | `funktion`  | `zurückgeben` |
| fr   | Français   | `si`     | `fonction`  | `retourner` |
| zh   | 中文        | `如果`   | `函数`      | `返回`    |
| hi   | हिन्दी      | `अगर`    | `फलन`       | `लौटाओ`   |
| ar   | العربية    | `إذا`    | `دالة`      | `إرجاع`   |

`anadil locales` prints the full list. Every locale defines exactly the 35
Python hard keywords (`keyword.kwlist`); soft keywords such as `match`, `case`
and `type` stay English.

Locale selection order:

1. `--lang CODE`
2. first line directive: `# anadil: tr`
3. file suffix: `.tr`, `.es`, `.pt`, `.de`, `.fr`, `.zh`, `.hi`, `.ar`

## CLI

```text
anadil run FILE [--lang CODE] [args...]
anadil translate FILE [--lang CODE] [-o OUT]
anadil locales
anadil --version
```

For `run`, place options before `FILE`; everything after `FILE` is passed to the
program as `sys.argv[1:]`.

## Guarantees

- Only exact `NAME` tokens that match a locale keyword are rewritten. Strings,
  comments, f-strings, numbers, identifiers and attribute names are untouched.
- Line numbers are preserved one-to-one; a per-line column map translates
  reported error positions back to the localized source.
- `translate -o` and stdout output are UTF-8 with LF line endings on every
  platform, so exports are byte-identical and re-verifiable.
- A localized keyword after a dot is treated as an attribute name and never
  rewritten.
- Localized keywords are reserved words in their locale.
- Missing files, invalid UTF-8, unknown locales and untokenizable input fail
  with a clear message; nothing is guessed or silently skipped.
- Error headers are localized; CPython's detail text (for example
  `ZeroDivisionError`) remains English for now.
- Exit codes from the executed program are propagated.

## Limits

- Phase 1 localizes keywords only: no localization of builtins (`print`,
  `range`, ...), the standard library, or English exception text.
- This is not a natural-language compiler. It does not understand Spanish or
  Turkish prose; it understands Python syntax written with localized keywords.
- The local prototype ships 8 locales. Other languages can be added by editing
  `src/anadil/locales.json`; malformed tables are rejected at load time.
- Tested on CPython 3.12 on Windows; the code targets 3.12+.

## Development

```bash
python -m venv .venv
.venv/Scripts/pip install -e ".[dev]"
.venv/Scripts/python -m pytest -q --cov=anadil --cov-fail-under=100
```

The suite contains 75 tests with 100% statement coverage, including an
end-to-end execution of the same program in all 8 locales and byte-level
determinism checks. CI runs Ubuntu 3.12-3.13 plus Windows and macOS at 3.12,
enforces the 100% coverage gate on Linux 3.12, and translates every example
twice on all three operating systems to compare bytes and line counts.

## License

MIT
