#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
VENV_DIR="$ROOT_DIR/backend/venv_translation"

if [[ ! -x "$VENV_DIR/bin/python" ]]; then
  python3.12 -m venv "$VENV_DIR"
fi

"$VENV_DIR/bin/python" -m pip install --no-cache-dir pip==26.2.1
"$VENV_DIR/bin/python" -m pip install \
  --no-cache-dir \
  -r "$ROOT_DIR/backend/requirements-translation.txt"
"$VENV_DIR/bin/python" -m pip check

"$VENV_DIR/bin/python" - <<'PY'
from importlib import util
from importlib.metadata import distributions


def canonicalize(name: str) -> str:
    return name.lower().replace("_", "-")


expected = {
    "ctranslate2",
    "numpy",
    "pip",
    "pysbd",
    "pyyaml",
    "sentencepiece",
    "setuptools",
}
installed = {
    canonicalize(distribution.metadata["Name"])
    for distribution in distributions()
}
missing = expected - installed
unexpected = installed - expected
if missing or unexpected:
    raise SystemExit(
        "Translation runtime package mismatch: "
        f"missing={sorted(missing)} unexpected={sorted(unexpected)}"
    )

blocked_modules = {"onnxruntime", "spacy", "stanza", "torch"}
importable = {name for name in blocked_modules if util.find_spec(name) is not None}
if importable:
    raise SystemExit(
        f"Translation runtime contains prohibited modules: {sorted(importable)}"
    )
PY

echo "Verified Torch-free translation runtime: $VENV_DIR"
