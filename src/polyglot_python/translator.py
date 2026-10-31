"""Deterministic translation of localized Python keywords.

Only exact ``NAME`` tokens that match a locale keyword are rewritten; strings,
comments, f-strings, numbers and attribute names are never touched. Line
numbers are preserved exactly, and a per-line column map lets callers report
positions against the original localized source.
"""

from __future__ import annotations

import io
import json
import keyword
import re
import tokenize
from dataclasses import dataclass
from functools import lru_cache
from importlib import resources
from pathlib import Path
from types import MappingProxyType
from typing import Mapping

_SUFFIX_LOCALES = {
    ".tr": "tr",
    ".es": "es",
    ".pt": "pt",
    ".de": "de",
    ".fr": "fr",
    ".zh": "zh",
    ".hi": "hi",
    ".ar": "ar",
    ".ru": "ru",
    ".it": "it",
    ".nl": "nl",
    ".pl": "pl",
    ".id": "id",
    ".vi": "vi",
    ".ja": "ja",
}

_DIRECTIVE = re.compile(r"^#\s*polyglot-python:\s*([A-Za-z][A-Za-z0-9_-]*)\s*$")

_MESSAGE_KEYS = (
    "syntax_error",
    "runtime_error",
    "token_error",
)

_SIGNIFICANT = (tokenize.NAME, tokenize.OP, tokenize.NUMBER, tokenize.STRING)


class PolyglotError(Exception):
    """Base class for all polyglot-python errors."""


class LocaleError(PolyglotError):
    """Raised when locale data is malformed or a locale is unknown."""


class TokenizeFailure(PolyglotError):
    """Raised when the localized source cannot be tokenized."""

    def __init__(self, line: int, column: int, detail: str) -> None:
        super().__init__(detail)
        self.line = line
        self.column = column
        self.detail = detail


@dataclass(frozen=True)
class Locale:
    """A validated locale: Python keyword -> localized keyword."""

    code: str
    name: str
    keywords: Mapping[str, str]
    messages: Mapping[str, str]

    @property
    def reverse_keywords(self) -> dict[str, str]:
        return {local: python for python, local in self.keywords.items()}


@dataclass(frozen=True)
class Translation:
    """A translated program plus its original-source column maps."""

    original: str
    python: str
    column_maps: tuple[tuple[int, ...], ...]

    def original_column(self, lineno: int, offset: int) -> int:
        """Map a 1-based translated column back to a 1-based original column.

        An empty map means the line was not touched, so the column is already
        correct. Out-of-range positions are clamped to the line bounds.
        """
        if not self.column_maps or lineno < 1:
            return offset
        index = min(lineno, len(self.column_maps)) - 1
        column_map = self.column_maps[index]
        if not column_map:
            return offset
        position = min(max(offset, 1), len(column_map)) - 1
        return column_map[position] + 1


def _tokenizes_as_name(word: str) -> bool:
    try:
        tokens = list(tokenize.generate_tokens(io.StringIO(word).readline))
    except (tokenize.TokenError, IndentationError):
        return False
    significant = [
        token
        for token in tokens
        if token.type not in (tokenize.ENDMARKER, tokenize.NEWLINE, tokenize.NL)
    ]
    return (
        len(significant) == 1
        and significant[0].type == tokenize.NAME
        and significant[0].string == word
    )


def _validate_keywords(code: str, raw: object) -> Mapping[str, str]:
    if not isinstance(raw, dict):
        raise LocaleError(f"{code}: keywords must be a JSON object")
    expected = set(keyword.kwlist)
    actual = set(raw)
    if actual != expected:
        missing = sorted(expected - actual)
        extra = sorted(actual - expected)
        raise LocaleError(
            f"{code}: keywords must match Python keywords exactly "
            f"(missing={missing}, extra={extra})"
        )
    seen: dict[str, str] = {}
    for python_word in keyword.kwlist:
        local = raw[python_word]
        if not isinstance(local, str) or not local.isidentifier():
            raise LocaleError(
                f"{code}: {python_word!r} maps to an invalid identifier: {local!r}"
            )
        if keyword.iskeyword(local) and local != python_word:
            raise LocaleError(
                f"{code}: {python_word!r} maps to reserved Python keyword {local!r}"
            )
        if local in seen:
            raise LocaleError(
                f"{code}: duplicate localized keyword {local!r} "
                f"for {seen[local]!r} and {python_word!r}"
            )
        if not _tokenizes_as_name(local):
            raise LocaleError(
                f"{code}: {python_word!r} maps to {local!r}, which this "
                "interpreter does not tokenize as one identifier "
                "(Python 3.12+ is required for Indic scripts)"
            )
        seen[local] = python_word
    return MappingProxyType(dict(raw))


