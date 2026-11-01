"""Command line interface for polyglot-python."""

from __future__ import annotations

import argparse
import builtins
import keyword
import os
import sys
import traceback
import types
from importlib.machinery import SourceFileLoader
from types import CodeType
from typing import Mapping, Sequence

from . import __version__
from .translator import (
    Locale,
    TokenizeFailure,
    Translation,
    has_locale_suffix,
    load_locales,
    resolve_locale,
    translate,
)


class _Failure(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


_MISSING = object()


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


def _find_locale(locales: Mapping[str, Locale], code: str) -> Locale:
    locale = locales.get(code)
    if locale is None:
        available = ", ".join(sorted(locales))
        raise _Failure(f"unknown locale {code!r}; available: {available}")
    return locale


def _prepare(path: str, lang: str | None) -> tuple[Locale | None, Translation]:
    text = _read_source(path)
    code = resolve_locale(lang, text, path)
    locale: Locale | None = None
    if code is not None:
        locale = _find_locale(load_locales(), code)
    try:
        translation = translate(text, locale)
    except TokenizeFailure as exc:
        prefix = _message(locale, "token_error", "Tokenization error")
        raise _Failure(
            f"{prefix}: {path}:{exc.line}:{exc.column}: {exc.detail}"
        ) from exc
    return locale, translation


def _compile(
    path: str, locale: Locale | None, translation: Translation
) -> CodeType | None:
    try:
        return compile(translation.python, path, "exec")
    except SyntaxError as exc:
        lineno = exc.lineno or 1
        column = translation.original_column(lineno, exc.offset or 1)
        prefix = _message(locale, "syntax_error", "Syntax error")
        print(
            f"{prefix}: {path}:{lineno}:{column}: {exc.msg}",
            file=sys.stderr,
        )
        return None


def _run(namespace: argparse.Namespace) -> int:
    try:
        locale, translation = _prepare(namespace.file, namespace.lang)
    except _Failure as exc:
        print(f"polyglot-python: {exc.message}", file=sys.stderr)
        return 1

    code = _compile(namespace.file, locale, translation)
    if code is None:
        return 1

    module = types.ModuleType("__main__")
    module.__file__ = os.path.abspath(namespace.file)
    if sys.version_info < (3, 15):
        # CPython 3.15 no longer sets __cached__ on modules.
        module.__cached__ = None
    module.__loader__ = SourceFileLoader("__main__", module.__file__)
    module.__dict__["__builtins__"] = builtins
    script_dir = os.path.dirname(module.__file__)
    saved_main = sys.modules.get("__main__", _MISSING)
    saved_path = list(sys.path)
    saved_argv = sys.argv
    sys.modules["__main__"] = module
    sys.path.insert(0, script_dir)
    sys.argv = [namespace.file, *namespace.args]
    try:
        exec(code, module.__dict__)
    except SystemExit as exc:
        if exc.code is None:
            return 0
        if isinstance(exc.code, int):
            return exc.code
        print(exc.code, file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        raise
    except Exception as exc:
        prefix = _message(locale, "runtime_error", "Runtime error")
        print(f"{prefix}: {namespace.file}", file=sys.stderr)
        traceback.print_exception(type(exc), exc, exc.__traceback__.tb_next)
        return 1
    finally:
        sys.argv = saved_argv
        sys.path[:] = saved_path
        if saved_main is _MISSING:
            sys.modules.pop("__main__", None)
        else:
            sys.modules["__main__"] = saved_main
    return 0


def _collect(paths: Sequence[str]) -> tuple[list[str], list[str]]:
    files: list[str] = []
    errors: list[str] = []
    for raw in paths:
        if not os.path.isdir(raw):
            files.append(raw)
            continue
        found: list[str] = []
        for root, dirs, names in os.walk(raw, followlinks=False):
            dirs[:] = sorted(name for name in dirs if not name.startswith("."))
            for name in sorted(names):
                if name.startswith("."):
                    continue
                candidate = os.path.join(root, name)
                if has_locale_suffix(candidate):
                    found.append(candidate)
        if not found:
            errors.append(f"no localized files in {raw}")
        files.extend(found)
    return files, errors


def _check(namespace: argparse.Namespace) -> int:
    files, errors = _collect(namespace.files)
    ok = not errors
    for message in errors:
        print(f"polyglot-python: {message}", file=sys.stderr)
    for path in files:
        try:
            locale, translation = _prepare(path, namespace.lang)
        except _Failure as exc:
            print(f"polyglot-python: {exc.message}", file=sys.stderr)
            ok = False
            continue
        if _compile(path, locale, translation) is None:
            ok = False
    return 0 if ok else 1


def _translate(namespace: argparse.Namespace) -> int:
    try:
        _, translation = _prepare(namespace.file, namespace.lang)
    except _Failure as exc:
        print(f"polyglot-python: {exc.message}", file=sys.stderr)
        return 1

    if namespace.output:
        try:
            with open(namespace.output, "w", encoding="utf-8", newline="") as handle:
                handle.write(translation.python)
        except OSError as exc:
            reason = exc.strerror or str(exc)
            print(
                f"polyglot-python: cannot write {namespace.output}: {reason}",
                file=sys.stderr,
            )
            return 1
    else:
        sys.stdout.write(translation.python)
    return 0


def _locales(_namespace: argparse.Namespace) -> int:
    locales = load_locales()
    print(f"{'code':<6}{'name':<18}keywords")
    for code in sorted(locales):
        locale = locales[code]
        print(f"{code:<6}{locale.name:<18}{len(locale.keywords)}")
    return 0


def _keywords(namespace: argparse.Namespace) -> int:
    locales = load_locales()
    try:
        locale = _find_locale(locales, namespace.code.strip().lower())
    except _Failure as exc:
        print(f"polyglot-python: {exc.message}", file=sys.stderr)
        return 1
    width = max(len(word) for word in keyword.kwlist)
    print(f"{'python':<{width}}  {locale.name}")
    for word in keyword.kwlist:
        print(f"{word:<{width}}  {locale.keywords[word]}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="polyglot-python",
        description="Write Python in your own language: deterministic keyword translation.",
    )
    parser.add_argument(
        "--version", action="version", version=f"polyglot-python {__version__}"
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

    check = subparsers.add_parser(
        "check", help="translate and compile programs without running them"
    )
    check.add_argument(
        "files",
        nargs="+",
        metavar="PATH",
        help="localized source files, or directories to search",
    )
    check.add_argument("--lang", metavar="CODE", help="locale code, e.g. tr")
    check.set_defaults(handler=_check)

    listing = subparsers.add_parser("locales", help="list bundled locales")
    listing.set_defaults(handler=_locales)

    keywords = subparsers.add_parser(
        "keywords", help="print a locale's keyword mapping"
    )
    keywords.add_argument("code", help="locale code, e.g. tr")
    keywords.set_defaults(handler=_keywords)

    return parser


def _silence_broken_stdout() -> None:
    devnull = os.open(os.devnull, os.O_WRONLY)
    try:
        os.dup2(devnull, sys.stdout.fileno())
    except (OSError, ValueError):
        pass
    finally:
        os.close(devnull)


def main(argv: Sequence[str] | None = None) -> int:
    _configure_console()
    parser = build_parser()
    namespace = parser.parse_args(argv)
    try:
        return namespace.handler(namespace)
    except BrokenPipeError:
        _silence_broken_stdout()
        return 1


if __name__ == "__main__":
    sys.exit(main())
