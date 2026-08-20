# CrushMe E2E

Playwright starts Django on `127.0.0.1:8001` with
`crushme_project.settings_e2e`, prepares a deterministic file-backed SQLite
database, and starts Vite on `127.0.0.1:5174`.

```bash
cd frontend
npx playwright install chromium
npm run e2e
```

All remote hosts are rejected in configuration and the test fixture requires
the backend identity from `/api/health/` to report `environment=e2e`.

Selectors must prefer roles, labels, or `data-testid`. Test IDs describe a
stable business element (`login-submit`, `catalog-heading`) and must not encode
CSS structure or translated copy.
