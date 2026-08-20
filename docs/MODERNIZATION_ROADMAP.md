# CrushMe Modernization Roadmap

## Objective

Promote CrushMe from `lifecycle: legacy` to the maintained fleet standard used
by mature projects, without changing its e-commerce, wishlist, translation,
currency, payment, or public API behavior.

The promotion path is `legacy -> modernizing -> active`. The intermediate state
allows AI ecosystem maintenance while making it explicit that final technical
and operational gates are still pending.

## Baseline (2026-08-20)

| Capability | Current state |
|---|---|
| Fleet lifecycle | Production active; promotion program begins from `legacy` |
| AI ecosystem | Partial catalog, no QA agents, drift from the fleet baseline |
| CI | Test-quality workflow only; no backend/unit/E2E execution workflow |
| Backend tests | 0 behavior tests |
| Frontend unit tests | 1 test file |
| E2E tests | 0 specs; flow registry contains only 3 provisional flows |
| QA safety | No isolated E2E environment; fake-data deletion can target all non-superuser data |
| Dependencies | Heavy translation/ML stack requires reachability and vulnerability review |
| Operations | Versioned systemd/Nginx guidance differs from deployed production units |

## Execution Protocol

- Integration branch: `release/crushme-modernization`.
- Every writable phase uses its own session branch/worktree and targets the
  integration branch. A maximum of four phases may write in parallel.
- Parallel phases must own disjoint files. A wave closes only after all its
  phases are integrated and its gate passes.
- Local verification remains targeted (maximum 20 tests per command). CI runs
  the complete suites as partitioned jobs.
- The production clone remains on `main`; production data is never used for QA.
- Public response shapes, locale routes, the single HTTP client, FBV views,
  WooCommerce mirroring, offline translation, PayPal, and Wompi are invariants.

## Wave 0 - Transition and Work Coordinate

- [x] Add the `modernizing` lifecycle to the fleet contract.
- [x] Register `crushme_project_staging` as the isolated modernization worktree.
- [x] Create `release/crushme-modernization` without changing production checkout.
- [x] Record this roadmap and the verified baseline.

**Gate:** registry validation passes, the work coordinate resolves to staging,
and AI ecosystem tooling includes CrushMe without classifying it as promoted.

## Wave 1 - AI Ecosystem, Cleanup, and Standards

- [ ] Synchronize Codex, Claude Code, Windsurf, skills, and QA agents from the
  canonical toolkit; reconcile project-specific guidance after synchronization.
- [ ] Run `repo-cleanup` read-only, approve findings, then remove only verified
  artifacts, dead code, stale configuration, and obsolete documentation.
- [ ] Refresh Memory Bank, README, deployment guidance, and runtime identities.
- [ ] Align pre-commit, branch protocol, test-quality core, and development rules.

**Gate:** AI drift is zero, the repository is clean, and instructions match the
actual Vue/Django architecture and deployed services.

## Wave 2 - Vulnerabilities, Dependencies, and Hardening

- [ ] Run `vuln-audit` report-first for Python and npm, then apply approved
  patch/minor updates. Major upgrades require a separate compatibility decision.
- [ ] Prove dependency reachability before removing heavy ML/translation packages;
  validate WooCommerce synchronization and offline translation after any removal.
- [ ] Audit authorization, validation, uploads, JWT, payment webhooks, and log
  redaction; fix findings without changing public business contracts.
- [ ] Harden environment examples, sandbox defaults, CORS/CSRF, headers, rate
  limits, systemd, and Nginx configuration.

**Gate:** no unmitigated critical/high vulnerability, successful builds and
deployment checks, and every deferred major has a documented owner and reason.

## Wave 3 - Test Platform and CI

- [ ] Add isolated backend test/E2E settings, factories, fixtures, and mocks for
  all external systems.
- [ ] Complete the Vue/Jest harness, component setup, request mocks, and selector
  conventions.
- [ ] Add Playwright orchestration, `.env.e2e.example`, deterministic seed data,
  and guards that refuse production in code.
- [ ] Add `.testquality.yml`, junk baseline, complete flow registry, coverage
  tooling, and partitioned backend/unit/E2E CI jobs.

SQLite is the fast isolated default; CI also runs a focused MySQL migration and
compatibility job. Fake-data commands must be idempotent and scoped to an E2E
scenario; `--confirm` alone must never authorize production deletion.

**Gate:** CI is reproducible and a test proves fake-data commands cannot touch a
production-grade database.

## Wave 4 - Functional QA

- [ ] Run `qa` in dry-run mode to regenerate and rank the real flow map.
- [ ] Fan out backend, frontend-unit, and E2E authoring through `qa --apply`.
- [ ] Validate all E2E drafts live and heal failures with bounded retries.
- [ ] Run the quality gate, test audit, and complete partitioned CI.

P1/P2 coverage includes authentication, catalog, cart, public/shared wishlists,
guest gifting, checkout, orders, PayPal, Wompi, WooCommerce sync/translation,
profiles, reviews, locale, and currency. Each flow covers success, error,
failure, and display outcomes or records a justified exemption.

**Gate:** QA is green with no junk-only flow and no unvalidated E2E spec.

## Wave 5 - Staging, Operations, and Performance

- [ ] Deploy `crushme.projectapp.co` from the integration branch using database
  `crushme_staging`, Redis cache DB 10, Huey DB 11, socket
  `/run/crushme_staging.sock`, and sandbox-only external integrations.
- [ ] Add TLS, health checks, deterministic staging data, and post-deploy checks.
- [ ] Validate logs, timers, backups, and a real restore rehearsal on staging.
- [ ] Profile queries, cache, static/media delivery, Huey, and memory; size limits
  with at least 30% headroom above measured peak use.

The Vue SPA remains built into Django; no SSR or persistent Node service is added.

**Gate:** staging is reproducible, restore-tested, observable, and green under
post-deploy validation.

## Wave 6 - Certification and Promotion

Run four read-only gates in parallel: `qa`, `vuln-audit`,
`sync-ai-ecosystems --check`, and `full-audit` plus operational diagnostics.
Resolve all blocking findings, authorize the one-shot release merge, integrate
into `main`, snapshot and deploy production, run non-destructive smoke checks,
and observe the runtime for at least 24 hours with rollback ready.

Only after stable production verification:

- [ ] Change lifecycle from `modernizing` to `active`.
- [ ] Remove the one-shot release authorization.
- [ ] Refresh this roadmap, Memory Bank, and fleet QA memory.

## Promotion Definition of Done

- Canonical AI ecosystem reports no drift.
- CI, quality gate, and QA are green with no unvalidated critical flow.
- No critical/high vulnerability remains without an approved mitigation.
- Fake data and E2E cannot reach production data or live external gateways.
- Staging deploy and backup restoration are proven.
- Production deploy, health checks, and the observation window are green.
- Business invariants and public interfaces remain compatible.
