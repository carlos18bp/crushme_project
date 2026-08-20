"""Behavior tests for the canonical standards baseline checker."""

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]
CHECKER = REPO_ROOT / "scripts" / "check_standards_baseline.py"
DOCUMENTS = (
    "docs/BACKEND_AND_FRONTEND_COVERAGE_REPORT_STANDARD.md",
    "docs/DJANGO_VUE_ARCHITECTURE_STANDARD.md",
    "docs/E2E_FLOW_COVERAGE_REPORT_STANDARD.md",
    "docs/GLOBAL_RULES_GUIDELINES.md",
    "docs/TESTING_QUALITY_STANDARDS.md",
    "docs/TEST_QUALITY_GATE_REFERENCE.md",
)


def _sha256(content):
    return hashlib.sha256(content).hexdigest()


@pytest.fixture
def baseline_repo(tmp_path):
    """Create a repository whose six canonical documents match the manifest."""
    content = b"canonical standard\n"
    documents = {}
    for relative_path in DOCUMENTS:
        document = tmp_path / relative_path
        document.parent.mkdir(parents=True, exist_ok=True)
        document.write_bytes(content)
        documents[relative_path] = _sha256(content)

    manifest = {
        "schema_version": 1,
        "source": {
            "repository": (
                "https://github.com/carlos18bp/base_django_vue_feature.git"
            ),
            "profile": "vue",
            "commit": "0" * 40,
        },
        "documents": documents,
    }
    (tmp_path / ".standards-baseline.json").write_text(
        json.dumps(manifest), encoding="utf-8"
    )
    return tmp_path


def _run_checker(repo_root):
    return subprocess.run(
        [sys.executable, str(CHECKER), "--repo-root", str(repo_root)],
        capture_output=True,
        check=False,
        text=True,
    )


def test_matching_documents_exit_zero(baseline_repo):
    """A complete matching snapshot exits successfully."""
    result = _run_checker(baseline_repo)

    assert result.returncode == 0


def test_changed_document_exits_one(baseline_repo):
    """A locally changed canonical document reports drift."""
    (baseline_repo / DOCUMENTS[0]).write_text("local edit\n", encoding="utf-8")

    result = _run_checker(baseline_repo)

    assert result.returncode == 1


def test_invalid_manifest_exits_two(tmp_path):
    """Malformed manifest JSON reports invalid configuration."""
    (tmp_path / ".standards-baseline.json").write_text("{", encoding="utf-8")

    result = _run_checker(tmp_path)

    assert result.returncode == 2