def _validate_messages(code: str, raw: object) -> Mapping[str, str]:
    if not isinstance(raw, dict):
        raise LocaleError(f"{code}: messages must be a JSON object")
    messages: dict[str, str] = {}
    for key in _MESSAGE_KEYS:
        value = raw.get(key)
        if not isinstance(value, str) or not value:
            raise LocaleError(f"{code}: missing message {key!r}")
        messages[key] = value
    return MappingProxyType(messages)


@lru_cache(maxsize=1)
def load_locales() -> Mapping[str, Locale]:
    """Load and validate every bundled locale."""
    raw_text = resources.files("polyglot_python").joinpath("locales.json").read_text(
        encoding="utf-8"
    )
    return _parse_locales(raw_text)


def _parse_locales(raw_text: str) -> Mapping[str, Locale]:
    data = json.loads(raw_text)
    if not isinstance(data, dict) or not isinstance(data.get("locales"), dict):
        raise LocaleError("locales.json: expected an object with a 'locales' object")
    locales: dict[str, Locale] = {}
    for code, entry in data["locales"].items():
        if not isinstance(entry, dict):
            raise LocaleError(f"{code}: locale entry must be a JSON object")
        name = entry.get("name")
        if not isinstance(name, str) or not name:
            raise LocaleError(f"{code}: missing locale name")
        locales[code] = Locale(
            code=code,
            name=name,
            keywords=_validate_keywords(code, entry.get("keywords")),
            messages=_validate_messages(code, entry.get("messages")),
        )
    return MappingProxyType(locales)


def resolve_locale(
    explicit: str | None, text: str, filename: str | None = None
) -> str | None:
    """Resolve a locale code: --lang, then ``# polyglot-python: xx``, then suffix."""
    if explicit:
        return explicit.strip().lower()
    first_line = text.split("\n", 1)[0].strip()
    match = _DIRECTIVE.match(first_line)
    if match:
        return match.group(1).lower()
    if filename:
        suffix = Path(filename).suffix.lower()
        if suffix in _SUFFIX_LOCALES:
            return _SUFFIX_LOCALES[suffix]
    return None


def translate(text: str, locale: Locale | None) -> Translation:
    """Translate localized keywords to Python keywords, deterministically."""
    original = text
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    if locale is None:
        return Translation(
            original=original,
            python=normalized,
            column_maps=tuple(() for _ in normalized.split("\n")),
        )

    reverse = locale.reverse_keywords
    try:
        tokens = list(tokenize.generate_tokens(io.StringIO(normalized).readline))
    except tokenize.TokenError as exc:
        detail = str(exc.args[0]) if exc.args else "tokenization failed"
        position = exc.args[1] if len(exc.args) > 1 else (1, 0)
        raise TokenizeFailure(
            int(position[0]), int(position[1]) + 1, detail
        ) from exc
    except IndentationError as exc:
        raise TokenizeFailure(exc.lineno or 1, exc.offset or 1, str(exc)) from exc

    replacements: dict[int, list[tuple[int, int, str]]] = {}
    previous: tokenize.TokenInfo | None = None
    for token in tokens:
        after_dot = (
            previous is not None
            and previous.type == tokenize.OP
            and previous.string == "."
        )
        if (
            token.type == tokenize.NAME
            and not after_dot
            and token.string in reverse
        ):
            row, column = token.start
            replacements.setdefault(row, []).append(
                (column, token.end[1], reverse[token.string])
            )
        if token.type in _SIGNIFICANT:
            previous = token

    out_lines: list[str] = []
    column_maps: list[tuple[int, ...]] = []
    for lineno, line in enumerate(normalized.split("\n"), 1):
        edits = sorted(replacements.get(lineno, ()))
        if not edits:
            out_lines.append(line)
            column_maps.append(())
            continue
        parts: list[str] = []
        column_map: list[int] = []
        position = 0
        for start, end, replacement in edits:
            parts.append(line[position:start])
            column_map.extend(range(position, start))
            parts.append(replacement)
            column_map.extend([start] * len(replacement))
            position = end
        parts.append(line[position:])
        column_map.extend(range(position, len(line)))
        out_lines.append("".join(parts))
        column_maps.append(tuple(column_map))

    return Translation(
        original=original,
        python="\n".join(out_lines),
        column_maps=tuple(column_maps),
    )
