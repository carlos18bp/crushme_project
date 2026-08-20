#!/usr/bin/env python3
"""Verify the canonical Base Vue standards copied into this repository."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path, PurePosixPath
from typing import Any


MANIFEST_NAME = ".standards-baseline.json"
SOURCE_REPOSITORY = "https://github.com/carlos18bp/base_django_vue_feature.git"
REQUIRED_DOCUMENTS = {
    "docs/BACKEND_AND_FRONTEND_COVERAGE_REPORT_STANDARD.md",
    "docs/DJANGO_VUE_ARCHITECTURE_STANDARD.md",
    "docs/E2E_FLOW_COVERAGE_REPORT_STANDARD.md",
    "docs/GLOBAL_RULES_GUIDELINES.md",
    "docs/TESTING_QUALITY_STANDARDS.md",
    "docs/TEST_QUALITY_GATE_REFERENCE.md",
}
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")
COMMIT_PATTERN = re.compile(r"^[0-9a-f]{40}$")


class ManifestError(ValueError):
    """Raised when the baseline manifest cannot be trusted."""


def _require_object(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ManifestError(f"{label} must be a JSON object")
    return value


def _load_manifest(path: Path) -> dict[str, Any]:
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ManifestError(f"missing {MANIFEST_NAME}") from exc
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ManifestError(f"cannot read {MANIFEST_NAME}: {exc}") from exc

    manifest = _require_object(manifest, "manifest")
    expected_keys = {"schema_version", "source", "documents"}
    if set(manifest) != expected_keys:
        raise ManifestError(
            f"manifest keys must be exactly {sorted(expected_keys)}"
        )
    if manifest["schema_version"] != 1:
        raise ManifestError("schema_version must be 1")

    source = _require_object(manifest["source"], "source")
    expected_source_keys = {"repository", "profile", "commit"}
    if set(source) != expected_source_keys:
        raise ManifestError(
            f"source keys must be exactly {sorted(expected_source_keys)}"
        )
    if source["repository"] != SOURCE_REPOSITORY:
        raise ManifestError(f"source.repository must be {SOURCE_REPOSITORY}")
    if source["profile"] != "vue":
        raise ManifestError("source.profile must be vue")
    if not isinstance(source["commit"], str) or not COMMIT_PATTERN.fullmatch(
        source["commit"]
    ):
        raise ManifestError("source.commit must be a lowercase 40-character SHA")

    documents = _require_object(manifest["documents"], "documents")
    document_paths = set(documents)
    if document_paths != REQUIRED_DOCUMENTS:
        missing = sorted(REQUIRED_DOCUMENTS - document_paths)
        extra = sorted(document_paths - REQUIRED_DOCUMENTS)
        raise ManifestError(f"documents set mismatch; missing={missing}, extra={extra}")

    for relative_path, expected_hash in documents.items():
        path = PurePosixPath(relative_path)
        if path.is_absolute() or ".." in path.parts:
            raise ManifestError(f"unsafe document path: {relative_path}")
        if not isinstance(expected_hash, str) or not SHA256_PATTERN.fullmatch(
            expected_hash
        ):
            raise ManifestError(f"invalid SHA-256 for {relative_path}")

    return manifest


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def check_baseline(repo_root: Path) -> list[str]:
    root = repo_root.resolve()
    if not root.is_dir():
        raise ManifestError(f"repo root is not a directory: {root}")

    manifest = _load_manifest(root / MANIFEST_NAME)
    mismatches: list[str] = []
    for relative_path, expected_hash in sorted(manifest["documents"].items()):
        document_path = (root / relative_path).resolve()
        if not document_path.is_relative_to(root):
            raise ManifestError(f"document escapes repo root: {relative_path}")
        if not document_path.is_file():
            mismatches.append(f"missing: {relative_path}")
            continue
        actual_hash = _sha256(document_path)
        if actual_hash != expected_hash:
            mismatches.append(
                f"drift: {relative_path} expected={expected_hash} actual={actual_hash}"
            )
    return mismatches


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Verify canonical Base Vue standards by SHA-256."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Repository root containing .standards-baseline.json.",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    try:
        mismatches = check_baseline(args.repo_root)
    except ManifestError as exc:
        print(f"Standards baseline configuration invalid: {exc}", file=sys.stderr)
        return 2

    if mismatches:
        print("Standards baseline drift detected:", file=sys.stderr)
        for mismatch in mismatches:
            print(f"- {mismatch}", file=sys.stderr)
        return 1

    print(f"Standards baseline OK ({len(REQUIRED_DOCUMENTS)} documents)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
