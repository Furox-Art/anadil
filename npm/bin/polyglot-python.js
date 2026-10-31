#!/usr/bin/env node
'use strict';

const { spawnSync } = require('node:child_process');

function candidates() {
  if (process.env.POLYGLOT_PYTHON) {
    return [{ command: process.env.POLYGLOT_PYTHON, prefix: [] }];
  }
  if (process.platform === 'win32') {
    return [
      { command: 'python', prefix: [] },
      { command: 'python3', prefix: [] },
      { command: 'py', prefix: ['-3'] },
    ];
  }
  return [
    { command: 'python3', prefix: [] },
    { command: 'python', prefix: [] },
  ];
}

function findPython() {
  for (const candidate of candidates()) {
    const probe = spawnSync(
      candidate.command,
      [...candidate.prefix, '-c', 'import polyglot_python'],
      { stdio: 'ignore' },
    );
    if (!probe.error && probe.status === 0) {
      return candidate;
    }
  }
  return null;
}

const python = findPython();
if (python === null) {
  const reason = process.env.POLYGLOT_PYTHON
    ? `POLYGLOT_PYTHON="${process.env.POLYGLOT_PYTHON}" was not found or cannot import polyglot_python.`
    : 'No Python 3.12+ interpreter with polyglot_python installed was found.';
  console.error(`polyglot-python: ${reason}`);
  console.error('Install the Python package: pip install "polyglot-python>=0.2.0"');
  console.error('Set POLYGLOT_PYTHON to a Python executable to choose it explicitly.');
  process.exit(1);
}

const result = spawnSync(
  python.command,
  [...python.prefix, '-m', 'polyglot_python', ...process.argv.slice(2)],
  { stdio: 'inherit' },
);

if (result.error) {
  console.error(`polyglot-python: failed to run ${python.command}: ${result.error.message}`);
  process.exit(1);
}

process.exit(result.status === null ? 1 : result.status);
