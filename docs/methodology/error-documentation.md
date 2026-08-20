# Error Documentation — CrushMe

This file tracks known errors, their context, and resolutions. When a reusable fix or correction is found during development, document it here to avoid repeating the same mistake.

## Format

```
### [ERR-NNN] Short description
- **Date**: YYYY-MM-DD
- **Context**: Where/when this error occurs
- **Root Cause**: Why it happens
- **Resolution**: How to fix it
- **Files Affected**: List of files
```

## Known Issues

### [KNOWN-001] Production database credential exists in Git history
- **Date**: 2026-08-20
- **Context**: Repository cleanup found a literal credential in the former `backend/setup_db.sql`.
- **Root Cause**: Initial deployment bootstrap SQL was committed with a real password.
- **Impact**: The tracked value matches the active production database credential.
- **Required Resolution**: Rotate credentials, update protected stores atomically, verify services, and purge or explicitly accept Git-history exposure.
- **Files Affected**: Git history for `backend/setup_db.sql`; production environment and fleet credential store.

### [KNOWN-002] Permanent staging DNS is not provisioned
- **Date**: 2026-08-20
- **Context**: `crushme.projectapp.co` does not resolve.
- **Impact**: HTTPS staging deployment and external Playwright validation cannot complete.
- **Required Resolution**: Create DNS record to the staging VPS before Wave 5 certification.

## Resolved Issues

### [ERR-001] Payment sessions trusted client-controlled order data
- **Date**: 2026-08-20
- **Context**: PayPal and Wompi preparation/capture accepted values that could
  diverge from durable catalog and order state.
- **Root Cause**: Gateway payload construction lacked a single server-side
  integrity boundary and durable session correlation.
- **Resolution**: Rebuild products, variants, shipping, discounts, totals, and
  gift recipients server-side; verify gateway amounts/signatures and process
  sessions idempotently.
- **Files Affected**: Payment views/services, serializers, models, and integrity tests.

### [ERR-002] Test and E2E environments could reach runtime integrations
- **Date**: 2026-08-20
- **Context**: Isolated test runs inherited mutable currency and external-client
  defaults from application settings.
- **Root Cause**: There were no dedicated settings entry points or guarded E2E
  orchestration.
- **Resolution**: Add `settings_test`, `settings_e2e`, and `settings_ci_mysql`;
  pin exchange rates, clear external credentials, refuse production hosts and
  database names, and seed a deterministic scenario.
- **Files Affected**: Django settings, Playwright config, E2E scripts, seed and
  fake-data guards.

### [ERR-003] Cold E2E checkout navigation was flaky
- **Date**: 2026-08-20
- **Context**: The cart checkout case passed alone but timed out in a two-spec
  batch while Vite compiled the lazy checkout route.
- **Root Cause**: Home made unrelated requests, navigation observation started
  after the click, and a 10-second action timeout was below measured cold load.
  Ambiguous wishlist text also invoked offline Argos during an unrelated flow.
- **Resolution**: Host Navbar setup on the static terms route, register
  `waitForURL` before clicking, use a bounded 20-second conditional timeout,
  keep locale-unambiguous wishlist fixtures, and require cleanup `DELETE 200`.
- **Files Affected**: `frontend/e2e/helpers/test.js`, cart and wishlist specs.

### [ERR-004] Runtime documentation named the wrong production service
- **Date**: 2026-08-20
- **Context**: Historical guidance named `gunicorn.service` while the deployed
  app unit is `crushme_project.service`.
- **Root Cause**: Repository templates and live systemd identity had drifted.
- **Resolution**: Verify live units read-only and synchronize project guidance,
  deployment docs, and versioned runtime templates.
- **Files Affected**: AI guidance, Memory Bank, README, and deployment docs.
