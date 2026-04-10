---
trigger: model_decision
description: Error documentation and known issues tracking. Reference when debugging, fixing bugs, or encountering recurring issues.
---

# Error Documentation — ProjectApp

This file tracks known errors, their context, and resolutions. When a reusable fix or correction is found during development, document it here to avoid repeating the same mistake.

---

## Format

```
### [ERROR-NNN] Short description
- **Date**: YYYY-MM-DD
- **Context**: Where/when this error occurs
- **Root Cause**: Why it happens
- **Resolution**: How to fix it
- **Files Affected**: List of files
```

---

## Known Issues

### [KNOWN-001] kore_project Next.js server occupies port 3000
- **Date**: 2025-07-07
- **Context**: A Windsurf terminal runs `npm run dev --port 3000` for `kore_project`, which respawns after being killed
- **Impact**: Nuxt dev server can't bind port 3000; E2E tests fail intermittently
- **Workaround**: Run Nuxt on port 3001 with `E2E_PORT=3001`
- **Permanent fix**: Close the kore_project terminal in Windsurf IDE

---

## Resolved Issues

### [ERR-001] defineI18nRoute(false) conflicts with i18n strategy 'prefix'
- **Date**: 2025-07-07
- **Context**: All platform pages had `defineI18nRoute(false)`, but Nuxt i18n uses `strategy: 'prefix'`
- **Root Cause**: Routes returned 404 because the router expected locale-prefixed paths
- **Resolution**: Removed `defineI18nRoute(false)` from all 11 platform page files
- **Files Affected**: `frontend/pages/platform/*.vue`, `frontend/pages/platform/projects/**/*.vue`, `frontend/pages/platform/clients/**/*.vue`

### [ERR-002] platform-auth middleware bypassed by i18n locale prefix (SECURITY)
- **Date**: 2025-07-07
- **Context**: `platform-auth.js` checked `to.path.startsWith('/platform')` but i18n produces `/en-us/platform/login`
- **Root Cause**: Path comparisons didn't strip locale prefix, so all auth guards were bypassed
- **Resolution**: Added `rawPath = to.path.replace(/^\/[a-z]{2}(-[a-z]{2})?(?=\/)/, '')` before path checks
- **Files Affected**: `frontend/middleware/platform-auth.js`

### [ERR-003] Playwright networkidle hangs with Vite HMR WebSocket
- **Date**: 2025-07-07
- **Context**: `page.waitForLoadState('networkidle')` never resolves in Nuxt dev mode
- **Root Cause**: Vite HMR WebSocket keeps persistent connection, preventing networkidle
- **Resolution**: Use `domcontentloaded` + explicit element waits instead
- **Files Affected**: All 14 `frontend/e2e/platform/*.spec.js` files

### [ERR-004] Playwright strict mode violations from sidebar + page content
- **Date**: 2025-07-07
- **Context**: `getByText('Tablero')`, `getByText('Proyectos')`, etc. matched both sidebar links and page headings
- **Resolution**: Scope to `page.locator('main')`, use `getByRole('heading')`, or `{ exact: true }`
- **Files Affected**: Multiple platform E2E spec files
