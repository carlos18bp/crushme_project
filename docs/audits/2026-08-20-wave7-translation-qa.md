# Wave 7 CPU-Only Translation QA

Date: 2026-08-20 UTC

Coordinate: authoring worktree on
`chore/20082026-crushme-cpu-translation`; production remained unchanged on
`main`.

## Verdict

**GREEN FOR STAGE-1 REVIEW.** The new local translation boundary, rollback
selection, model integrity checks, metadata persistence, and fail-open behavior
pass focused backend QA. Production deployment and its 48-hour observation
remain separate release gates.

## Safety

- QA used `settings_test.py`; no production database, Redis, integrations,
  fake data, E2E mutation, service, socket, or environment file was touched.
- The production preflight reported `fake_data_allowed=no`; that phase was
  skipped.
- Frontend/API payloads and existing cached translations are unchanged.

## Evidence

| Gate | Result |
|---|---|
| Focused backend behavior | 23/23 passed across 6 files |
| Existing Argos rollback regression | 1/1 passed |
| QA touched-file verify | 6 files, 0 errors, 0 warnings, green |
| Semantic test quality | 100/100, 0 findings, strict + Ruff |
| Ruff production/test slice | 0 findings |
| Pre-commit | Quality gate, detect-secrets, and Bandit passed across 48 files |
| Django system check | 0 issues |
| Migration drift | No schema changes |
| Dependency audit | Runtime and builder: 0 known vulnerabilities; build-only PyTorch CPU wheel is outside PyPI audit coverage |
| Minimal runtime integrity | `pip check` clean; exact allowlist; Torch/Stanza/spaCy/ONNX imports rejected |
| GPU/CUDA proof | 0 CUDA devices; CPU compute types only; no CUDA/NVIDIA package or shared-library dependency |
| Model build/install | Both pinned bundles reproduced with CTranslate2 4.8.1 / Transformers 5.15.1 and SHA-256 verified; build cache removed automatically |
| Live local daemon | ES->EN and EN->ES reference translations passed |
| Resource proof | 156 MiB RSS (160,188 KiB), 2 threads, Torch not loaded |
| Readiness | Configured daemon identity and Torch state are enforced by `/api/health/` |
| systemd candidate syntax | Translation, web, socket, and Huey units passed |

The global `$qa` read-out remains unchanged: 56/56 outcomes mapped, 4 covered,
16 partial, 36 missing, 0 junk-only, 0 unvalidated, and 1 negative-case gap;
the full gate reported zero errors, infrastructure errors, or warnings. Those
36 explicit gaps predate Wave 7 and are not converted into false coverage.

## Release Gates

Stage 1 still requires PR CI, fresh recovery artifacts, controlled production
deployment, the live translation runtime probe, representative WooCommerce
sync, and 48 hours without translation errors, OOM events, or restart loops.
Stage 2 dependency removal must not begin before those conditions pass.
