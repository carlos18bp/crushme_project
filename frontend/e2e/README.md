# CrushMe E2E

Playwright starts Django on `127.0.0.1:8001` with
`crushme_project.settings_e2e`, prepares a deterministic file-backed SQLite
database, and starts Vite on `127.0.0.1:5174`.

```bash
cd frontend
npx playwright install chromium
npm run e2e
```

Production hosts are rejected in configuration and the test fixture verifies
the backend identity through `/api/health/`. Remote staging additionally
requires `E2E_REMOTE_STAGING=1`; API writes remain blocked unless
`E2E_ALLOW_STAGING_WRITES=1` is also explicit.

Selectors must prefer roles, labels, or `data-testid`. Test IDs describe a
stable business element (`login-submit`, `catalog-heading`) and must not encode
CSS structure or translated copy.
