# polyglot-python (npm)

Thin Node.js wrapper for the
[polyglot-python](https://github.com/Furox-Art/polyglot-python) Python CLI.
It does not reimplement the transpiler: it finds a Python 3.12+ interpreter
that has the Python package installed and forwards every argument to
`python -m polyglot_python`.

## Requirements

- Python 3.12 or newer
- The Python package: `pip install "polyglot-python>=0.2.0"`
- Node.js 18 or newer

## Usage

```bash
npm install -g polyglot-python
polyglot-python run examples/classify.tr
polyglot-python check examples/classify.tr
polyglot-python translate examples/classify.tr -o classify.py
polyglot-python locales
```

The wrapper accepts the same commands and flags as the Python CLI; see the
[main README](https://github.com/Furox-Art/polyglot-python#cli).

Set `POLYGLOT_PYTHON` to a Python executable to override interpreter detection:

```bash
POLYGLOT_PYTHON=/usr/bin/python3.12 polyglot-python --version
```

## License

MIT
