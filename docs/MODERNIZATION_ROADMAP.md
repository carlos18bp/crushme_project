# CrushMe Modernization Roadmap

## Objective

Promote CrushMe from its legacy baseline to the maintained fleet standard used
by the Vue scaffold and mature projects, without replacing its business model,
public domain, production data, or established Django/Vue architecture.

The only runtime coordinate is the production project at
`/home/ryzepeck/webapps/crushme_project`, serving `crushme.com.co` from database
`crushme`. The temporary modernization worktree is a Git authoring surface, not
a deployable environment.

## Invariants

- Production stays on `main` between releases.
- Every wave uses a fresh branch and PR directly to `main`.
- A maximum of four phases may run in parallel when they own disjoint paths.
- Local tests remain targeted: at most 20 tests per command, three commands per
  cycle, and two Playwright specs per invocation.
- Fake data, E2E, migrations, and restore tests must refuse the production
  database unless the command is an explicitly authorized deployment step.
- Public API shapes, function-based DRF views, the single Axios client,
  WooCommerce mirroring, offline translation, locale/currency behavior,
  wishlists, PayPal, and Wompi remain business invariants.
- Runtime-changing waves require a fresh database/media snapshot, a verified
  restore, a rollback point, and post-deploy health checks.

## Baseline

At the start of the program, `main` had partial AI guidance, no partitioned CI,
almost no behavior tests, tracked generated artifacts, vulnerable dependencies,
and operational documentation that disagreed with the deployed services. An
earlier session prepared useful changes in
`chore/20082026-crushme-modernization`, but also created an unintended staging
coordinate. That branch is evidence and a source for reviewed changes only; it
will not be merged wholesale.

## Wave Plan

| Wave | Purpose | Release gate |
|---|---|---|
| 0 | Free disk, retire the accidental staging coordinate, establish this roadmap and a safe worktree | Production remains healthy; disk usage below 80%; registry and worktree checks green |
| 1 | Synchronize Codex, Claude Code, Windsurf, skills, standards, and Memory Bank | Project-specific AI drift is zero and guidance matches the real runtime |
| 2 | Remove verified repository waste and add hermetic test/CI/development foundations | Six partitioned CI jobs pass; no production behavior or data changes |
| 3 | Update dependencies and harden authentication, uploads, payments, secrets, headers, and runtime boundaries | No unmitigated critical/high finding; restore rehearsal and controlled production deploy pass |
| 4 | Close backend, frontend-unit, and E2E behavior gaps and audit test quality | No junk-only or unvalidated critical flow; quality gate and CI pass |
| 5 | Align production operations, backups, observability, restore, and performance with the fleet standard | Post-deploy, restore, timers, logs, and representative load show at least 30% headroom |
| 6 | Run final read-only certification and promote lifecycle | QA, vulnerability, AI sync, full audit, and 24-hour production observation are green |

## Wave Delivery

Each wave starts from the latest `main` as `chore/crushme-wave-<n>-<topic>`. The
old modernization commits are cherry-picked or reapplied only after their diff
is reviewed against the wave's scope. Every PR is squash-merged after its own
gate; production then returns to a clean `main` before the next wave starts.

Documentation/AI/test-only waves do not restart services. Runtime waves use a
maintenance window and preserve the previous commit, environment, venv,
staticfiles, database snapshot, and media snapshot until observation closes.

## Promotion Definition Of Done

- No accidental CrushMe staging registry, DNS, database, socket, or service
  exists.
- AI ecosystems and project methodology match the canonical fleet baseline.
- CI and QA cover real behavior without conditional or mock-only evidence.
- No critical/high vulnerability remains without a tested mitigation.
- The exposed historical database credential is revoked and protected stores
  contain only its replacement.
- Production backup restoration and rollback are rehearsed.
- Production stays healthy for at least 24 hours after the final runtime wave.
- The fleet lifecycle is changed from `modernizing` to `active` only after all
  prior conditions pass.
