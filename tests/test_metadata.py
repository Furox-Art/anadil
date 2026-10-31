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
