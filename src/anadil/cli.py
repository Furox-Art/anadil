"""Command line interface for anadil."""

from __future__ import annotations

import argparse
import os
import sys
import traceback
from typing import Sequence

from . import __version__
from .translator import (
    Locale,
    TokenizeFailure,
    Translation,
    load_locales,
    resolve_locale,
    translate,
)


class _Failure(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


def _configure_console() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is None:
            continue
        try:
            reconfigure(encoding="utf-8", newline="\n")
        except (ValueError, OSError):
            pass


def _message(locale: Locale | None, key: str, fallback: str) -> str:
    if locale is None:
        return fallback
    return locale.messages.get(key, fallback)


def _read_source(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8-sig", newline="") as handle:
            return handle.read()
    except UnicodeDecodeError as exc:
        raise _Failure(
            f"cannot decode {path} as UTF-8: {exc.reason} at byte {exc.start}"
        ) from exc
    except OSError as exc:
        reason = exc.strerror or str(exc)
        raise _Failure(f"cannot read {path}: {reason}") from exc


def _prepare(path: str, lang: str | None) -> tuple[Locale | None, Translation]:
    text = _read_source(path)
    code = resolve_locale(lang, text, path)
    locale: Locale | None = None
    if code is not None:
        locales = load_locales()
        locale = locales.get(code)
        if locale is None:
            available = ", ".join(sorted(locales))
            raise _Failure(f"unknown locale {code!r}; available: {available}")
    try:
        translation = translate(text, locale)
    except TokenizeFailure as exc:
        prefix = _message(locale, "token_error", "Tokenization error")
        raise _Failure(
            f"{prefix}: {path}:{exc.line}:{exc.column}: {exc.detail}"
        ) from exc
    return locale, translation


def _run(namespace: argparse.Namespace) -> int:
    try:
        locale, translation = _prepare(namespace.file, namespace.lang)
    except _Failure as exc:
        print(f"anadil: {exc.message}", file=sys.stderr)
        return 1

    try:
        code = compile(translation.python, namespace.file, "exec")
    except SyntaxError as exc:
        lineno = exc.lineno or 1
        column = translation.original_column(lineno, exc.offset or 1)
        prefix = _message(locale, "syntax_error", "Syntax error")
        print(
            f"{prefix}: {namespace.file}:{lineno}:{column}: {exc.msg}",
            file=sys.stderr,
        )
        return 1

    scope = {
        "__name__": "__main__",
        "__file__": os.path.abspath(namespace.file),
    }
    saved_argv = sys.argv
    sys.argv = [namespace.file, *namespace.args]
    try:
        exec(code, scope)
    except SystemExit as exc:
        if exc.code is None:
            return 0
        if isinstance(exc.code, int):
            return exc.code
        print(exc.code, file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        raise
    except Exception:
        prefix = _message(locale, "runtime_error", "Runtime error")
        print(f"{prefix}: {namespace.file}", file=sys.stderr)
        traceback.print_exc()
        return 1
    finally:
        sys.argv = saved_argv
    return 0


def _translate(namespace: argparse.Namespace) -> int:
    try:
        _, translation = _prepare(namespace.file, namespace.lang)
    except _Failure as exc:
        print(f"anadil: {exc.message}", file=sys.stderr)
        return 1

    if namespace.output:
        try:
            with open(namespace.output, "w", encoding="utf-8", newline="") as handle:
                handle.write(translation.python)
        except OSError as exc:
            reason = exc.strerror or str(exc)
            print(
                f"anadil: cannot write {namespace.output}: {reason}",
                file=sys.stderr,
            )
            return 1
    else:
        sys.stdout.write(translation.python)
    return 0


def _locales(_namespace: argparse.Namespace) -> int:
    locales = load_locales()
    print(f"{'code':<6}{'name':<16}keywords")
    for code in sorted(locales):
        locale = locales[code]
        print(f"{code:<6}{locale.name:<16}{len(locale.keywords)}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="anadil",
        description="Write Python in your own language: deterministic keyword translation.",
    )
    parser.add_argument(
        "--version", action="version", version=f"anadil {__version__}"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    run = subparsers.add_parser("run", help="translate and execute a program")
    run.add_argument("file", help="localized source file")
    run.add_argument("--lang", metavar="CODE", help="locale code, e.g. tr")
    run.add_argument(
        "args",
        nargs=argparse.REMAINDER,
        help="arguments passed to the program",
    )
    run.set_defaults(handler=_run)

    transform = subparsers.add_parser(
        "translate", help="print the Python translation"
    )
    transform.add_argument("file", help="localized source file")
    transform.add_argument("--lang", metavar="CODE", help="locale code, e.g. tr")
    transform.add_argument(
        "-o", "--output", metavar="PATH", help="write the translation to PATH"
    )
    transform.set_defaults(handler=_translate)

    listing = subparsers.add_parser("locales", help="list bundled locales")
    listing.set_defaults(handler=_locales)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    _configure_console()
    parser = build_parser()
    namespace = parser.parse_args(argv)
    return namespace.handler(namespace)


if __name__ == "__main__":
    sys.exit(main())
