"""anadil: deterministic multilingual Python keyword transpiler."""

from .translator import (
    Locale,
    LocaleError,
    TokenizeFailure,
    Translation,
    load_locales,
    resolve_locale,
    translate,
)

__version__ = "0.1.0"

__all__ = [
    "Locale",
    "LocaleError",
    "TokenizeFailure",
    "Translation",
    "__version__",
    "load_locales",
    "resolve_locale",
    "translate",
]
