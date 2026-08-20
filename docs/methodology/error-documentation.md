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

## Resolved Issues

### [ERR-001] Accidental staging coordinate
- **Date**: 2026-08-20
- **Context**: The first modernization attempt created a work clone and fleet
  artifacts as if CrushMe required a permanent staging deployment.
- **Root Cause**: A safe authoring coordinate was incorrectly modeled as a
  second runtime coordinate.
- **Resolution**: Removed the clone, registry entry, DNS assumptions, and
  Nginx/systemd/env artifacts. Modernization now uses a temporary Git worktree
  while production remains on `main`.
