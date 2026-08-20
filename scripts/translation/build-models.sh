#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
OUTPUT_DIR="${1:-}"

if [[ -z "$OUTPUT_DIR" ]]; then
  echo "Usage: $0 OUTPUT_DIR" >&2
  exit 2
fi

OUTPUT_DIR="$(realpath -m "$OUTPUT_DIR")"
if [[ -e "$OUTPUT_DIR/es-en" || -e "$OUTPUT_DIR/en-es" ]]; then
  echo "Refusing to overwrite existing model directories in $OUTPUT_DIR" >&2
  exit 2
fi

BUILD_DIR="$(mktemp -d)"
cleanup() {
  find "$BUILD_DIR" -mindepth 1 -delete
  rmdir "$BUILD_DIR"
}
trap cleanup EXIT

# Keep multi-gigabyte source weights inside the disposable build directory.
export HF_HOME="$BUILD_DIR/huggingface"
export HF_HUB_DISABLE_TELEMETRY=1

python3.12 -m venv "$BUILD_DIR/venv"
"$BUILD_DIR/venv/bin/python" -m pip install --no-cache-dir pip==26.2.1
"$BUILD_DIR/venv/bin/python" -m pip install \
  --no-cache-dir \
  -r "$ROOT_DIR/backend/requirements-translation-build.txt"

mkdir -p "$OUTPUT_DIR"
"$BUILD_DIR/venv/bin/python" -m ctranslate2.converters.transformers \
  --model Helsinki-NLP/opus-mt-es-en \
  --revision c96e2c5399ebfae4fc43d9669556b9afa74bb69d \
  --output_dir "$OUTPUT_DIR/es-en" \
  --quantization int8 \
  --copy_files source.spm target.spm

"$BUILD_DIR/venv/bin/python" -m ctranslate2.converters.transformers \
  --model Helsinki-NLP/opus-mt-en-es \
  --revision 5bc4493d463cf000c1f0b50f8d56886a392ed4ab \
  --output_dir "$OUTPUT_DIR/en-es" \
  --quantization int8 \
  --copy_files source.spm target.spm

MODEL_OUTPUT_DIR="$OUTPUT_DIR" PYTHONPATH="$ROOT_DIR/backend" \
  "$BUILD_DIR/venv/bin/python" -c \
  'import os; from pathlib import Path; from crushme_app.services.translation_manifest import validate_model_bundle; validate_model_bundle(Path(os.environ["MODEL_OUTPUT_DIR"]))'
chmod -R go-w "$OUTPUT_DIR"
echo "Verified CPU-only translation models: $OUTPUT_DIR"
