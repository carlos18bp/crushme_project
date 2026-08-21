# Error Documentation - CrushMe

This file records reusable failures, risks, and resolutions.

## Known Issues

### [KNOWN-001] Argos pins a Stanza release with a model-loading advisory

- **Date**: 2026-08-20
- **Context**: Argos Translate 1.11.0 requires Stanza 1.10.1, reported as
  `PYSEC-2026-3075`; the fixed Stanza release is incompatible with that pin.
- **Reachability**: Application code does not import Stanza or create a Stanza
  pipeline. Settings force Argos `MINISBD` chunking on CPU.
- **Mitigation**: Startup rejects any other chunk/device setting, and a
  regression test against real Argos 1.11 proves MiniSBD is selected even when
  a package advertises a Stanza model path.
- **Follow-up**: Wave 7 stage 1 keeps this mitigation only for explicit
  rollback. Close this issue by removing Argos/Stanza after the CTranslate2
  observation gate passes.

### [KNOWN-002] Translation dependency retirement is observation-gated

- **Date**: 2026-08-20
- **Context**: The CPU-only CTranslate2 daemon is implemented with static-int8
  models, but Argos/Torch must remain available for the stage-1 rollback.
- **Risk**: Removing rollback dependencies before representative production
  sync and traffic would combine a model change with an irreversible release.
- **Gate**: 48 hours, one representative WooCommerce sync, zero translation
  errors/OOM/restarts, public ES/EN parity, and at least 25% daemon headroom.

## Resolved Issues

### [ERR-004] Translation cold start breached the capacity headroom gate

- **Date**: 2026-08-21
- **Context**: The first production restart after model pages left the host
  cache charged 200.5 MiB to the translation cgroup, leaving 21.7% against the
  original 256 MiB hard limit even though process RSS remained about 160 MiB.
- **Root Cause**: Authoring measurements captured hot-cache RSS but not the
  reclaimable model file cache charged during a production cold start.
- **Resolution**: Raised only the isolated daemon limits to
  `MemoryHigh=240M` and `MemoryMax=320M`. CPU, thread count, package allowlist,
  and runtime behavior are unchanged; the observed cold peak retains about
  37% hard-limit headroom.

### [ERR-003] Product cards exposed an absent stock translation key

- **Date**: 2026-08-20
- **Context**: After a failed stock check, product-card actions displayed the
  literal key `products.product.outOfStock` instead of localized text.
- **Root Cause**: The component referenced the product-action namespace, while
  the EN/ES messages define the label at `products.outOfStock`.
- **Resolution**: Pointed all product-card action variants at the canonical key
  and added a component regression test driven by an out-of-stock response.

### [ERR-001] Accidental staging coordinate

- **Date**: 2026-08-20
- **Context**: The first modernization attempt created a clone and fleet
  artifacts as if CrushMe required a permanent staging deployment.
- **Root Cause**: A safe authoring coordinate was incorrectly modeled as a
  second runtime coordinate.
- **Resolution**: Removed clone, registry entry, DNS assumptions, and
  Nginx/systemd/environment artifacts. Modernization uses a temporary Git
  worktree while production remains the only runtime.

### [ERR-002] Active production database credential exposed in Git history

- **Date**: 2026-08-20
- **Context**: The removed `backend/setup_db.sql` contained the active
  `crushme_user` password in shared history.
- **Root Cause**: Initial database bootstrap material was committed with a real
  credential.
- **Resolution**: Created and restore-tested fresh backups, provisioned
  `crushme_app_20260820` with only `crushme.*` grants, atomically updated
  runtime and protected stores, restarted/verified both services, and dropped
  the former MySQL user. Toolkit source commit: `52d9898`.
- **Risk Acceptance**: The revoked value remains in shared Git history.
  Rewriting history would disrupt active branches without improving revocation;
  this specific historical value is accepted as revoked. New/current secrets
  remain blocked by detect-secrets.
