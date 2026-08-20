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

_No resolved issues recorded yet._
