# Lessons Learned - CrushMe

## Architecture

- The single `crushme_app` remains workable because views are split by resource
  and meaningful business logic already lives in services. Do not split it
  without a concrete ownership or deployment boundary.
- Function-based DRF views and the single Axios client are product architecture,
  not legacy defects to replace during maintenance.
- WooCommerce mirroring, offline bilingual translation, public wishlists,
  guest gifting, PayPal, and Wompi are business invariants.
- Payment gateways must never trust client totals. Durable, server-calculated
  `PaymentSession` state is the cross-request contract.

## Security

- JWT rotation requires concurrency control, not only
  `BLACKLIST_AFTER_ROTATION`; lock the outstanding token row and verify the race
  against MySQL in CI.
- Frontend refresh coordination needs both a shared promise and an auth epoch,
  otherwise logout can be undone by an older in-flight response.
- Production integration mode must fail closed. Sandbox defaults belong only in
  development/test settings.
- Upload validation must inspect decoded content and pixel count in addition to
  extension, MIME, and byte size.
- A secret removed from the current tree is not resolved until the credential
  is revoked, protected stores are synchronized, and services are verified.

## Development And Testing

- The venv is `backend/venv_cpu/`; use the PyTorch CPU index and avoid pip cache
  on this disk-constrained host.
- Backend tests use `settings_test.py`; E2E uses `settings_e2e.py`. Neither may
  inherit production database, Redis, email, or gateway resources.
- Six partitioned CI jobs own broad verification. Local runs stay targeted at
  no more than 20 tests, three commands per cycle, and two E2E specs.
- The semantic test-quality gate, Ruff/ESLint, Bandit, detect-secrets, npm audit,
  and pip-audit are complementary gates; none replaces behavior tests.

## Operations

- A Git worktree is sufficient to isolate authoring while production stays on
  clean `main`; it must not become a second deployable environment.
- A backup is not evidence until restore is rehearsed. Database restore and
  media file-count, byte-count, and inventory-hash checks all passed before the
  credential cutover.
- Runtime documentation must be derived from deployed service units, not old
  naming assumptions. The active units are `crushme_project.service` and
  `crushme-huey.service`.
- Infrastructure backups must not share the availability boundary of the task
  queue. A dedicated persistent systemd timer is independently observable and
  restore-testable.
- Importing Argos from URL/serializer modules loads Torch/ONNX into every web
  worker and Huey before it is needed. A local import at the translation call
  preserves behavior while restoring ordinary-request memory headroom.

## Remaining Debt

- Argos 1.11 pins vulnerable Stanza 1.10.1. MiniSBD/CPU makes the path
  unreachable, but the dependency must be reviewed monthly.
- PyTorch remains a heavy Argos dependency and drives disk/memory cost when an
  offline translation is executed.
- Vite still reports existing large-chunk warnings; measured production
  latency is the trigger for a separate code-splitting change.
- Critical business-flow gaps remain explicitly tracked by the Wave 4 flow
  map and continuous QA backlog.
