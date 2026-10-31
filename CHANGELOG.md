# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project uses
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Six locales: Italian (`it`), Dutch (`nl`), Polish (`pl`), Indonesian (`id`),
  Vietnamese (`vi`) and Japanese (`ja`), each with an `examples/classify.<code>`
  program.
- A broader `examples/tour.<code>` program per locale that exercises all 35
  keywords (classes, exceptions, generators, closures, `with`,
  `async`/`await`) and is verified to translate back to a reference program.
- `polyglot-python keywords CODE` prints a locale's complete
  Python-to-localized keyword table.
- Five locales: Korean (`ko`), Ukrainian (`uk`), Romanian (`ro`), Swedish (`sv`)
  and Greek (`el`), each with `classify` and `tour` example programs.
- `check` accepts several files in one invocation and exits nonzero if any of
  them fails, so a whole set of localized sources can be validated in CI.

### Fixed

- `run` now executes a program the way `python FILE` does: the script's
  directory leads `sys.path`, so sibling imports work, and the program is
  registered as the `__main__` module.

## [0.2.1] - 2026-11-01

### Added

- npm release workflow using Trusted Publishing.

## [0.2.0] - 2026-10-31

### Added

- `polyglot-python check FILE [--lang CODE]` translates and compiles without
  executing, with localized syntax errors.
- Russian (`ru`) locale, including `examples/classify.ru`.
- Release workflow using PyPI Trusted Publishing.
- npm wrapper package that forwards to the Python CLI.

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
