# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project uses
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - Unreleased

### Added

- `polyglot-python check FILE [--lang CODE]` translates and compiles without
  executing, with localized syntax errors.
- Russian (`ru`) locale, including `examples/classify.ru`.
- Release workflow using PyPI Trusted Publishing.

### Changed

- Tests cover every keyword in both directions for all 9 locales, every example
  through the CLI, and version consistency with the changelog.
- CI tests Python 3.12-3.14 on Linux and 3.12 on Windows and macOS, cancels
  superseded runs, enforces job timeouts, and smoke-tests the built wheel in a
  clean environment.
- Dependabot updates pip dependencies and GitHub Actions weekly.
- Package metadata uses PEP 639 license expressions.

## [0.1.0] - 2026-10-31

### Added

- Initial deterministic keyword transpiler with 8 locales: tr, es, pt, de, fr,
  zh, hi, ar. Phase 1 prototype, not published to PyPI.
