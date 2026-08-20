# CrushMe Architecture Profile

## Purpose

CrushMe adopts the canonical Django + Vue development standards copied from
`base_django_vue_feature` at commit
`c580ea81ea70b7c878775c0f12e7eebbf75b3787`. The exact source and SHA-256 for
each canonical document are recorded in `.standards-baseline.json` and enforced
by `scripts/check_standards_baseline.py`.

This profile records project-specific implementation choices. It does not
weaken the security, testing, coverage, or business-logic rules in the
canonical standards. Generic examples in those documents must be translated to
the concrete paths and runtime described here.

## Documentation Precedence

1. Explicit operator requirements and the production business-behavior
   contract take priority.
2. Specialized canonical standards govern their subject: global rules, test
   quality, quality-gate behavior, unit coverage, and E2E flow coverage.
3. This profile governs CrushMe-specific architecture, names, and execution
   constraints when a generic template example differs.
4. `docs/methodology/` documents the observed system and decisions; it cannot
   silently relax a canonical rule.
5. `README.md` is an entry point, not a competing source of truth.

`AGENTS.md`, `CLAUDE.md`, and their scoped backend/frontend files govern agent
execution. They must point to this profile and remain synchronized across the
Codex and Claude Code ecosystems.

## Preserved Business Architecture

### Backend

- The existing `crushme_app` remains the single business app. Models,
  serializers, views, services, URLs, tasks, commands, and tests are separated
  by resource inside it.
- DRF endpoints remain function-based `@api_view` functions. Do not convert
  them to class-based views or ViewSets merely to resemble a template.
- Business and integration logic remains in `crushme_app/services/`; views
  validate input, enforce permissions, call services, and return responses.
- JWT protects the public API, while Django admin keeps session authentication
  and CSRF protection.
- WooCommerce catalog mirroring, public wishlists, crush verification, guest
  checkout, PayPal, Wompi, and server-authoritative payment totals are product
  contracts and must not change during standards convergence.

### Frontend

- The application is a Vue 3 + Vite SPA with locale-prefixed routes, Vue I18n,
  and Pinia state in `frontend/src/stores/modules/`.
- Existing stores use both setup and Options API styles. New stores should use
  the Composition/setup pattern; legacy stores are migrated only through a
  behavior-preserving change with focused tests.
- All API traffic goes through `frontend/src/services/request_http.js`. Do not
  add a parallel HTTP client or bypass its JWT refresh, CSRF, locale, and
  currency behavior.
- Vite output belongs in `backend/static/frontend/` and is generated, not
  hand-edited.

## Runtime Profile

- Python runs from `backend/venv_cpu/` during the stage-1 translation rollback
  window. The isolated production translation daemon uses
  `backend/venv_translation/`.
- CTranslate2 inference is hardcoded to CPU with static `int8` compute. The
  translation runtime must not import Torch, use CUDA, or install GPU wheels.
- Argos and its CPU-only Torch dependency remain only as an explicit rollback
  path until Wave 7 stage 2 removes them from the main application environment.
- Production uses MySQL 8, Redis DB 1 for cache, Redis DB 2 for Huey, Nginx,
  `crushme_project.service`, `crushme-huey.service`, and the candidate
  `crushme-translation.service`.
- Production code and data live in the primary checkout. Standards work uses
  temporary session worktrees; it must not create a staging clone or staging
  data coordinate.

## Quality And Safety Profile

- Backend tests use `crushme_project.settings_test`; Playwright uses
  `crushme_project.settings_e2e`. Both must stay isolated from production
  MySQL, Redis, email, and payment integrations.
- Never run Playwright, fake-data commands, or mutating QA against production.
- During ordinary development, run only focused files: at most 20 tests per
  command, at most three test commands per cycle, and at most two Playwright
  specs per invocation.
- Every user flow is tracked in `frontend/e2e/flow-definitions.json` and
  `docs/USER_FLOW_MAP.md`; missing coverage remains visible until a qualifying
  E2E test drives the flow through the UI.
- Production deployment is a separate, explicitly authorized operation with
  fresh database/media backups, migration checks, service restart, health
  verification, and rollback evidence.

## Deviation Governance

Convergence means applying the standard to new work and removing unjustified
drift, not rewriting stable business logic for structural symmetry. A new
deviation requires all of the following in the same PR:

- a concrete technical or product rationale;
- focused regression tests for preserved behavior;
- an update to this profile and the methodology memory;
- an explicit owner or removal condition when the deviation is temporary.

Canonical documents must never be edited locally. Update Base Vue first,
record the new source commit and hashes, copy the approved documents, and run
the baseline checker.
