"""polyglot-python: deterministic multilingual Python keyword transpiler."""

from .translator import (
    Locale,
    LocaleError,
    TokenizeFailure,
    Translation,
    has_locale_suffix,
    load_locales,
    resolve_locale,
    translate,
)

__version__ = "0.2.1"

__all__ = [
    "Locale",
    "LocaleError",
    "TokenizeFailure",
    "Translation",
    "__version__",
    "has_locale_suffix",
    "load_locales",
    "resolve_locale",
    "translate",
]
