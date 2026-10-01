from __future__ import annotations

import pathlib
import tomllib


ROOT = pathlib.Path(__file__).resolve().parents[1]


def test_supported_python_range_matches_ci_contract():
    payload = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    assert payload["project"]["requires-python"] == ">=3.11,<3.13"


def test_default_runtime_is_pinned_to_ci_python():
    assert (ROOT / ".python-version").read_text(encoding="utf-8").strip() == "3.12.14"
