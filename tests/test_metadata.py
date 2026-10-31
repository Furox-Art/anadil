import json
import tomllib
from pathlib import Path

import polyglot_python

ROOT = Path(__file__).resolve().parents[1]


def test_version_matches_pyproject():
    metadata = tomllib.loads(
        ROOT.joinpath("pyproject.toml").read_text(encoding="utf-8")
    )
    assert polyglot_python.__version__ == metadata["project"]["version"]


def test_changelog_mentions_current_version():
    changelog = ROOT.joinpath("CHANGELOG.md").read_text(encoding="utf-8")
    assert f"## [{polyglot_python.__version__}]" in changelog


def test_npm_wrapper_matches_version():
    package = json.loads(ROOT.joinpath("npm", "package.json").read_text(encoding="utf-8"))
    assert package["name"] == "polyglot-python"
    assert package["version"] == polyglot_python.__version__
    binary = ROOT.joinpath("npm", package["bin"]["polyglot-python"])
    assert binary.is_file()
    assert binary.read_text(encoding="utf-8").startswith("#!/usr/bin/env node\n")
