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
- **Follow-up**: Re-evaluate monthly. Re-enabling Stanza chunking or removing
  the guard is a release blocker until the dependency is fixed.

## Resolved Issues

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
